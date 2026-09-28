# scroogec_fast / scroogec_fast_x86-64

`scroogec_fast` (and its statically-linked build `scroogec_fast_x86-64`) is a high-performance, single-tool native compiler, static shape-gate verifier, and metrics analyzer for the Scrooge programming language (`.sg`).

## Overview

Compiled from `scroogec_fast.nim` (in the development repository), `scroogec_fast` operates as a **100% self-contained, zero-dependency unified tool** that:
- Performs static verification, shape-gate validation, arity checking, stack effect analysis, and type checking.
- Directly compiles Scrooge source code (`.sg`) into standalone native ELF 64-bit x86-64 executables without requiring external Python tools or runtime script files.
- Dumps intermediate target representation files (C source code and binary bytecode) via dedicated CLI flags.
- Bundles the full Scrooge C runtime environment and automatically compiles native binaries via `gcc`.
- Resolves imported standard library modules (`use "strings"`, `use "util"`, etc.) automatically.

## Usage

```bash
scroogec_fast [-L <libDir>] [--stage2] [--metrics] [--check-only] [--debug-stack] [--profile] [-O0|-O1|-O2|-O3] [--dump-c [path]] [--dump-bytecode [path]] [-o <outBinary>] <file.sg>
```

### Options & Flags

- `<file.sg>` *(Required)*: Path to the Scrooge source file to check, verify, or compile.
- `-L <dir>`, `--lib <dir>`, `--library-dir <dir>`: Specifies a custom directory path for resolving standard library lexicons (e.g., `strings.sg`, `util.sg`, `manifest.sm`).
- `-o <outBinary>`, `--output <outBinary>`: Specifies the output native executable binary name (default: `<basename>` derived from `<file.sg>`).
- `--dump-c [path]`, `--dump-c:[path]`: Performs static verification, generates and dumps intermediate C source code to `path` (or `<basename>.c`), and exits immediately.
- `--dump-bytecode [path]`, `--dump-bytecode:[path]`, `--dump-scc [path]`: Performs static verification, generates and dumps intermediate binary bytecode (`.scc`) to `path` (or `<basename>.scc`), and exits immediately.
- `--check-only`: Only performs static analysis and outputs `ACCEPT` or `REJECT` without emitting a native binary executable.
- `--debug-stack`: Ends the generated `main` with `print_stack()`, so the program prints whatever it left on the stack as `STACK: [...]` after its own output. Off by default.
- `--profile`: Builds a program that prints each word's calls, self time and total time to stderr at exit (see `compiler/scroogec_fast.md`).
- `-O0` / `-O1` / `-O2` / `-O3`: the optimisation level passed to gcc (default `-O3`). Behaviour is identical at every level; `-O0` builds a large program about ten times faster, for the edit-build-test loop.
- `--stage2`: Enables Stage 2 verification rules (enabled by default).
- `--metrics`: Calculates transitive static stack metrics and branch count for the entry point macro and outputs a JSON summary.

## Modes of Operation

### 1. Direct Native Binary Compilation (Default)

Performs static verification. If the code passes verification (`ACCEPT`), `scroogec_fast` automatically compiles the program and all imported library modules into a native ELF executable:

```bash
# Compiles app.sg to native executable ./app
compiler/scroogec_fast app.sg

# Execute native binary directly
./app
```

To specify a custom output binary name:
```bash
compiler/scroogec_fast app.sg -o my_app
```

To specify a custom library search directory:
```bash
compiler/scroogec_fast -L /path/to/library app.sg -o my_app
```

### 2. Intermediate File Dumping (`--dump-c` & `--dump-bytecode`)

Performs static verification (`ACCEPT`), dumps the requested intermediate representation file, and exits without generating an executable:

- **Dump C Source Code:**
  ```bash
  compiler/scroogec_fast --dump-c out.c app.sg
  ```
- **Dump Binary Bytecode (.scc):**
  ```bash
  compiler/scroogec_fast --dump-bytecode out.scc app.sg
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

- **100% Self-Contained**: Operates without the retired Python toolchain.
- **Statically Linked**: `scroogec_fast_x86-64` has zero external runtime library dependencies.
- **Intermediate Inspection**: Built-in support for inspecting intermediate C and bytecode output.
- **Library Module Resolution**: Automatically resolves imported library modules from specified or standard library locations (`library/`, `../Scrooge/library/`).
