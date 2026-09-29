# Skill: Writing Correct Scrooge (v1.55)

Operational guide for writing Scrooge that passes static verification and runs right. The specification defines the language; this guide is the method: how to learn it, how to build a program in it, the patterns that work, and how to debug.

---

## 0. How to Learn Scrooge

Learn the language from its documents and from small experiments, in this order:

1. **Read the specification** (`spec/scrooge_spec_v1_55.txt`) once, end to end. It is short and normative: when this guide and the spec disagree, the spec wins.
2. **Read this guide**, in particular sections 2 to 2c (frames, how stack effects add up, loops): they cover the rules that cost earlier programmers the most rebuilds.
3. **Look every word up in `library/manifest.sm`**: one typed line per library word (`tool`) with a one-line description, and one per primitive (`prim`), e.g. `hwrite ( v:Unknown p:Ptr i:Scalar -- )`. Spec Sec.8 lists the same signatures per lexicon. It is generated from the sources and checked against the compiler, so it is exact. Check it before writing a helper: sorting, string conversion, argument parsing, bit counts, file reading and more already exist.
4. **Then experiment.** When a rule is unclear, write a 3-line program that tests exactly that question, check it (`--check-only`) and run it. A probe answers in seconds and is always right; reasoning about stack effects in your head often is not.

Learn from the documents and your experiments, not from the compiler's internals: do not read the generated C (`--dump-c`) or the compiler's source to work out what Scrooge means. The documents are meant to be complete; where they are not, a probe program is the right way to find out, and a note in your friction log is the right way to report the gap.

---

## 0b. How to Build a Program

**Design top down.** Before writing code, write the program's structure as a short outline: the main loop, the data it keeps (as `#record` layouts, section 3), and the few words each part needs, with their signatures. A signature is a promise the checker enforces, so choosing them first is most of the design.

**Implement bottom up, in small increments.** Build the lowest layer first (parsing a number, one record accessor, one helper), and make it pass `--check-only` and a tiny test program before building on it. Then the next layer, tested the same way. Never write several hundred lines and compile them for the first time together: the first error hides the design problem behind it.

