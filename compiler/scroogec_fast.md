# scroogec_fast / scroogec_fast_x86-64 Compiler Technical Specification

`scroogec_fast` (and its statically-linked build `scroogec_fast_x86-64`) is a high-performance, single-tool native compiler, static shape-gate verifier, and metrics analyzer for the Scrooge programming language (`.sg`).

---

## 1. Compiler Architecture & CLI Usage

Compiled from `scroogec_fast.nim`, `scroogec_fast` operates as a 100% self-contained unified tool that performs tokenization, AST construction, static verification (Track 1 arity analysis & Track 2 type checking), and C code generation without requiring external Python scripts.

### CLI Syntax
```bash
./scroogec_fast [-L <libDir>] [--stage2] [--metrics] [--check-only] [--dump-c [path]] [--dump-bytecode [path]] [-o <outBinary>] <file.sg>
```

### Options & Flags
- `<file.sg>` *(Required)*: Path to the Scrooge source file to check, verify, or compile.
- `-L <dir>`, `--lib <dir>`, `--library-dir <dir>`: Specifies a custom directory path for resolving standard library lexicons (e.g., `strings.sg`, `util.sg`, `manifest.sm`).
- `-o <outBinary>`, `--output <outBinary>`: Specifies the output native executable binary name (default: `<basename>` derived from `<file.sg>`).
- `--dump-c [path]`: Performs static verification, generates intermediate C source code to `path` (or `<basename>.c`), and exits.
- `--dump-bytecode [path]`: Performs static verification, generates intermediate binary bytecode (`.scc`) to `path` (or `<basename>.scc`), and exits.
- `--check-only`: Performs static analysis and outputs `ACCEPT` or `REJECT` without emitting a native binary executable.
- `--stage2`: Enables Stage 2 verification rules (enabled by default).
- `--metrics`: Calculates transitive static stack metrics and branch count for the entry point macro and outputs a JSON summary.

### Executable & Path Resolution Fallback
`scroogec_fast` automatically resolves standard library modules (`use "strings"`, `use "util"`, etc.) and `manifest.sm` using multi-path fallback:
1. Directory specified via `-L / --lib / --library-dir` flag.
2. Executable parent directory fallback: `getAppDir() / ".." / "library"`.
3. Executable adjacent fallback: `getAppDir() / "library"`.
4. Working directory fallback: `./library/` or `./manifest.sm`.

This path resolution enables `scroogec_fast` to be executed globally from any working directory while maintaining access to standard library lexicons.

---

## 2. C Code Generation Optimizations

### Compact C Array Generation Pipeline
`scroogec_fast` incorporates an optimized C code generation pipeline for pure integer data blocks (`make_int_array` in `EMBEDDED_RUNTIME_C`).

#### Implementation
Instead of emitting individual allocation loops with multiple C statements per element, pure integer literal blocks emit compact C literal arrays:

```c
static inline ScroogeValue make_int_array(const long long* data, int len) {
    ScroogeValue* elems = (ScroogeValue*)malloc(len * sizeof(ScroogeValue));
    for (int i = 0; i < len; i++) {
        elems[i].type = VAL_INT;
        elems[i].int_val = data[i];
    }
    return make_block(elems, len);
}
```

Generated C code for a data block like `"Hello"`:
```c
push(make_int_array((const long long[]){72LL, 101LL, 108LL, 108LL, 111LL}, 5));
```

#### Performance Impact
- **C Code Line Count Reduction**: Reduces intermediate C file size by over 80%.
- **GCC Compilation Speedup**: Achieves up to ~23x compile-time speedup when compiling large Scrooge programs or data-heavy benchmarks with `gcc`.

---

## 2b. File I/O Runtime

The six file primitives (`fopen`, `fclose`, `fgetc`, `fputc`, `fread`, `fwrite`; spec §12) are backed by a fixed `FILE*` table in `EMBEDDED_RUNTIME_C`:

- `MAX_FILES` is 64. Slots 0/1/2 are pre-opened by `init_files()` (called from `init_runtime()`) as `stdin`/`stdout`/`stderr`, leaving 61 slots that `fopen` allocates from by first-free scan. Exhaustion is reported through `fopen`'s `ok` flag, never by growing the table or writing past it.
- A `File` value is that slot index. There is no `VAL_FILE` runtime type: `File` is a static type tag, exactly as `Map` and `Record` are, so `f_stdin`-style one-word type assertions in `library/file.sg` work the same way the spec's `hread` wrapper idiom does. Runtime safety comes from `file_slot()`, which validates the index is in range and the slot is open before every read or write.
- `FILE_PATH_MAX` is 4096. `op_fopen` converts the path Block into a C string, validating every slot is an integer, and releases the Block's reference (`block_decref`) since the value came off the stack.
- `op_fread` buffers into `unsigned char[want]` and only converts what was actually read into `ScroogeValue` slots, so an oversized count costs one byte per requested character up front rather than sixteen.
- `op_fputc`/`op_fwrite` flush when the target is slot 1 or 2, matching `print_char`, so `print_char` and file-word output to a standard stream interleave in source order. A real file stays buffered until `fclose` or normal process exit.

