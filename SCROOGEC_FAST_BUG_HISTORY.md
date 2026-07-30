# scroogec_fast Bug History & Resolution Log

This document records all compiler, parser, AST transformer, and C code generator bugs discovered, analyzed, and resolved during the development of `scroogec_fast` and `scroogec_fast_x86-64`.

---

## Bug 1: Intermediate C Code Line Bloat & Compilation Time Reduction

- **Symptom**: Large programs containing many string literals (such as SQL test suites like `impl_scrooge_select1.sg`) generated an 8.0 MB C file (`select1.c`) containing **311,614 lines** of C code, causing `gcc -O2` compilation to take 30+ seconds.
- **Root Cause**: Every string literal in Scrooge (`"CREATE TABLE..."`) expanded into 120 lines of imperative `malloc`, `push(make_int(...))`, and `b[i] = pop()` instructions inside a single C function (`m_suite_statements()`).
- **Fix**: Added `make_int_array` in `EMBEDDED_RUNTIME_C` and added `isPureIntBlock` compact C array generation in `scroogec_fast.nim`. Reduced generated C line count from **311,614 lines down to 5,364 lines** (98.3% reduction) and reduced GCC compile time from **30+ seconds down to 1.35 seconds** (~23x speedup).

---

## Bug 2: String Literal Leak in `use` Import Directives

- **Symptom**: `use "strings"` (`use [ 115 116 114 ... ]`) left the ASCII character array sitting on top of the stack upon program completion (`STACK: [[115, 116, ...]]`).
- **Root Cause**: Pre-processor string expansion converted `use "strings"` into `use [ 115 116 114 105 110 103 115 ]`. `parseNodes` in `scroogec_fast.nim` previously skipped only the single next token after `use`, causing the string block `[ 115 116 ... ]` to leak into top-level executable AST nodes.
- **Fix**: Updated `parseNodes` to skip the entire block argument following `use` directives during AST construction.

---

## Bug 3: Executable-Relative Library File Resolution

- **Symptom**: Executing `./Scrooge/compiler/scroogec_fast_x86-64` from external working directories failed to resolve imported library modules if `./library/` was not present in the current working directory.
- **Root Cause**: `findLibraryFile` checked relative paths against `getCwd()`, but did not check relative to `getAppDir()` (the installation path of the `scroogec_fast_x86-64` compiler binary itself).
- **Fix**: Added executable installation path (`getAppDir() / ".." / "library"`) resolution to `findLibraryFile`.

---

## Bug 4: Operand Pop Order Swap in `nkFold` C Code Generation

- **Symptom**: `nkFold` (`[fold| idx acc val ctx | body from init ]`) threw a runtime `Fatal: Stack underflow` during execution despite passing static verification (`ACCEPT`).
- **Root Cause**: In `nkFold`, `foldInit` pushes `init` on top of `arr` and `ctx`. The C code generator was popping `arr_val = pop()` **before** `foldInit` was evaluated, popping `init` into `arr_val` and attempting to access `0.block.len`.
- **Fix**: Reordered `nkFold` pop sequence in C generation to pop `acc_val` (`init`) first, then `arr_val`, then `ctx_val`.

---

## Bug 5: Premature Frame Scope Closure on `-> [ vars ]` in Macro Bodies

- **Symptom**: Macros with trailing expressions after the first body block (such as `#find_char_step` ending with `cond [ idx ] else [ acc ] ?`) closed the frame scope (`leave_frame()`) prematurely, causing local variable lookups (`idx`, `acc`) to fail silently and emit empty `if/else` statements (`if (cond) {} else {}`).
- **Root Cause**: `parseNodes` closed the frame scope (`leave_frame()`) immediately after the first `[ body ]` block instead of scoping `-> [ vars ]` over all remaining body expressions in the macro.
- **Fix**: Updated `parseNodes` to scope `-> [ vars ]` across all remaining expressions in the macro body until `end` or block closing.

---

## Bug 6: Token Index Offset Mismatch After `use` Directive Block Parsing

- **Symptom**: In `ggg.sg` (`use "strings"` followed by `test_string_conformance`), `parseNodes` set `i = idx` (index of `]`) instead of `endIdx` (after `]`), causing `if t == "]": break` to terminate parsing top-level nodes before reaching `test_string_conformance`, leaving `main()` empty.
- **Root Cause**: Index assignment in `parseNodes` used `i = idx` instead of `i = endIdx`.
- **Fix**: Corrected index assignment in `parseNodes` to `i = endIdx`.

---

## Bug 7: Missing C Code Generator Handlers for `abs`, `min`, and `max` Primitives

- **Symptom**: Source code using `abs`, `min`, or `max` primitives threw `Compilation error: Unknown word / primitive: min` during C code generation.
- **Root Cause**: While `abs`, `min`, and `max` were recognized by static verification, their runtime C implementations and `emitNode` handlers were missing.
- **Fix**: Added `op_abs`, `op_min`, and `op_max` C runtime implementations to `EMBEDDED_RUNTIME_C` and added primitive cases in `emitNode`.

---

## Bug 8: Parameter Signature Order Mismatch in `db_table_insert`

- **Symptom**: Calling `db_table_insert` passed `row` then `tbl`, but signature was declared `( tbl:Ptr row:Block -- )`, causing heap pointers and blocks to swap at runtime.
- **Root Cause**: Signature declared parameters in opposite order from argument pushing order on stack.
- **Fix**: Corrected signature to `#db_table_insert ( row:Block tbl:Ptr -- )` in `impl_scrooge_select1.sg`.
