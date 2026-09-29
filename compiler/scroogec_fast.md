# scroogec_fast / scroogec_fast_x86-64 Compiler Technical Specification

`scroogec_fast` (and its statically-linked build `scroogec_fast_x86-64`) is a high-performance, single-tool native compiler, static shape-gate verifier, and metrics analyzer for the Scrooge programming language (`.sg`).

---

## 1. Compiler Architecture & CLI Usage

Compiled from `scroogec_fast.nim` (in the development repository), `scroogec_fast` operates as a 100% self-contained unified tool that performs tokenization, AST construction, static verification (Track 1 arity analysis & Track 2 type checking), and C code generation without requiring external Python scripts.

### CLI Syntax
```bash
compiler/scroogec_fast [-L <libDir>] [--stage2] [--metrics] [--check-only] [--debug-stack] [--profile] [-O0|-O1|-O2|-O3] [--no-ptr-check] [--dump-c [path]] [--dump-bytecode [path]] [-o <outBinary>] <file.sg>
```

### Options & Flags
- `<file.sg>` *(Required)*: Path to the Scrooge source file to check, verify, or compile.
- `-L <dir>`, `--lib <dir>`, `--library-dir <dir>`: Specifies a custom directory path for resolving standard library lexicons (e.g., `strings.sg`, `util.sg`, `manifest.sm`).
- `-o <outBinary>`, `--output <outBinary>`: Specifies the output native executable binary name (default: `<basename>` derived from `<file.sg>`).
- `--dump-c [path]`: Performs static verification, generates intermediate C source code to `path` (or `<basename>.c`), and exits.
- `--dump-bytecode [path]`: Performs static verification, generates intermediate binary bytecode (`.scc`) to `path` (or `<basename>.scc`), and exits.
- `--check-only`: Performs static analysis and outputs `ACCEPT` or `REJECT` without emitting a native binary executable.
- Exit status: 0 on ACCEPT (and a successful build), 1 on REJECT or a failed build. A build first removes any existing file at the output path, so a rejected build never leaves an older binary behind.
- `--debug-stack`: Ends the generated `main` with `print_stack()`, so the program prints whatever it left on the stack as `STACK: [...]` after its own output. Off by default (every program used to print a trailing `STACK: []`).
- `--profile`: Builds a program that counts every word's calls and times its activations, and prints a table to stderr when it exits (also on `abort`): calls, self time (excluding callees), share of wall time, total time (including callees; a recursive word's inner activations are not counted twice), sorted by self time. A tail-recursive loop is one activation. Activations are timed with the CPU cycle counter (about 10 ns each, included in self time, so a word called hundreds of millions of times looks slower than it is). Without the flag the generated C contains no profiling code.
- `-O0` / `-O1` / `-O2` / `-O3`: the optimisation level passed to gcc (default `-O3`). Behaviour is identical at every level; `-O0` builds a large program about ten times faster, for the edit-build-test loop.
- `--no-ptr-check`: leave out the check that a Ptr's allocation has not been released by `hrelease` and reused (one comparison per `hread`/`hwrite`; about 7% in a program made almost only of heap reads). For benchmark builds of a program already tested with the check on; a Ptr to a released slot that has not been reused is still caught.
- Source editing, a whole word at a time (no compile): `--words FILE`, `--show NAME FILE`, `--replace NAME FILE`, `--insert-before NAME FILE`, `--insert-after NAME FILE` (new definitions on stdin, checked before anything is written), `--delete NAME FILE`, `--fmt [--check] FILE` (re-indent only). See the skill guide, section 8b.
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

The file primitives (`fopen`, `fclose`, `fgetc`, `fputc`, `fread`, `fwrite`, `freadline`, `fread_into`, `fseek`, `ftell`; spec §12) are backed by a fixed `FILE*` table in `EMBEDDED_RUNTIME_C`:

- `MAX_FILES` is 64. Slots 0/1/2 are pre-opened by `init_files()` (called from `init_runtime()`) as `stdin`/`stdout`/`stderr`, leaving 61 slots that `fopen` allocates from by first-free scan. Exhaustion is reported through `fopen`'s `ok` flag, never by growing the table or writing past it.
- A `File` value is that slot index. There is no `VAL_FILE` runtime type: `File` is a static type tag, exactly as `Map` and `Record` are, so `f_stdin`-style one-word type assertions in `library/file.sg` work the same way the spec's `hread` wrapper idiom does. Runtime safety comes from `file_slot()`, which validates the index is in range and the slot is open before every read or write.
- `FILE_PATH_MAX` is 4096. `op_fopen` converts the path Block into a C string, validating every slot is an integer, and releases the Block's reference (`block_decref`) since the value came off the stack.
- `op_fread` buffers into `unsigned char[want]` and only converts what was actually read into `ScroogeValue` slots, so an oversized count costs one byte per requested character up front rather than sixteen.
- Every non-leaf word calls `word_enter(id)` on entry (MAX_FRAMES check, and one store of its id into `word_stack[call_depth]`) and `call_depth--` on exit. After a `Fatal:` message, `err_printf` prints that chain via `scrooge_backtrace`, from the `word_names`/`word_places` tables emitted with every program. A leaf word (it calls no other word, so it cannot recurse) skips both: measured with callgrind, the store alone cost 4% of instructions on a call-heavy solver, and skipping leaves made two sudoku solvers 7-9% cheaper than before the chain existed.
- User modules (G28): before checking, `resolveProgram` loads every `use "name"` that is not a library lexicon as the file name.sg beside the using file (transitively, once each), prepends the modules to the program's text, and records where each starts; `mapLines` rewrites every reported "line N" (errors, warnings) to the module file and line, and `sourcePlace` does the same for the runtime word chain and `trace`.
- Memory (G24, G29): the heap allocation table grows by doubling (no fixed allocation count). A Block owns a reference to each Block element: `block_free` releases them (skipping the scan when `holds_blocks` is 0, which `cons`, `pair`, `block_slice`, `block_set` and the file readers keep exact), and the copying paths (`block_slice`, `cons`/`block_set` on a shared Block) count each copied element. Freed Block headers are reused from a free list.
- Output to stdout is buffered. `print_char`/`print_int`/`print_float` and `op_fputc`/`op_fwrite` on slot 1 share `stdout`'s buffer, so they stay in order. Every runtime message to stderr goes through `err_printf`, which flushes stdout first; `op_fputc`/`op_fwrite` on slot 2 and reads from slot 0 flush it too, and `exit` flushes it at the end.

## 2c. Command-Line Argument Runtime

The `argc`/`argv` primitives (spec §13) are backed by two file-scope globals in `EMBEDDED_RUNTIME_C`, set once from `main`:

```c
static int scrooge_argc = 0;
static char** scrooge_argv = NULL;
static inline void init_args(int argc, char** argv) { ... }
```

- **The generated `main` signature changed** from `int main()` to `int main(int argc, char** argv)`, and now calls `init_args(argc, argv)` immediately after `init_runtime()`. Anything that parses or diffs `--dump-c` output across compiler versions will see that line move.
- **Nothing is materialized up front.** `op_argv` converts one argument to a Block on demand, so a program that never asks pays nothing and one that asks for argument 3 allocates that one string. `library/args.sg`'s `arg_tail` is the only thing that deliberately builds all of them.
- **The indexing is C's, unchanged**: `argv[0]` is the program as invoked, the first real argument is index 1, and `argc` counts both. Re-basing it in the runtime would make the language disagree with the `argc`/`argv` every reader already knows, invisibly at the call site.
- Out-of-range (either direction) reports `ok=0` with an empty Block rather than aborting — it is the ordinary way to ask whether an argument was supplied. A *present but empty* argument returns an empty Block with `ok=1`; present-and-empty is deliberately distinguishable from absent. Only a non-integer index is fatal, matching `hread`/`fread`.
- Arguments are read-only, and the environment is read-only (`getenv`).

