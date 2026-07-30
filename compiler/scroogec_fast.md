# scroogec_fast / scroogec_fast_x86-64

`scroogec_fast` (and its statically-linked build `scroogec_fast_x86-64`) is a high-performance, single-tool native compiler, static shape-gate verifier, and metrics analyzer for the Scrooge programming language (`.sg`).

## Overview

Compiled from `scroogec_fast.nim`, `scroogec_fast` operates as a **100% self-contained, zero-dependency unified tool** that:
- Performs static verification, shape-gate validation, arity checking, stack effect analysis, and type checking.
- Directly compiles Scrooge source code (`.sg`) into standalone native ELF 64-bit x86-64 executables without requiring external Python tools or runtime script files.
- Dumps intermediate target representation files (C source code and binary bytecode) via dedicated CLI flags.
- Bundles the full Scrooge C runtime environment and automatically compiles native binaries via `gcc`.
- Resolves imported standard library modules (`use "strings"`, `use "util"`, etc.) automatically.

## Usage

```bash
scroogec_fast [-L <libDir>] [--stage2] [--metrics] [--check-only] [--dump-c [path]] [--dump-bytecode [path]] [-o <outBinary>] <file.sg>
```

### Options & Flags

- `<file.sg>` *(Required)*: Path to the Scrooge source file to check, verify, or compile.
- `-L <dir>`, `--lib <dir>`, `--library-dir <dir>`: Specifies a custom directory path for resolving standard library lexicons (e.g., `strings.sg`, `util.sg`, `manifest.sm`).
- `-o <outBinary>`, `--output <outBinary>`: Specifies the output native executable binary name (default: `<basename>` derived from `<file.sg>`).
- `--dump-c [path]`, `--dump-c:[path]`: Performs static verification, generates and dumps intermediate C source code to `path` (or `<basename>.c`), and exits immediately.
- `--dump-bytecode [path]`, `--dump-bytecode:[path]`, `--dump-scc [path]`: Performs static verification, generates and dumps intermediate binary bytecode (`.scc`) to `path` (or `<basename>.scc`), and exits immediately.
- `--check-only`: Only performs static analysis and outputs `ACCEPT` or `REJECT` without emitting a native binary executable.
- `--stage2`: Enables Stage 2 verification rules (enabled by default).
- `--metrics`: Calculates transitive static stack metrics and branch count for the entry point macro and outputs a JSON summary.

## Modes of Operation

### 1. Direct Native Binary Compilation (Default)

Performs static verification. If the code passes verification (`ACCEPT`), `scroogec_fast` automatically compiles the program and all imported library modules into a native ELF executable:

```bash
# Compiles app.sg to native executable ./app
./scroogec_fast app.sg

# Execute native binary directly
./app
```

To specify a custom output binary name:
```bash
./scroogec_fast app.sg -o my_app
```

To specify a custom library search directory:
```bash
./scroogec_fast -L /path/to/library app.sg -o my_app
```

### 2. Intermediate File Dumping (`--dump-c` & `--dump-bytecode`)

Performs static verification (`ACCEPT`), dumps the requested intermediate representation file, and exits without generating an executable:

- **Dump C Source Code:**
  ```bash
  ./scroogec_fast --dump-c out.c app.sg
  ```
- **Dump Binary Bytecode (.scc):**
  ```bash
  ./scroogec_fast --dump-bytecode out.scc app.sg
  ```

### 3. Static Verification Mode (`--check-only`)

Performs static verification only without compiling a binary executable or dumping intermediate files:

- **Success Output:**
  ```text
  ACCEPT
  ```
- **Failure Output:**
  ```text
  REJECT <ErrorClass> <WordName>
  ```
  *(Example: `REJECT TypeError at`)*

### 4. Metrics Mode (`--metrics`)

Calculates static execution metrics for the entry word in the target file and outputs formatted JSON:

```json
{
  "transient_stack_depth": 4,
  "static_branch_count": 2
}
```

## Key Characteristics

