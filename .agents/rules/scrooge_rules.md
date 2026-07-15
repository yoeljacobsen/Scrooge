# Scrooge v1.41 Workspace Rules & Agent Directives

This rule file ensures the Google Antigravity environment enforces Scrooge language standards and guidelines when reading, writing, or generating Scrooge script code.

---

## 1. Antigravity Agent Directives

1. **Enforce Postfix Stack Syntax:** Scrooge v1.41 is strictly a postfix stack language. All deprecated infix or imperative structural remnants (such as `fn`, `ret`, `for`, `while`, `.push`, or `.pop`) are decommissioned.
2. **First-Pass Static Verification Invariant:** Code is only valid when the static checker (`python3 check/scrooge_check.py <file>`) returns a clean exit status.
3. **Immutability Model:** Scrooge list operations are copy-on-write. Backtrack flows should rely entirely on passing the updated array state down the execution line.
4. **No Variables:** Never use primitive names or keywords (e.g., `end`, `pair`, `nil`) as parameters or frame aliases.
5. **Pointer Arithmetic Protection:** Pointers are opaque. Compute integer offsets first, then pass to memory primitives (`ptr offset hread` or `val ptr offset hwrite`).

---

## 2. Core Scrooge v1.41 Language Specification Reference

### 2.1 Core Data Types
* **Scalar:** Signed 64-bit integers or floating-point mantissas (e.g., `314e-2`).
* **Strings:** Enclosed in double quotes (e.g., `"Hi"`), expanded during pre-compilation to ASCII Block arrays.
* **Block:** Indexable, immutable arrays enclosed in square brackets `[ ... ]`.

### 2.2 Operator Registry Highlights
* Stack Shufflers: `.`, `%`, `$`, `@`, `;`, `roll`, `pk`
* List Operations: `cons`, `pair`, `len`, `nil`, `:` (get), `to` (slice)
* Heap Manipulation: `hnew`, `hread`, `hwrite`
* Control Flow: `cond` / `else` / `?` (If-Else), context iterators `[map|` and `[fold|`

---

## 3. Versioning & Tagging Policy

- **Absolute Version Lockstep:** The repository release tag (e.g., `v1.41`) freezes the compiler, static checker, standard library, and agent system prompts in absolute alignment.
- **Spec Changes Trigger Versioning:** Any change to the system prompt specification (`spec/system_prompt_v1.41.txt`) or primitive semantics that results in a new version MUST trigger a new Git tag creation matching the version number exactly.
