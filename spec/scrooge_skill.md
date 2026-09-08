# Skill: Writing Correct Scrooge (v1.48)

Operational guide for generating Scrooge code that passes static verification on the first try. The specification defines the language; this document defines the methodology, patterns, and empirical best practices.

---

## 0. Preparation & Standard Library Rules

1. **Learn before development**: Study language specifications (`spec/scrooge_spec_v1_48.txt`) and library modules in `library/`.
2. **Do not reinvent library words**: Always check existing library files (`util.sg`, `strings.sg`, `memory.sg`, `array.sg`, `list.sg`, `map.sg`, `record.sg`, `bitset.sg`, `file.sg`, `args.sg`) before writing custom helpers. Import existing library words with `use "<module>"` (e.g., `use "util"`).

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
- **File Handle (from `fopen`)**: `fgetc` / `fputc` / `fread` / `fwrite`, or the `file.sg` words below. A `File` is opaque in exactly the way a `Ptr` is: arithmetic on it, `hread`/`hwrite` through it, and `_at`/`_get`/`_set` into it are all static `TypeError`s.
- **Command-Line Argument (from `argv`)**: an ordinary `Block` of character codes -- index it, compare it, print it like any other string. `argc`/`argv` use C's indexing exactly: `0 argv` is the program, the first real argument is `1 argv`.

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

## 6b. Sequential File I/O (`file.sg`)

A file is read and written as a Block of character codes -- the same representation `strings.sg` uses -- through an opaque `File` handle. Handles 0/1/2 are pre-opened as stdin/stdout/stderr, so the same words serve the standard streams (`f_stdin`, `f_stdout`, `f_stderr`).

**Reach for the whole-file words first.** They open, transfer and close in one step, and report every failure through an `ok` Scalar:
```scrooge
use "file"
#save_report ( text:Block -- ok:Scalar )
  -> [ text ] [ text "report.txt" f_write_file ]
end
```
- `f_read_file ( path:Block -- str:Block ok:Scalar )` / `f_write_file ( str:Block path:Block -- ok:Scalar )` / `f_append_file ( str:Block path:Block -- ok:Scalar )`.

**Open explicitly when one handle serves several operations.** Use the named mode helpers, never a bare mode integer:
- `f_open_read` / `f_open_write` / `f_open_append` `( path:Block -- fh:File ok:Scalar )`, then `fclose ( fh:File -- ok:Scalar )`.
- `f_read_all ( fh:File -- str:Block )`, `f_read_line ( fh:File -- line:Block got:Scalar )`, `f_write_str ( str:Block fh:File -- ok:Scalar )`, `f_write_line ( str:Block fh:File -- ok:Scalar )`.

**Check the flag, always.** Nothing in this lexicon aborts on a missing file, a full handle table or a short write -- it returns `ok=0`, `got=0`, or a written count below `str len`. A `cond` on that flag is not optional politeness; skipping it means using a handle that was never opened.

**Choose the granularity deliberately.** `fread`/`fwrite` move a whole chunk in one C-level pass. `fgetc`/`fputc` move one character and cost a word call plus a `cons` copy each, so use them only where the read must stop exactly at a delimiter (which is what `f_read_line` does). Never hand-write a per-character loop to do what `f_write_str` or `f_read_all` already does.

**Mind the width.** One character read into a Block occupies a full Block slot, considerably wider than a byte. `f_read_all` is right for configuration and data files; stream anything much larger with `fread` a chunk at a time rather than accumulating the whole input.

---

## 6c. Command-Line Arguments (`args.sg`)

`argc` and `argv` use C's indexing exactly: `0 argv` is the program as invoked, the first real argument is `1 argv`, and `argc` counts both -- so `argc` is 1 for a program run with no arguments. An argument is a `Block` of character codes, so it prints and compares like any other string.

**Prefer `arg_or` over a bare `argv`.** It takes a default and returns just the argument, keeping the ok flag out of your call site:
```scrooge
use "args"
#output_path ( -- path:Block )
  1 "out.txt" arg_or
end
```

**Iterate with `arg_tail`.** It gives the arguments *without* the program name, as a `Block` of `Block`s -- the shape a `[fold| ... ]` wants. It is also the only word here that materializes every argument, so ask for one argument by index when that is all you need.

**Scan flags with `arg_find`.** `"-v" arg_find` answers "was `-v` passed, and at which index", using the same found-flag convention as `find_sub`. The search starts at index 1, so the program name can never match.

**Distinguish absent from empty.** `argv` reports a missing index as `ok=0`, but an argument that was supplied and is empty (`prog ""`) is `ok=1` with an empty `Block`. Do not treat length 0 as "not given".

**Read `programs/args_demo.sg`** for the whole shape of a command-line program: flags separated from operands, the program named in a diagnostic, and standard input used when no operands were given.

---

## 7. Failure Checklist (Check Before Emitting Code)

1. **Reserved Words**: Never use reserved words as parameter names or frame aliases (`use`, `lexicon`, `to`, `from`, `and`, `or`, `not`, `cond`, `else`, `map`, `fold`, `pk`, `roll`, `select`, `nil`, `cons`, `pair`, `end`, `dup`, `drop`, `swap`, `rot`, `over`, `fill`, `len`, `seed`, `rand`, `exp`, `log`, `pow`, `sqrt`, `abs`, `max`, `min`, `to_float`, `hnew`, `hread`, `hwrite`, `print_char`, `print_int`, `abort`, `hmark`, `hrelease`, `fopen`, `fclose`, `fgetc`, `fputc`, `fread`, `fwrite`).
2. **Lexicon Shadowing**: Never define a `#word` that shadows a `use`-imported word or standard primitive.
3. **Unbracketed `cond` Condition**: Ensure `cond` condition is unbracketed expression (`flag cond [ ... ] else [ ... ] ?`).
4. **Literal `roll`/`pk` Index**: Use literal indices only (`1 pk`, `2 roll`).
5. **No Code Nesting**: Depth-1 cap on code blocks inside code blocks.
6. **Correct Access Operator**: Use `_at` for arrays, `_get` for records, `hread` for heap handles, `fgetc`/`fread` for file handles.
7. **Every Helper Defined Before Caller**: Order words from dependencies to caller.

---

## 8. Verification and Compilation

For all static verification, shape-gate analysis, and native executable generation, use `scroogec_fast` (or `compiler/scroogec_fast_x86-64`):
```bash
./scroogec_fast -L library <file.sg>
```
