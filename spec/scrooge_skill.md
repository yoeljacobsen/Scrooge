# Skill: Writing Correct Scrooge (v1.48)

Operational guide for generating Scrooge code that passes static verification on the first try. The specification defines the language; this document defines the methodology, patterns, and empirical best practices.

---

## 0. Preparation & Standard Library Rules

1. **Learn before development**: Study language specifications (`spec/scrooge_spec_v1_48.txt`) and library modules in `library/`.
2. **Do not reinvent library words**: Always check existing library files (`util.sg`, `strings.sg`, `memory.sg`, `array.sg`, `list.sg`, `map.sg`, `record.sg`) before writing custom helpers. Import existing library words with `use "<module>"` (e.g., `use "util"`).

---

## 1. Decompose into Small Words

Scrooge rewards many small words over one large word:
- **One word = one job**, minimal live variables, shallow stack depth.
- Give each helper a clear signature (`#helper_name ( input:Type -- output:Type )`).
- **Define helpers BEFORE the word that calls them**.

---

## 2. Name Values with Frames; Avoid Stack Gymnastics

Prefer arrow frames `-> [ a b ] [ ... use a, b by name ... ]` over positional stack shufflers (`dup`, `swap`, `rot`, `over`). Arrow frames preserve static type tags, whereas shufflers produce `Unknown` types.

- **Unbracketed `cond` Conditions**: Write `flag cond [ true_branch ] else [ false_branch ] ?`. Do NOT place brackets `[` `]` around the condition expression `flag`.
- **Clean Single-Frame Scoping**: In helper words, decompose complex steps into top-level helper words:
  ```scrooge
  #copy_block ( blk:Block -- copy:Block )
    -> [ blk ] [
      blk [fold| idx acc val _ | val acc cons from nil ] reverse
    ]
  end
  ```

---

## 3. Choose the Right Access Operation by Structure

- **Sequence (Arrays / Lists / Blocks)**: Integer index $\rightarrow$ `array_at` / `list_at` / `block_at` or `at`.
- **Record (Mixed Types)**: Key / slot $\rightarrow$ `record_get` / `map_get`. Records do NOT provide `_at`.
- **Heap Pointer (from `hnew`)**: `hread` / `hwrite`. Never use `_at` or `_get` on heap pointers. Pointer arithmetic (`ptr 1 +`) is forbidden; compute integer offsets as Scalars.

---

## 4. Block-Building Idioms

- **Sequential `cons` (Order-Preserving)**:
  Pushing values sequentially onto `nil` (`v0 v1 cons ... nil cons`) preserves original input order (`[v0, v1]`). Do NOT follow with `reverse`.
  ```scrooge
  { Preserves original order [10, 20] }
  10 20 nil cons cons
  ```

- **`fold` Accumulation (Inverting)**:
  Accumulating values during `[fold| ... | val acc cons from nil ]` prepends elements one-by-one, which inherently reverses iteration order. Use a trailing `reverse` step when input order must be preserved:
  ```scrooge
  #copy_block ( blk:Block -- copy:Block )
    -> [ blk ] [
      blk [fold| idx acc val _ | val acc cons from nil ] reverse
    ]
  end
  ```

---

## 5. Numeric Conversions & Arithmetic

- **Floating-Point Literals**: Use bare decimal floats (`0.0`, `3.14`, `-0.5`) or scientific notation (`314e-2`).
- **Explicit Float Casting (`to_float`)**:
  Cast integer scalars to float before division (`/`) when float division is required:
  ```scrooge
  #avg_calc ( sum:Scalar count:Scalar -- avg:Scalar )
    -> [ sum count ] [
      sum to_float count to_float /
    ]
  end
  ```

---

## 6. Standard Library Additions (v1.48)

Import library lexicons at the top of the file via `use "<lexicon>"`.

- **Signed Integer Formatting (`strings.sg`)**:
  `int_to_str ( n:Scalar -- str:Block )` converts positive and negative integers to digit character blocks (e.g., `-42` $\rightarrow$ `"-42"` prepended with ASCII `-` / 45).

- **Block Equality & Sorting (`util.sg`)**:
  - `#block_eq ( b1:Block b2:Block -- equal:Scalar )`: Checks length equality first, then folds element-by-element equality (returns `1` if equal, `0` otherwise).
  - `#block_sort ( blk:Block -- sorted:Block )`: Stable insertion sort returning a sorted block.

- **Safe Indexing (`array.sg`)**:
  - `#nth_or_default ( arr:Block idx:Scalar default:Unknown -- val:Unknown )`: Returns element at `idx` if within bounds (`0 <= idx < arr len`), otherwise returns `default`.

---

## 7. Failure Checklist (Check Before Emitting Code)

1. **Reserved Words**: Never use reserved words as parameter names or frame aliases (`use`, `lexicon`, `to`, `from`, `and`, `or`, `not`, `cond`, `else`, `map`, `fold`, `pk`, `roll`, `select`, `nil`, `cons`, `pair`, `end`, `dup`, `drop`, `swap`, `rot`, `over`, `fill`, `len`, `seed`, `rand`, `exp`, `log`, `pow`, `sqrt`, `abs`, `max`, `min`, `to_float`, `hnew`, `hread`, `hwrite`, `print_char`, `print_int`).
2. **Lexicon Shadowing**: Never define a `#word` that shadows a `use`-imported word or standard primitive.
3. **Unbracketed `cond` Condition**: Ensure `cond` condition is unbracketed expression (`flag cond [ ... ] else [ ... ] ?`).
4. **Literal `roll`/`pk` Index**: Use literal indices only (`1 pk`, `2 roll`).
5. **No Code Nesting**: Depth-1 cap on code blocks inside code blocks.
6. **Correct Access Operator**: Use `_at` for arrays, `_get` for records, `hread` for heap handles.
7. **Every Helper Defined Before Caller**: Order words from dependencies to caller.

---

## 8. Verification and Compilation

For all static verification, shape-gate analysis, and native executable generation, use `scroogec_fast` (or `compiler/scroogec_fast_x86-64`):
```bash
./scroogec_fast -L library <file.sg>
```
