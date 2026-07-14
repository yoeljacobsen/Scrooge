# Scrooge Library and Compiler Primitive Proposals

This document outlines proposed improvements, bug fixes, and additions to the Scrooge language specifications and standard library primitives based on the evaluation of the Python subset interpreter under Scrooge v1.30.

---

## 1. Core Runtime Operator Adjustments

### Integer Division by Default (`/` Operator)
* **Problem:** In the transpiler runtime, `/` was mapped to Python's float division (`a / b`), returning a floating-point number. Because Scrooge has no floating-point type and operates under Forth-like integer semantics, this led to stack pollution with `float` types and formatting errors.
* **Proposal:** The `/` operator must strictly transpile to integer floor division (`a // b` or `int(a / b)`).
* **Code Change:**
  ```python
  # In transpiler.py operator map:
  def op_div(stack):
      b = stack.pop()
      a = stack.pop()
      stack.append(a // b)
  ```

---

## 2. Recommended Standard Library Additions

To reduce boilerplate in user programs, we propose adding standard primitives for string formatting and stream output:

### `print_char` / `print_int` Primitives
* **Current Effort:** The current Python interpreter requires writing 40+ lines of complex Scrooge code to initialize a custom stdout heap buffer, convert integer digits via base-10 modulo/division recursion, write individual ASCII values, and reconstruct them via list concatenation (`cons`).
* **Proposal:** Add native, low-overhead words for writing values directly to the stdout stream:
  - `print_char ( scalar -- )`: Appends a single character (ASCII value) directly to the system stdout.
  - `print_int ( scalar -- )`: Formats and appends an integer directly to the system stdout.

---

## 3. Control Flow Enhancements

### Tail-Call Optimization (TCO) or Native Loops
* **Problem:** Scrooge programs rely entirely on recursion for loops. Because each function call/binding sequence compiles to nested Python functions, a deep iteration (such as zeroing 1000 heap cells in `init_heap_cells`) triggers Python's `RecursionError` by exceeding the execution stack depth.
* **Proposal:**
  - Implement **Tail-Call Optimization (TCO)** in the transpiler to compile tail-recursive Scrooge words into iterative loops instead of nested functions.
  - Introduce a native loop construct:
    - `loop [ body ]`: Executes a closure repeatedly until a condition is met.