- **100% Self-Contained**: Operates without external Python scripts (`scroogec.py`, `scrooge2c.py`).
- **Statically Linked**: `scroogec_fast_x86-64` has zero external runtime library dependencies.
- **Intermediate Inspection**: Built-in support for inspecting intermediate C and bytecode output.
- **Library Module Resolution**: Automatically resolves imported library modules from specified or standard library locations (`library/`, `../Scrooge/library/`).

## Bug Fixes & Resolved Issues Log

The following key compiler, C code generator, and parser bugs were identified, debugged, and resolved during this session:

### 1. Intermediate C Code Line Bloat & Compilation Time Reduction
- **Issue**: Large programs containing many string literals (such as SQL test suites) generated 300,000+ lines of imperative `malloc`/`push`/`pop` C instructions in a single function body, causing `gcc -O2` compilation to take 30+ seconds.
- **Fix**: Added `make_int_array` in `EMBEDDED_RUNTIME_C` and compact `isPureIntBlock` static array formatting. Reduced generated C line count from **311,614 lines down to 5,364 lines** (98.3% reduction) and reduced GCC compile time from **30+ seconds down to 1.35 seconds**.

### 2. String Literal Leak in `use` Import Statements
- **Issue**: `use "strings"` directives left the ASCII string block `[ 115 116 114 ... ]` sitting on top of the stack upon program completion.
- **Fix**: Updated `parseNodes` to skip the entire block argument following `use` directives during AST construction.

### 3. Executable-Relative Library File Resolution
- **Issue**: Executing the compiler binary from arbitrary working directories (e.g. `./Scrooge/compiler/scroogec_fast_x86-64`) failed to resolve library modules if `./library/` was not present in current working directory.
- **Fix**: Added executable installation path (`getAppDir() / ".." / "library"`) resolution to `findLibraryFile`.

### 4. Correct Operand Pop Sequence for `nkFold` Constructs
- **Issue**: `nkFold` (`[fold| idx acc val ctx | body from init ]`) threw a runtime `Fatal: Stack underflow` during execution despite passing static verification (`ACCEPT`).
- **Fix**: Reordered `nkFold` pop sequence in C generation to pop `acc_val` (`init`) first, then `arr_val`, then `ctx_val`.

### 5. `-> [ vars ]` Frame Scope Extension in Macro Bodies
- **Issue**: Macros with trailing expressions after the first body block (such as `#find_char_step` ending with `cond [ idx ] else [ acc ] ?`) closed the frame scope (`leave_frame()`) prematurely, causing variable references (`idx`, `acc`) to fail silently and emit empty `if/else` statements.
- **Fix**: Updated `parseNodes` to scope `-> [ vars ]` across all remaining expressions in the macro body until `end` or block closing.

### 6. Token Index Mismatch After `use` Block Parsing
- **Issue**: In `use [ ... ]` directive block skipping, `parseNodes` assigned `i = idx` (index of `]`) instead of `i = endIdx` (after `]`), causing `if t == "]": break` to terminate parsing top-level nodes before reaching main entry macro.
- **Fix**: Updated `parseNodes` index assignment to `i = endIdx`.

### 7. Missing C Code Generator Handlers for `abs`, `min`, and `max` Primitives
- **Issue**: Source code using `abs`, `min`, or `max` primitives threw `Compilation error: Unknown word / primitive: min` during C code generation.
- **Fix**: Added `op_abs`, `op_min`, and `op_max` C runtime implementations to `EMBEDDED_RUNTIME_C` and added primitive cases in `emitNode`.

### 8. Parameter Signature Order Mismatch in `db_table_insert`
- **Issue**: `impl_scrooge_select1.sg` caller passed `row` then `tbl`, but `#db_table_insert` signature was defined as `( tbl:Ptr row:Block -- )`, causing heap pointers and blocks to swap at runtime.
- **Fix**: Corrected signature to `#db_table_insert ( row:Block tbl:Ptr -- )` in `impl_scrooge_select1.sg`.
