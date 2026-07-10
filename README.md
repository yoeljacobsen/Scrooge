# Scrooge Language Implementation & Experiments

This repository contains the implementation, tools, and experimental programs for the **Scrooge** programming language.

## About Scrooge

Scrooge is a purely functional, stack-oriented (concatenative) programming language designed with an emphasis on token economy, copy-on-write immutability, and stateless stack operations.

### Key Features
- **Purely Functional**: No variables or mutable state. All operations are performed directly on the stack.
- **Copy-on-Write Immutability**: Core data structures (such as lists/blocks) are immutable. Operations like setting an element return a new block.
- **Concatenative Stack Operations**: Standard stack manipulation primitives (`.` (dup), `%` (drop), `$` (swap), `@` (rot), `;` (over), `pick`, `roll`, `wrap`).
- **Control Flow**:
  - `?` (If-Else): Evaluates conditional execution blocks.
  - `!` (Loop/Map): Performs loops or maps over arrays.

---

## Repository Structure

The repository is organized as follows:
- **`transpiler.py`**: The core compiler and transpiler that compiles Scrooge code to Python.
- **`run_comparisons.py`**: Benchmark runner that profiles and validates Scrooge programs against equivalent Python implementations.
- **`problems.json`**: Benchmark problem definitions.
- **`programs/`**: Collection of Scrooge programs and experimental outputs (e.g., Fibonacci, GCD, Hessenberg QR, MNIST).
- **`docs/`**: Design documents, orchestration profiles, and specifications.
- **`prompts/`**: Different versions of the system prompts used to generate Scrooge programs.
- **`discussion_state/`**: The conversation transcripts and development history leading to this version.
- **`samples/`**: Sample Scrooge files and their Python equivalents.
- **`scratch/`**: Temporary testing and validation scripts.

---

## Getting Started

### Transpiling and Running Scrooge Code
You can transpile and run Scrooge code directly using the Python transpiler:
```python
import transpiler

scrooge_code = "[ 1 2 + ]"
result = transpiler.run_scrooge(scrooge_code)
print(result)  # Output stack
```

### Running Benchmarks
To run the benchmarks and print performance comparisons:
```bash
python3 run_comparisons.py
```
