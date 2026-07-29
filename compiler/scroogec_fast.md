# scroogec_fast / scroogec_fast_x86-64

`scroogec_fast` (and its statically-linked build `scroogec_fast_x86-64`) is a high-performance, single-tool native compiler, static shape-gate verifier, and metrics analyzer for the Scrooge programming language (`.sg`).

## Overview

Compiled from `scroogec_fast.nim`, `scroogec_fast` operates as a **100% self-contained, zero-dependency unified tool** that:
- Performs static verification, shape-gate validation, arity checking, stack effect analysis, and type checking.
- Directly compiles Scrooge source code (`.sg`) into standalone native ELF 64-bit x86-64 executables without requiring external Python tools or runtime script files.
- Bundles the full Scrooge C runtime environment and automatically compiles native binaries via `gcc`.
- Resolves imported standard library modules (`use "strings"`, `use "util"`, etc.) automatically.

## Usage

```bash
scroogec_fast [-L <libDir>] [--stage2] [--metrics] [--check-only] [-o <outBinary>] <file.sg>
```

### Options & Flags

- `<file.sg>` *(Required)*: Path to the Scrooge source file to check, verify, or compile.
- `-L <dir>`, `--lib <dir>`, `--library-dir <dir>`: Specifies a custom directory path for resolving standard library lexicons (e.g., `strings.sg`, `util.sg`, `manifest.sm`).
- `-o <outBinary>`, `--output <outBinary>`: Specifies the output native executable binary name (default: `<basename>` derived from `<file.sg>`).
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

### 2. Static Verification Mode (`--check-only`)

Performs static verification only without compiling a binary executable:

- **Success Output:**
  ```text
  ACCEPT
  ```
- **Failure Output:**
  ```text
  REJECT <ErrorClass> <WordName>
  ```
  *(Example: `REJECT TypeError at`)*

### 3. Metrics Mode (`--metrics`)

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
- **Library Module Resolution**: Automatically resolves imported library modules from specified or standard library locations (`library/`, `../Scrooge/library/`).
