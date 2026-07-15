# Scrooge Mono-Repo (v1.41 Postfix Stack Language)

This repository contains the unified specification, compiler, static checker, and standard library for **Scrooge v1.41**, a purely functional, postfix stack-oriented programming language designed for extreme token economy, copy-on-write immutability, and stateless stack operations.

Scrooge v1.41 strictly conforms only to the **postfix stack-based** design. All deprecated infix or imperative-style structural remnants (such as `fn`, `ret`, `for`, `while`, `.push`, or `.pop`) have been completely decommissioned.

---

## Directory Structure

The mono-repo is organized into clean, isolated components:

- **`spec/`**: Contains the frozen system specification prompts used to align downstream coding agents.
  - `system_prompt_v1.41.txt`: The definitive Scrooge v1.41 language definition and primitive registry.
- **`compiler/`**: The core transpilation and style checking tools.
  - `transpiler.py`: Compiles Scrooge postfix stack code into Python executable targets (supporting TCO, block iterators, and division semantics).
  - `linter.py`: Pre-compilation static linter enforcing syntax constraints and keywords.
- **`check/`**: The static checker toolchain and conformance test assets.
  - `scrooge_check.py`: The unified verification runner coordinating dual-track static analysis.
  - `scrooge.py`: Reference interpreter and tokenizer.
  - `verify.py`: Track 1 arity checker.
  - `typecheck.py`: Track 2 coarse type validator.
  - `manifest.sm`: Checker's MCP module import signatures manifest.
  - `corpus/`: Complex Scrooge files used to test checker conformance.
- **`library/`**: Verified standard library lexicon sources.
  - `array.sg`, `list.sg`, `map.sg`, `memory.sg`, `record.sg`, `strings.sg`, `util.sg`
  - `manifest.sm`: Standard library MCP master manifest.
  - `manifest_check.py`: Manifest drift detection script.
- **`programs/`** & **`samples/`**: Postfix Scrooge application programs and benchmark samples.

---

## Getting Started

### Local Verification
To statically check and verify any Scrooge postfix program against the Track 1 & 2 validators, execute:
```bash
python3 check/scrooge_check.py <file>
```

To run the full checker conformance test suite:
```bash
python3 check/scrooge_check.py --suite
```

### Transpiling and Running
To transpile and run Scrooge code via the Python compiler backend:
```python
import sys
import os
sys.path.insert(0, 'compiler')
import transpiler

scrooge_code = '[ "Hi, Scrooge!\n" str_print ]'
# Note: For programs using libraries, prepend standard library files
# e.g., library/util.sg, library/strings.sg
```

### Running Performance Benchmarks
To run the benchmarks and profile execution metrics:
```bash
python3 run_comparisons.py
```

---

## Release Alignment Invariant

The repository tag (e.g., **`v1.41`**) locks the **System Prompt**, **Compiler**, **Checker**, and **Standard Library** in absolute, unyielding lockstep. Any changes to primitive semantics, compiler behaviors, or static constraints are synchronously propagated across all four layers to prevent drift.

---

## Authors & License

- **Author**: Yoel Jacobsen (<yoel.jacobsen@gmail.com>)
- **License**: MIT License - see the [LICENSE](LICENSE) file for details.
