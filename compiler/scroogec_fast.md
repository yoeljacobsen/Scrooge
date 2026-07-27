# scroogec_fast_x86-64

`scroogec_fast_x86-64` is a high-performance, statically-linked native binary for verifying, type-checking, and analyzing Scrooge source code (`.sg`) on x86-64 Linux architectures.

## Overview

Compiled from `scroogec_fast.nim`, `scroogec_fast_x86-64` serves as the primary compiler and static checker for the Scrooge language. It operates as a self-contained, zero-dependency binary that tokenizes source code, loads standard library manifests (`manifest.sm`), enforces language safety rules, and generates static code metrics.

## Usage

```bash
scroogec_fast_x86-64 [--stage2] [--metrics] <file.sg>
```

### Parameters & Options

- `<file.sg>` *(Required)*: Path to the Scrooge source file to check or analyze.
- `--stage2`: Enables Stage 2 verification rules (enabled by default).
- `--metrics`: Calculates transitive metrics for the entry point macro and outputs a JSON summary.

## Modes of Operation

### 1. Verification Mode (Default)

Performs static verification, checking for syntax errors, stack imbalance, type mismatches, reserved word violations, and structural constraints.

- **Success Output:**
  ```text
  ACCEPT
  ```
- **Failure Output:**
  ```text
  REJECT <ErrorClass> <WordName>
  ```
  *(Example: `REJECT UnknownWordError foo`)*

### 2. Metrics Mode (`--metrics`)

Calculates static execution metrics for the entry word in the target file and outputs formatted JSON:

```json
{
  "transient_stack_depth": 4,
  "static_branch_count": 2
}
```

## Key Characteristics

- **Statically Linked**: Zero dynamic runtime library dependencies (`libc`, `libm` statically bundled).
- **Manifest Resolution**: Automatically searches for library signatures in `./library/manifest.sm` or `../library/manifest.sm`.
- **Primary Tooling**: Specified in `spec/scrooge_skill.md` as the sole binary for Scrooge code verification and compilation.
