# Skill: Writing Correct Scrooge

Operational guide for generating Scrooge that passes the checker on the first
try. The spec defines the language; this defines the method. Empirically, most
failures come from a small set of mistakes listed in §4 — internalize those.

## 1. Method: decompose into small words

Scrooge rewards many small words over one big word. This is not style — a word
that threads 7+ named values through recursion is where generation reliably
fails. When a task needs wide state, split it:

- One word = one job, few live values, shallow stack.
- Give each helper a clear signature; let the top-level word just wire helpers
  together.
- Define helpers BEFORE the word that calls them.

Example shape (merge, decomposed): a `copy-one-cell` word, a `drain-the-rest`
word, a `compare-and-step` word, and a tiny entry word — not one 9-alias
monster. Decomposition is the single highest-leverage habit for correctness.

## 2. Name values with frames; avoid stack gymnastics

Prefer `-> [ a b ] [ ... use a, b by name ... ]` over juggling values
positionally with dup/swap/rot. Named values are easier to get right and the
checker tracks their types (it loses types across shufflers). Reach for a frame
whenever more than two values are live.

## 3. Choose the right access operation by the structure you hold

- Sequence (all elements same type) → integer index → `array_at` / `list_at` /
  `block_at`.
- Record (fields of different types) → static key/slot → `record_get` /
  `map_get`. Records have no `_at`; do not index them.
- Heap pointer (from `hnew`) → `hread` / `hwrite`, never `_at`/`_get`.
The operation name states the type — say what you hold, and the word follows.

## 4. The failure list (check every one before you finish)

These are the mistakes that actually recur. Scan your output against them:

1. Reserved word as a name. exp, max, min, len, end, sum-of-primitives... are
   reserved. If a natural parameter name is reserved, rename it (e, mx, n).
2. Wrong index operator. `_at`/`_get` on a heap Ptr, or `hread` on a Block, or
   `_at` on a record. Match operator to structure (§3).
3. Unbalanced `cond`. Both branches must leave the same number AND types.
4. `roll`/`pk` with a non-literal index. Only `1 pk`, never `idx pk`.
5. Shadowing your own word name with a local alias. Use a distinct alias.
6. Nested code blocks. No code block inside a code block; extract to a word.
7. Missing `cond` keyword: `flag cond [..] else [..] ?`, never `flag [..] ...`.
8. Iterator context order: if ctx is used, `ctx block [fold| ... ]`; if not,
   bind it `_`.
9. Unbracketed frame: both `[ vars ]` and `[ body ]` are required.
10. Pointer arithmetic (`ptr 1 +`). Compute the offset as a Scalar first.
11. Missing `use "..."` for a library word (e.g. `<=`/`>=` need `use "util"`).
12. Whitespace: brackets are tokens — `[ 1 2 ]`, `x ]`, never `[1 2]`, `x]`.
13. In-place swap that overwrites before reading — read both cells first.
14. Forgetting a word is defined before its caller.

## 5. Loops

No loop keyword. Write a tail-recursive word: a frame binds the state, a
trailing `cond` tests the exit, the recursive branch calls the word again with
advanced state. Keep the carried state minimal — if it grows past a few values,
decompose (§1).

## 6. Mutation

Blocks are structurally immutable and value-mutable: `_set` may replace a
slot's value with the same type, never change shape or type. If a word you call
may mutate a value you still need, do not assume it is unchanged after the call
— the word's signature declares whether it mutates. Real shared mutable state
lives on the heap; reach for it deliberately, not by default.

## 7. Self-check before emitting

1. Does every word's body net-match its signature arity?
2. Does every `cond` balance in count and type?
3. Is any name a reserved word? Any `roll`/`pk` index non-literal?
4. Is every access operator matched to its structure (§3)?
5. Any code block nested in a code block?
6. Every library word covered by a `use`?
7. Every helper defined before its caller?

Passing the checker proves the program is well-formed, not that it is correct.
After it checks, re-read the logic against the task: a balanced, well-typed
word can still compute the wrong answer.