### Adding a primitive

A new primitive must be added in **seven** places or it breaks in one of two silent ways. `--selftest` catches the first four; nothing catches the fifth automatically.

1. `RESERVED` -- so it cannot be used as a parameter name or frame alias.
2. `PRIM_EFFECT` (module level) -- arity for the Track 1 checker.
3. `ALL_EMITTER_PRIM_WORDS` -- the hand-maintained mirror `--selftest` checks against.
4. `emitNode` and `emitBCNode` -- one case arm each; a spelling in `PRIM_EFFECT` without both is the ACCEPT-then-fails-to-build class `--selftest` exists to eliminate.
5. `PRIM_TYPES` (inside `wordTC`) -- Track 2 types. **A missing entry here does not error.** The word falls through to the trailing `tstack.add("Unknown")`, which pushes a result without popping the operands, desyncing the type stack by the input count and mis-typing every call site after it in the same word. This is Bug 18 in `SCROOGEC_FAST_BUG_HISTORY.md`.
6. `analyzeStack`'s local `PRIM_EFFECT` copy -- `--metrics` stack-depth accounting.
7. Spec §7 -- `tools/spec_sync_check` requires every backticked token there to be a `PRIM_EFFECT` key.

---

## 3. AST & Scope Mechanics

### Tail-Call Rewriting and Frame Unwinding

A word whose entry frame binds exactly its declared inputs and whose body ends in a direct self-call is rewritten into a `goto word_loop_start` loop rather than a C call (`terminalSelfCalls`). The rewrite must **unwind** every frame entered since the loop head through `leave_frame()`:

```c
while (frames_cnt > tco_frames_cnt) { leave_frame(); }
```

Rewinding `frames_cnt`/`current_frame_idx`/`frame_storage_top` directly -- as the codegen originally did -- abandons every Block reference stored in an inner frame's slots without decref'ing it. Since the ordinary multi-step idiom (`-> [ a b ] [ ... ] -> [ a b c ] ...`) parses into a *nested* frame, that leaked one accumulator reference per iteration, so any such loop's accumulator was never freed: quadratic memory. See Bug 17.

### Frame Scoping Rules
An arrow frame `-> [ vars ] [ body ]` binds variables popped from the stack for the duration of its body block:
- **Nested Scopes**: Variable bindings persist across trailing multi-block expressions and nested child scopes within the frame body.
- **Sibling Inheritance**: Consecutive sibling frames within a macro inherit earlier unshadowed aliases.
- **Trailing Conditionals**: Trailing `cond` expressions inherit active frame variable aliases.

### AST Node Line-Number Tracking
`scroogec_fast` attaches precise line-number tracking (`lineNum: int`) during tokenization:
- **`Token` Structure**: Every token emitted by `tokenize` records its originating source line number (`Token(val: string, lineNum: int)`). Multi-line comments `{ ... }` and string literal expansions `"..."` track line increments accurately.
- **AST Propagation**: AST construction (`parseNodes`, `extractMacros`) attaches `lineNum` directly to `Node` ref objects (`Node.lineNum`) and `Macro` ref objects (`Macro.lineNum`).

---

## 4. Diagnostic Formatting Specifications

All static verification errors follow a standardized diagnostic format designed for clarity and actionable debugging.

### Diagnostic Format
```text
REJECT <ErrorClass> line X <details>
```

### Standard Error Classes & Examples

1. **Arity Net Effect Delta**:
   ```text
   REJECT ArityMismatch line 42 #word: body net effect +2 != signature effect +1
   ```

2. **Arity Drift Guard**:
   ```text
   REJECT ArityMismatch line 12 #bad_map: entry frame binds 1 vars but signature declares 2 inputs
   ```

3. **Call-Site Parameter Type Mismatch**:
   ```text
   REJECT TypeError line 5 #caller_bug_8: parameter 'row' expects Block but got Ptr
   ```

4. **Invalid Index Operation**:
   ```text
   REJECT TypeError line 18 #word: 'at' index into Ptr (should be hread)
   ```

5. **Lexicon Shadowing Collision**:
   ```text
   REJECT DuplicateWordError line 5: '#word_name' collides with an imported lexicon definition
   ```

6. **Reserved Word Violation**:
   ```text
   REJECT ReservedWordIdentifierError line 3: 'len' used as a parameter name in signature of #my_func
   ```