---

### Adding a primitive

A new primitive must be added in **seven** places. `--selftest` now mechanically catches an omission in five of them (2-5); the remaining two are caught by `tools/spec_sync_check` (development repository) and by nothing respectively.

1. `RESERVED` -- so it cannot be used as a parameter name or frame alias. **Not automatically checked.**
2. `PRIM_EFFECT` (module level) -- arity for the Track 1 checker. This table is what `--selftest` treats as the definition of the primitive surface; everything else is held against it.
3. `ALL_EMITTER_PRIM_WORDS` -- the hand-maintained mirror of the emitters' `case` arms.
4. `emitNode` and `emitBCNode` -- one case arm each. A spelling in `PRIM_EFFECT` without both is the ACCEPT-then-fails-to-build class `--selftest` was created to eliminate.
5. `PRIM_TYPES` (module level) -- Track 2 operand and result types. A word with no entry here *and* no early-return branch in `wordTC` falls through to that proc's trailing `tstack.add("Unknown")`, which pushes a result without popping the operands: the type stack desyncs by the input count and every later call site in the same word is checked against shifted operands. That was Bug 18, and `--selftest` now rejects it.
6. `analyzeStack`'s local `PRIM_EFFECT` copy -- `--metrics` stack-depth accounting. **Not automatically checked.**
7. Spec §7 -- `tools/spec_sync_check` (development repository) requires every backticked token there to be a `PRIM_EFFECT` key.

### What `--selftest` guarantees about the primitive surface

Six assertions, all bidirectional, all against `PRIM_EFFECT` as the definition:

- Every `PRIM_EFFECT` key compiles without raising through **both** emitters (a synthesized minimal program per key).
- Every entry in `ALL_EMITTER_PRIM_WORDS` has a `PRIM_EFFECT` entry, and vice versa.
- Every `PRIM_EFFECT` key is type-checked *somewhere*: either it has a `PRIM_TYPES` entry, or it appears in `WORDTC_EARLY_BRANCH_WORDS`.
- Every `PRIM_TYPES` key has a `PRIM_EFFECT` entry, so the type table cannot describe a primitive that does not exist.
- Every `WORDTC_EARLY_BRANCH_WORDS` entry has a `PRIM_EFFECT` entry.
- No word appears in **both** `PRIM_TYPES` and `WORDTC_EARLY_BRANCH_WORDS`. The early return wins, so a word in both has a dead type entry whose operand checks never run -- which is exactly how `to_float` came to accept a `Block` (Bug 19).

`WORDTC_EARLY_BRANCH_WORDS` is the Track 2 counterpart of `ALL_EMITTER_PRIM_WORDS` and exists for the same reason: Nim cannot introspect the `if` branches at the top of `wordTC`, so the list stands in for them and must be kept in lockstep. The pass line reports the split, e.g. `58 primitives ... (40 typed + 18 early-branch)` -- those two numbers summing to the primitive count is the invariant.

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
- **`#record` Expansion**: the last step of `tokenize` (`expandRecords`) replaces each `#record Name ... end` declaration with the tokens of ordinary word definitions (`Name_size`, `Name_new`, and a getter and setter per field, spec Sec.5), each carrying its field's line number. The parser, checker and code generator never see a record. Malformed declarations are collected while tokenizing and reported by the checker as `ParseError`s.
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
   REJECT DuplicateWordError line 5: '#reverse' collides with 'reverse' from lexicon "util"; rename it, or drop the local definition and use the lexicon's
   ```

6. **Reserved Word Violation**:
   ```text
   REJECT ReservedWordIdentifierError line 3: 'len' used as a parameter name in signature of #my_func
   ```
