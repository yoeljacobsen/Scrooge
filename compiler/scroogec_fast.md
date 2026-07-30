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

## 3. AST & Scope Mechanics

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
