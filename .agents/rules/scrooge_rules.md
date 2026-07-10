# Scrooge v1.2 Workspace Rules & Agent Directives

This rule file ensures the Google Antigravity environment enforces Scrooge language standards and guidelines when reading, writing, or generating Scrooge script code.

---

## 1. Antigravity Agent Directives

1. **Enforce the Immutability Model:** Scrooge list operations (especially `::`) are copy-on-write. Never write destruction loops; backtrack flows should rely entirely on passing the updated array state down the execution line.
2. **Never Invent Namespaces:** Scrooge contains no variables. If an implementation draft shows names assigned to temporary scopes (e.g., inside a `[ ... ]` block), discard the code artifact immediately and force a rewrite.
3. **Optimize Using Deep Access:** If a task requires processing data elements located deeper than three levels down the current stack register, do not write wrapping operations (`wrap +`). Use `pick` or `roll` directly to eliminate structural token overhead.
4. **Isolate Concatenation from Prepends:** `+` combines lists together. When pushing an item to the head of a matrix line without losing its structural identity, you must use the native `cons` primitive.

---

## 2. Core Scrooge v1.2 Language Specification

### 2.1 Core Data Types
* **Int:** Standard integer (e.g., `42`, `-5`).
* **Float:** Standard float (e.g., `3.14`).
* **Bitstring / Hex / Binary literals:** Native integer representations (e.g., `b0101` for binary 5, `h5f` for hex 95).
* **Block:** An indexable, executable sequence of elements enclosed in square brackets `[ ... ]`. Serves as both data arrays and deferred code blocks.

### 2.2 Operators & Stack Effects
All operators pop their arguments from the stack and push their results.

#### Stack Manipulation
* `.` (dup) : `x -> x x` (duplicates the top element)
* `%` (drop) : `x -> ` (discards the top element)
* `$` (swap) : `x y -> y x` (swaps the top two elements)
* `@` (rot) : `x y z -> y z x` (rotates top three; third element becomes top)
* `;` (over) : `x y -> x y x` (duplicates second element to top)
* `wrap` : `x -> [x]` (wraps top element in a single-element block)
* `pick` : `... x_N ... x_0 N -> ... x_N ... x_0 x_N` (copies the N-th element to top, 0-indexed)
* `roll` : `... x_N ... x_0 N -> ... x_0 x_N` (moves the N-th element to top, rotating elements)

#### Arithmetic & Bitwise
* `+` : Addition / Concatenation. If both operands are lists, concatenates them. If both are numbers, performs standard addition.
* `-` : Subtraction
* `*` : Multiplication
* `/` : Division
* `//` : Integer Division
* `\` : Modulo
* `^` : Bitwise XOR
* `&` : Bitwise AND
* `|` : Bitwise OR
* `~` : Bitwise NOT (unary)
* `<<` / `>>` : Bitwise left / right shifts

#### Comparison (pushes `1` for true, `0` for false)
* `=` (equals), `!=` (not equal), `>`, `<`, `>=`, `<=`

#### List / Block Operations
* `cons` : `x L -> [x ...L]` (prepends element `x` to list `L` without flattening)
* `:` (get) : `block index :` -> Returns element at index (0-indexed)
* `::` (set) : `block index value ::` -> Returns a new block with value replaced (copy-on-write immutability)
* `len` : `block len` -> Returns number of elements
* `slice` : `block start end slice` -> Returns a sub-block from start to end (exclusive)

#### Control Flow & Modularity
* `?` (If-Else) : `cond [ true_block ] [ false_block ] ?` -> Pops all three. If cond != 0, runs true_block; else runs false_block.
* `!` (Loop/Map) : `limit/array [ block ] !` -> Pops both. If given integer N, runs N times. If given an array block, maps over each item, pushing it onto the stack first.
* `,` (Apply) : `[ block ] ,` -> Pops and executes block directly on current stack.
* `#name [ ... ]` defines a stateless token substitution macro (Skill). Optional type annotations take the form `#name ( inputs -- outputs ) [ ... ]`.

---

## 3. Structured Task System Prompt Template

```text
You are a development agent operating inside the Scrooge language framework (v1.2).
You must write code using absolute token economy, zero mutable naming conventions, and purely functional stack operations.

Your Code Compilation Checklist:
1. Verify Stack Balance: Ensure every macro block accurately clears or fulfills its target stack footprint.
2. Use Flat Layouts: Prefer shallow stack depths using `pick` or loop maps (`!`) over nested code trees.
3. Format Explicit Outputs: Wrap the final clean Scrooge script code cleanly within code fences like:
   ```text
   [ code here ]
   ```
```