- Keep a test program per layer (a `main` that calls the layer's words on known inputs and prints the results), and keep it passing as you go.
- Split a large program into user modules (section 6d): one file per layer, each with its own test program.
- While iterating, build with `-O0` (a large program builds in seconds instead of tens of seconds); measure speed only with the default `-O3`.
- Keep a running note of what is done and what is next, so a long task survives an interruption.

---

## 0c. Standard Library Rules

1. **Do not reinvent library words**: check `library/manifest.sm` before writing a helper. Import lexicons with `use "<lexicon>"` (e.g., `use "util"`).
2. **Your own modules**: `use "name"` loads the file "name.sg" from your program's directory when no library lexicon has that name (section 6d).

---

## 1. Decompose into Small Words

Scrooge rewards many small words over one large word:
- **One word = one job**, minimal live variables, shallow stack depth.
- Give each helper a clear signature (`#helper_name ( input:Type -- output:Type )`).
- Words may appear in any order (a word can call one defined later); putting helpers first just reads better.

---

## 2. Name Values with Frames; Avoid Stack Gymnastics

Prefer arrow frames `-> [ a b ] [ ... use a, b by name ... ]` over positional stack shufflers (`dup`, `drop`, `swap`, `rot`, `over`, the only five that exist). Arrow frames preserve static type tags, whereas shufflers produce `Unknown` types. A frame binds at most 64 names; for more state, use a `#record`.

- **Unbracketed `cond` Conditions**: Write `flag cond [ true_branch ] else [ false_branch ]`. Do NOT place brackets `[` `]` around the condition expression `flag`. When there is nothing to do on the false path, drop the else-branch: `flag cond [ true_branch ]` (the true branch must then have net effect 0). A trailing `?` is optional.
- **Clean Single-Frame Scoping**: In helper words, decompose complex steps into top-level helper words:
  ```scrooge
  #copy_block ( blk:Block -- copy:Block )
    -> [ blk ] [
      blk [fold| idx acc val _ | val acc cons from nil ] reverse
    ]
  end
  ```

---

## 2b. How Stack Effects Add Up

The checker counts, for every word, how far each token moves the stack, and rejects a body whose total differs from its signature. These are the rules it applies, which cost earlier agents the most rebuilds:

- **A frame pops.** `-> [ a b ]` takes the top two values off the stack (net -2) and names them. Names stay in scope to the end of the enclosing block, so a later frame binds only NEW values: `-> [ s n ] [ ... ] s n foo -> [ r ] [ ... s n r ... ]`. Re-listing a name that is still in scope, as in `-> [ s n ] [ ... ] -> [ s n r ]`, pops two more values that are not there. Many examples re-push before re-binding (`-> [ a ] [ a a f ] -> [ a b ]`); that is one style, not a requirement.
- **`cond` consumes its flag,** and each branch is measured from there. Both branches must have the same net effect: `x 0 < cond [ 0 ] else [ x ]` is +1 either way. A branch without an else must be net 0. A branch whose last call is `abort` or `exit` is exempt. A branch may consume values below it (a word's parameters), but only if the other branch has the same net effect: `cond [ drop ] else [ ]` is rejected (-1 against 0), while `cond [ drop 0 ] else [ ]` is fine (0 and 0).
- **`and`/`or` evaluate both sides.** To guard a test that would fail on bad input, use `when`: `b len 0 > when [ b 0 block_get x = ]` evaluates the access only for a non-empty Block and is 0 otherwise (`unless` runs its body when the flag is 0). The body leaves exactly one value. For a statement with no result, use `flag cond [ ... ]`.
- **A fold's `from`** can be any expression leaving one value: `from 0`, `from nil`, or a name in scope (`from acc`).
- **A call has its signature's effect**, a word's call to itself included: in `#count ( n:Scalar -- )`, the body `-> [ n ] n 0 = cond [ ] else [ n 1 - count ]` is -1 for the frame, then 0 for the cond (its else-branch pushes `n 1 -`, +1, and the call `count` takes it, -1), total -1 as the signature says.
- **Record accessors:** a field with a count above 1 takes an index, `v s i Name_field_set` and `s i Name_field`; a count-1 field does not, `v s Name_field_set` and `s Name_field`.
- When a word is rejected with `ArityMismatch`, the message lists the stack depth at the end of each line of the body, relative to entry: the first line whose depth is not what you intended is where the stray value is.

---

## 2c. Counted Loops

For a fixed number of iterations, use a counted loop instead of a helper word:

```scrooge
0 10 [times| i | i + ]                      { sum 0..9: leaves 45 }
s 0 81 [for| c | 0 s c Board_cells_set ]     { clear 81 record cells; net 0 }
9 [times| r | 9 [times| c | r 9 * c + ... ] ]   { nested: the inner body sees r }
```

- `n [times| i | body ]` runs i = 0..n-1; `lo hi [for| i | body ]` runs i = lo..hi-1.
- The body's net effect is 0. To accumulate, leave the accumulator BELOW the loop and have the body replace it (`acc i +`); several accumulators work the same way (`0 1 20 [times| i | swap over + ]`).
- It is faster than the equivalent tail-recursive word (a plain C loop; carried values stay in registers) and has no depth limit.
- No `break`: a loop that must stop early (a search, a scan to a delimiter) is still a self-recursive word.

## 3. Choose the Right Access Operation by Structure

- **Sequence (Arrays / Lists / Blocks)**: Integer index $\rightarrow$ `array_at` / `list_at` / `block_at` or `at`.
- **Record (Mixed Types)**: Key / slot $\rightarrow$ `record_get` / `map_get`. Records do NOT provide `_at`.
- **Heap Pointer (from `hnew`)**: `hread` / `hwrite`. Never use `_at` or `_get` on heap pointers. Pointer arithmetic (`ptr 1 +`) is forbidden; compute integer offsets as Scalars.
- **Bulk heap work**: `hmove ( src soff dst doff count -- )` copies cells (overlap-safe), `hfill ( v p start count -- )` sets a range, `hsort` sorts one (numbers, or Blocks such as strings and rows, lexicographically). Use them instead of a per-cell loop.
- **An absent link**: `hnull` is a Ptr that refers to nothing (a tree's missing child, an empty list head). Test it with `p hnull =`; reading or writing through it is a fatal error.
- **Memory**: a Block owns the Blocks inside it and frees them with itself, and a heap cell owns what it holds, so nested data costs nothing once released. Bracket per-item work with `hmark`/`hrelease` so a long run does not keep every allocation alive.
- **Heap state with named fields**: declare it with `#record Name  field Type count ...  end` (spec Sec.5) instead of hand-numbering offsets. It generates `Name_new`, `Name_size`, and per field a typed getter `Name_field`, a setter `Name_field_set` (both take an index argument unless the count is 1: a count-1 setter is `v s Name_field_set`, with no index) and `Name_field_off`, the field's first cell, for bulk words such as `hmove`/`hfill`/`fread_into` that take a raw offset: `#record Board cells Scalar 81 solved Scalar 1 end` then `Board_new -> [ b ] [ 5 b 0 Board_cells_set 1 b Board_solved_set b 0 Board_cells print_int ]`.
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
- **Float to integer**: `x to_int` truncates toward zero (`-3.9 to_int` is -3). **Number to text**: `x 3 float_to_str` is the Block `"3.142"` for 3.14159 (exactly what `3 print_float` prints); `n int_to_str` (strings) for an integer. **Which kind of value**: `v type_of` is 0 for an integer, 1 a float, 2 a Block, 3 a Ptr.
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

## 6. Standard Library Highlights

Import library lexicons at the top of the file via `use "<lexicon>"`.

- **Signed Integer Formatting (`strings.sg`)**:
  `int_to_str ( n:Scalar -- str:Block )` converts positive and negative integers to digit character blocks (e.g., `-42` $\rightarrow$ `"-42"` prepended with ASCII `-` / 45).

- **Block Equality & Sorting (`util.sg`)**:
  - `#block_eq ( b1:Block b2:Block -- equal:Scalar )`: Checks length equality first, then folds element-by-element equality (returns `1` if equal, `0` otherwise).
  - `#block_sort ( blk:Block -- sorted:Block )`: Stable ascending sort, O(n log n) (it uses `hsort`). It sorts numbers, and Blocks lexicographically: a Block of strings sorts in byte order, a Block of rows column by column. For a descending order, `reverse` the result.

- **Safe Indexing (`array.sg`)**:
  - `#nth_or_default ( arr:Block idx:Scalar default:Unknown -- val:Unknown )`: Returns element at `idx` if within bounds (`0 <= idx < arr len`), otherwise returns `default`.

---

**Printing numbers.** `x 3 print_float` prints a number with 3 decimals. For times kept as integer nanoseconds, `ns 3 print_fixed` prints microseconds (`12345 3 print_fixed` is `12.345`), and `n 5 int_to_str_pad` zero-pads to 5 characters; both are in `strings.sg`. Do not hand-roll these.

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

**Choose the granularity deliberately.** `f_read_line` (the `freadline` primitive) reads a line in one C pass. `fh p start count fread_into` reads bytes straight into heap cells, with no Block per character: stream a large file through one fixed heap buffer that way. `fread`/`fwrite` move a whole chunk as a Block. `fgetc`/`fputc` move one character and cost a word call plus a `cons` copy each, so use them only where the read must stop at some other delimiter. Never hand-write a per-character loop to do what `f_write_str`, `f_read_line` or `f_read_all` already does. `fseek`/`ftell` reposition a file (not a pipe).

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

**Parse flags with `arg_flag`, `arg_value_or` and `arg_int_or`.** They cover the usual `-v`, `-f path` and `-n 1000` shapes without a hand-written loop; a missing, trailing or non-numeric value gives the default:
```scrooge
use "args"
#limit ( -- n:Scalar ) "-n" 1000000 arg_int_or end
#verbose ( -- f:Scalar ) "-v" arg_flag end
#input_path ( -- p:Block ) "-f" "data.csv" arg_value_or end
```

**Iterate with `arg_tail`.** It gives the arguments *without* the program name, as a `Block` of `Block`s -- the shape a `[fold| ... ]` wants. It is also the only word here that materializes every argument, so ask for one argument by index when that is all you need.

**Scan flags with `arg_find`.** `"-v" arg_find` answers "was `-v` passed, and at which index", using the same found-flag convention as `find_sub`. The search starts at index 1, so the program name can never match.

**Distinguish absent from empty.** `argv` reports a missing index as `ok=0`, but an argument that was supplied and is empty (`prog ""`) is `ok=1` with an empty `Block`. Do not treat length 0 as "not given".

**Default paths under the home directory.** `"~/Data/x.csv" f_expand_home` (file.sg) gives the path the shell would; `"HOME" getenv` reads a variable directly. Never hard-code a user's home directory.

**Read `examples/args_demo.sg`** for the whole shape of a command-line program: flags separated from operands, the program named in a diagnostic, and standard input used when no operands were given.

---

## 6d. Your Own Modules

A program of more than a few hundred lines belongs in several files. `use "geo"` loads the file "geo.sg" from the directory of the file that says it (when no library lexicon is called `geo`); a module is ordinary Scrooge (word definitions and its own `use` lines), modules may use each other, and each is loaded once. Errors, warnings, runtime word chains and `trace` name the module and its own line: `REJECT UnknownWordError geo.sg line 2 ...`. Give each module a test program that `use`s it.

---

## 7. Failure Checklist (Check Before Emitting Code)

1. **Reserved Words**: Never use reserved words as parameter names or frame aliases (`use`, `lexicon`, `to`, `from`, `and`, `or`, `not`, `cond`, `else`, `map`, `fold`, `pk`, `roll`, `select`, `nil`, `cons`, `pair`, `end`, `dup`, `drop`, `swap`, `rot`, `over`, `fill`, `len`, `seed`, `rand`, `exp`, `log`, `pow`, `sqrt`, `abs`, `max`, `min`, `to_float`, `bitand`, `bitor`, `bitxor`, `bitshl`, `bitshr`, `bitnot`, `hnew`, `hread`, `hwrite`, `print_char`, `print_int`, `abort`, `hmark`, `hrelease`, `fopen`, `fclose`, `fgetc`, `fputc`, `fread`, `fwrite`, `argc`, `argv`, `clock_ns`, `block_slice`, `bitcount`, `bitctz`, `bitclz`, `hsort`, `print_float`, `getenv`, `freadline`, `fread_into`, `fseek`, `ftell`, `trace`, `hmove`, `hfill`, `exit`, `to_int`, `float_to_str`, `type_of`, `hnull`, `when`, `unless`, `sort_cmp`). This is the list in spec Sec.10.
2. **Lexicon Shadowing**: Never define a `#word` that shadows a `use`-imported word or standard primitive; the error names what it collides with.
3. **Unbracketed `cond` Condition**: Ensure `cond` condition is unbracketed expression (`flag cond [ ... ] else [ ... ]`).
4. **Only Five Stack Shufflers**: `dup`, `drop`, `swap`, `rot`, `over`. There is no `pk`, `roll` or `nip`: each is an `UnknownWordError` (`pk` and `roll` are reserved for a possible future implementation). When a value is needed deeper than `over` reaches, bind it with a frame.
5. **Bracketed Values Are Data**: a `[ ... ]` used as a value may hold only literals (`[ 1 [ 2 3 ] ]`); build a Block from computed values with `cons` or `pair`. Cond branches, frame bodies and loop bodies are not values and nest freely.
6. **Correct Access Operator**: Use `_at` for arrays, `_get` for records, `hread` for heap handles, `fgetc`/`fread` for file handles.
7. **Stack effects add up** (section 2b): every `cond` branch has the same net effect, a second frame pops new values, and a count-1 record setter takes no index.
8. **Arithmetic edge cases**: integer `/` truncates toward zero but `\` is the floored remainder (sign of the divisor); integer overflow wraps; `<`/`>` compare numbers only; `a b sort_cmp` is -1, 0 or 1 for two strings (byte order) or rows. A `Ptr` used after the `hrelease` of its region stops the program with a message saying so.
9. **Do not name an alias after one of your words**: `-> [ tbl_name ]` hides `#tbl_name` until the end of the block (the checker warns). Likewise `%` is not modulo (use `\`), and `&&`/`||` do not exist.
10. **Frame Scope Runs to the End of the Block**: `-> [ x ] [ A ] B` is `-> [ x ] [ A B ]`, so `B` still sees `x`. A cond branch does not extend that way: an `else` written after a branch's `]` cannot reach a cond inside it.

---

## 8. Checking, Building and Running

From the repository root:
```bash
compiler/scroogec_fast -L library --check-only prog.sg   # ACCEPT, or every error found
compiler/scroogec_fast -L library -O0 -o prog prog.sg     # fast build while developing
compiler/scroogec_fast -L library -o prog prog.sg         # optimised build (-O3)
```

- The compiler exits 0 on ACCEPT and 1 on REJECT, and a rejected build removes any older binary at the `-o` path, so `build && ./prog` never runs a stale program.
- Warnings (a loop written as two words calling each other in tail position) go to stderr after `ACCEPT`; take them seriously, since such a loop stops at 65,536 trips.
- `exit ( code -- )` ends a program with a status of your choosing.
- For a final speed measurement of a program that already runs correctly, `--no-ptr-check` leaves out the stale-Ptr check (about 7% in heap-read-heavy code). Develop and test with the check on.

**Find where the time goes with `--profile`**, not by guessing: `compiler/scroogec_fast --profile -L library -o prog prog.sg` builds a program that prints, at exit, each word's calls, self time and total time to stderr. Its own output is unchanged. Each timed call adds about 10 ns, so read the call counts as well as the times: a tiny word called 100 million times is the place to restructure.

## 8b. Editing Scrooge Source

The compiler edits source a whole word at a time, so you never need a script that searches for and replaces a snippet of text (which breaks on any difference in indentation). It finds definitions with the compiler's own rules, so `end` or `#name` inside a string or a `{ }` comment is never mistaken for code:

```bash
compiler/scroogec_fast --words prog.sg                 # every definition: name, signature, lines
compiler/scroogec_fast --show parse_row prog.sg        # print one definition
compiler/scroogec_fast --replace parse_row prog.sg < new.sg        # replace it (new text on stdin)
compiler/scroogec_fast --insert-before parse_row prog.sg < helper.sg  # add a helper above it
compiler/scroogec_fast --insert-after parse_row prog.sg < next.sg
compiler/scroogec_fast --delete parse_row prog.sg
compiler/scroogec_fast --fmt prog.sg                   # re-indent (two spaces per bracket level)
```

- The new text (stdin) is one or more complete `#name ... end` definitions. It is checked before anything is written: balanced brackets, every definition ended, the parser accepts it, and no name it defines already exists (except the one being replaced). On any problem the file is left untouched and the reason is printed.
- `--insert-before` is the natural way to add a helper: it lands directly above the word that calls it.
- To change a few lines inside a long word, `--show` it, edit the text, and `--replace` it.
- `--fmt` changes only leading whitespace, never the code or the line count, and `--fmt --check` reports whether a file is already formatted. Formatted files make ordinary text edits reliable too.
- An edit does not check the whole program: run `--check-only` afterwards.

## 9. Debugging a Program That Runs Wrong

Work from cheapest to most detailed, and stay in Scrooge:

1. **`assert` your invariants** (`use "util"`): `count 81 <= "count past the grid" assert` stops the program with that message the first time the invariant fails, instead of minutes later with a corrupted result.
2. **Read the word chain.** A runtime `Fatal:` error is followed by the words that were running, innermost first, each with its definition line (`in #report (defined line 2)`); start there.
3. **`trace` a value**: `x trace` prints `trace line N: <value>` to stderr, for any type: numbers, Blocks (the first 64 elements, and as text when they are all printable characters), and a Ptr as its size. It consumes the value, so trace a frame-bound name (`-> [ x ] [ x trace ... x ... ]`) or a `dup`. stdout is flushed first, so traces appear in order with the program's output.
4. **Make the program observable**: a debugging flag that prints intermediate results (a parsed structure, a row count per step) finds most logic errors faster than any tool.
5. **Shrink the input.** When a large input fails, find the smallest input that still fails (halve it until it passes), and turn it into a test.
6. **`--debug-stack`** prints whatever the program left on the stack at exit, and **`--profile`** shows which words run how often: a count far from what you expect is a bug, not just a hot spot.

## 10. Long-Running Programs

A program that runs for minutes can also run away: an unbounded join, a leak, a loop that never ends.

- **Cap its memory** when you run it: `(ulimit -v 4000000; ./prog ...)` stops it at about 4 GB instead of letting it exhaust the machine.
- **Start small**: run on the first few inputs (a `-n` flag) before the whole data set, and scale up only when the small run is correct and its time and memory look proportionate.
- **Make it report progress** (a line every N items, to stderr) so a stalled or slowing run is visible.
- **Measure memory as resident memory**: `VmHWM` in `/proc/self/status`, or the maximum resident set size from `/usr/bin/time -v`. `VmPeak` counts reserved address space too (every program reserves a 1 GB stack it mostly never touches), so it overstates by about 1 GB.
- **Watch it and stop it early**: if memory keeps growing, progress stops, or the output is already wrong, kill it and fix the cause rather than waiting for it to finish.
