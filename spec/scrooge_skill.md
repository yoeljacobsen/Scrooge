# Skill: Writing Correct Scrooge (v1.91)

Operational guide for writing Scrooge that passes static verification and runs right. The specification defines the language; this guide is the method: how to learn it, how to build a program in it, the patterns that work, and how to debug.

---

## 0. How to Learn Scrooge

Learn the language from its documents and from small experiments, in this order:

1. **Start with the cheat sheet** (`spec/scrooge_cheatsheet.md`): the whole language, the library and the tools on one screen, with a program that runs. Keep it open while you write.
2. **Read the specification** (`spec/scrooge_spec_v1_91.txt`) once, end to end. It is short and normative: when this guide and the spec disagree, the spec wins.
3. **Read this guide**, in particular sections 2 to 2c (frames, how stack effects add up, loops): they cover the rules that cost earlier programmers the most rebuilds.
4. **Look every word up before you use it**: `compiler/scroogec_fast -L library --lookup hwrite` prints `hwrite ( p:Ptr i:Int v:Unknown -- )` and what it does. It knows primitives, library words (and the lexicon to `use`), types and constructs (`--lookup fold`), and, given your file as well, your own words. `--apropos sort order` finds words by what they do. The same lines are in `library/manifest.sm` and spec Sec.8, generated from the sources and checked against the compiler. Look before writing a helper: sorting, a growable vector, a hash map, string conversion, argument parsing, bit counts and file reading already exist.
5. **When a build is rejected**, `--explain ArityMismatch` (any class the message names) gives the rule, a wrong example and the corrected one, and `--stack WORD FILE` prints the stack at the end of each line of a word, with names and types: the line where it stops being what you meant is the bug.
6. **Then experiment.** When a rule is unclear, write a 3-line program that tests exactly that question, check it (`--check-only`) and run it. A probe answers in seconds and is always right; reasoning about stack effects in your head often is not.

Learn from the documents and your experiments, not from the compiler's internals: do not read the generated C (`--dump-c`) or the compiler's source to work out what Scrooge means. The documents are meant to be complete; where they are not, a probe program is the right way to find out, and a note in your friction log is the right way to report the gap.

---

## 0b. How to Build a Program

**Design top down.** Before writing code, write the program's structure as a short outline: the main loop, the data it keeps (as `#record` layouts, section 3), and the few words each part needs, with their signatures. A signature is a promise the checker enforces, so choosing them first is most of the design.

**Implement bottom up, in small increments.** Build the lowest layer first (parsing a number, one record accessor, one helper), and make it pass `--check-only` and its `#test_` words (`--test`, section 1) before building on it. Then the next layer, tested the same way. Never write several hundred lines and compile them for the first time together: the first error hides the design problem behind it.

- Test each layer with `#test_` words and `--test` (section 1), and keep them passing as you go.
- Split a large program into user modules (section 6d): one file per layer, each with its own test program.
- While iterating, build with `-O0` (a large program builds in seconds instead of tens of seconds); measure speed only with the default `-O3`.
- Keep a running note of what is done and what is next, so a long task survives an interruption.

---

## 0c. Standard Library Rules

1. **Do not reinvent library words**: check `library/manifest.sm` before writing a helper. Import lexicons with `use "<lexicon>"` (e.g., `use "util"`).
2. **Your own modules**: `use "name"` loads the file "name.sg" from your program's directory when no library lexicon has that name (section 6d).

---

## 1. Decompose into Small Words

**The rule: one word, one step.** Every word does one thing you can name in a few words. Its body is a short sequence of calls with at most one `cond` or one loop, never a branch inside a branch or a loop inside a branch, and it stays under 30 tokens. When a word needs a second level (a `cond` inside a `cond`, a loop inside a branch, a `cond ... else [ cond ...` chain), the inner part becomes a word of its own, named after what it decides or does; a choice among several cases is a sequence of small predicate words (`#is_literal`, `#is_length`) or a table lookup, not a nested cascade. The compiler's `LargeWord` limit (60 tokens or 3 levels) is a backstop, not a target: a word near it is already too big.

Build every program from small words, each doing one job, and combine them into larger ones. A small word is easy to reason about (its stack effect fits in your head), easy to test on its own, and the checker's messages about it point at a line you can see. A word of a hundred tokens is none of these: when it is wrong, you debug the whole of it.

**Two beliefs to drop, both measured false:** (1) "a call to a helper word inside a hot loop costs time, so hot code must be one big word": a call to a small word is compiled in place (a two-read helper in a loop run 20 million times: 25 ms named against 19-21 ms written inline); (2) "a word parameter is an indirect call": it is resolved when the program is compiled, and each word passed makes its own copy of the word that takes it, so there is no call through a value at all. Agents that believed these wrote words of 300 to 550 tokens and kept duplicated loops; neither is needed.

**Small words cost nothing.** A call to a word that does not recurse and is small (at most about 60 tokens, counting the small words it calls in turn) is compiled as that word's body in place: no call, its values stay in registers, and a counted loop that calls it keeps its fast heap access (section 10, `--loops`). So never inline a helper by hand for speed; measure first if in doubt. A recursive word, and every word in a `--profile` build, is a real call.

**Sizes.** Under 30 tokens and one level of nesting (a `cond` or a loop, not a loop inside a cond). `--words FILE` lists every word with its size in tokens, counted exactly as `LargeWord` counts (brackets and `?` are not tokens, a data literal is one). The checker warns (`WARNING LargeWord`) about a word over 60 tokens or with more than 3 nested conds and loops: split it.

**The workflow, a word at a time:**
1. Top down (section 0b): write the list of words with their signatures, from the program's outline down to the smallest steps. The top word should read like the outline: a short sequence of calls.
2. Bottom up: write the lowest word, and next to it (in the same module, or in a test file that `use`s it) a test word, `#test_name ( -- ok:Int )`, that runs it on an input whose answer you worked out by hand.
3. Run the tests: `compiler/scroogec_fast -L library --test src/stats.sg` builds the file with its top-level code replaced by a run of every `#test_` word and prints `PASS`/`FAIL` for each (exit status 1 if any failed). `expect ( ok msg -- ok )`, `expect_eq ( got want msg -- ok )` and `expect_near ( got want tol msg -- ok )` from the util lexicon print what went wrong and return the flag, so several combine with `and`: one `and` after each check but the first, so the test leaves one flag (`test_bits` in section 2d). A word that stops the program on bad input is tested with a test that begins `"msg" expect_stop`: `--test` runs it alone and passes it when the program stops with msg in its error output (`#test_bad ( -- ok:Int ) "not a number" expect_stop "x1" parse_or_die drop 0 end`). A runtime fault (an index out of range, a stale Ptr) exits with status 70, a program's own `abort` or `1 exit` with 1. Under `--test` the program runs with no arguments (`argc` is 1), so test a word that reads options by passing it the arguments as a Block, not through `argv`.
4. Only when the word passes, write the word that uses it, and its test. Keep every test passing as you go.

`examples/colstats/` is a complete program written this way: `examples/colstats/stats.sg` (statistics words with their tests), `examples/colstats/readnums.sg` (reading a file of numbers) and `examples/colstats/colstats.sg` (the top, a sequence of calls).

**A word's inputs are names already.** Use them directly: `#dist2 ( x:Int y:Int -- d:Int ) x sq y sq + end` binds `x` and `y` as if it began with `-> [ x y ]` (spec section 2, Implicit entry frame). Write `-> [ ... ]` yourself only for values computed inside the body, and give inputs names that are not words (an input named like a word that the body calls is an error, `ParamNamedLikeWord`; so is a frame alias named like one of your words, `AliasShadowsWord`).

**Frames are flat.** A frame's body is the rest of the block, never bracketed (spec section 2): `-> [ a b ] a b + -> [ s ] s s *` binds `a b`, then `s`, without nesting either. A `[ ... ]` right after the names is a value: `3 hnew -> [ p ] [ 2 4 7 ]` binds p and pushes the Block [ 2 4 7 ].

**Share a skeleton, not a copy.** When two words differ only in one step (two training loops, a minimum and a maximum), write the shared part once with a word parameter and pass the step: `#_reduce ( p:Ptr n:Int pick:Word(Scalar,Scalar--Scalar) -- x:Scalar ) p 0 hread n [times| i | p i hread pick ] end`, then `#st_min ( p:Ptr n:Int -- x:Int ) 'min _reduce end` (spec section 2, Word parameters). Each use compiles as its own word, so a word parameter costs nothing; the effect of the word passed is checked at the call.

**Private helpers.** In a module, a word whose name starts with `_` (`#_sq_dev`) is visible only in that file, so helpers do not crowd the program's namespace and two modules can each have their own `_step`.

**State travels in records.** When several words need the same five values, keep them in a `#record` and pass it: the getters are small words, so reading a field costs no call. A getter consumes the Ptr like any word taking an input: `tb TB_bcnt` leaves only the field, so a call that needs the record and one of its fields pushes the record twice: `tb tb TB_bcnt tb_apply` (with `tb` a frame name, each mention pushes it again). A field's offset word takes no record: `Tab_cols_off` is the cell where the field starts, so write `Tab_cols_off`, not `t Tab_cols_off`.

**Comments nest, so braces in comment text must pair.** `{ ... }` comments nest (spec section 1), so a lone `}` in the prose (`{ the } ends here }`) closes the comment, and the rest of the line is read as code (as unknown words). Write braces in comment text in pairs, or not at all.

**Recognise a word that is too large:** more than one job in its comment ("reads, parses and sums"), more than about five names in its frames, the same few lines repeated with different fields (make those lines a word taking the field), or a loop body you cannot describe in one sentence (make the body a word).

---

## 2. Name Values with Frames; Avoid Stack Gymnastics

Use names, not stack shufflers (`dup`, `drop`, `swap`, `rot`, `over`, the only five that exist). A word's inputs are names already: write them in the body (`#avg ( s:Int n:Int -- m:Float ) s to_float n to_float / end`) and the word binds them itself, so do not begin a body with `-> [ s n ]`. Name an intermediate result with a frame where it is made: `p n st_mean -> [ m ]`, then use `m` to the end of the block. Names keep their static types; shufflers produce `Unknown`. A frame binds at most 64 names; for more state, use a `#record`.

- **Unbracketed `cond` Conditions**: Write `flag cond [ true_branch ] else [ false_branch ]`. Do NOT place brackets `[` `]` around the condition expression `flag`. When there is nothing to do on the false path, drop the else-branch: `flag cond [ true_branch ]` (the true branch must then have net effect 0). A trailing `?` is optional.
- **Clean Single-Frame Scoping**: In helper words, decompose complex steps into top-level helper words:
  ```scrooge
  #copy_block ( blk:Block -- copy:Block )
    blk [fold| idx acc val _ | acc val cons from nil ] reverse
  end
  ```

---

**Label the arguments whose order is easy to get wrong.** `x :name` after a value says which parameter it is for, and the checker holds you to it: `p :p 0 :i 5 :v hwrite`, `src :src 0 :soff dst :dst 0 :doff n :count hmove`. Labels are optional for short calls. A call with 4 or more inputs must have every argument either labelled or passed by a name equal to the parameter's (a frame name, an input, or a word's declared result name); a parameter whose type no other parameter has (the one Ptr, Bytes, Dict or Float among Ints) needs neither, since a swap there is a TypeError. So `fh p start count fread_into` needs no labels, and `fh p 0 4096 fread_into` needs `0 :start 4096 :count`. In a loop that passes a step word's results back to itself, name the step's results like its inputs: `#step ( i:Int acc:Int -- i:Int acc:Int )`. Then the recursive call `i acc step loop` is checked by name. `--unchecked-calls FILE` lists the calls whose arguments are neither labelled nor named. A swapped pair of names (`b a sub` for `sub ( a b )`) draws the warning ArgumentOrder.

## 2b. How Stack Effects Add Up

The checker counts, for every word, how far each token moves the stack, and rejects a body whose total differs from its signature. These are the rules it applies, which cost earlier agents the most rebuilds:

- **A frame pops.** `-> [ a b ]` takes the top two values off the stack (net -2) and names them. Names stay in scope to the end of the enclosing block, so a later frame binds only NEW values: `-> [ s n ] ... s n foo -> [ r ] ... s n r ...`. Re-listing a name that is still in scope, as in `-> [ s n ] ... -> [ s n r ]`, pops two more values that are not there. Many examples re-push before re-binding (`-> [ a ] a a f -> [ a b ]`); that is one style, not a requirement.
- **`cond` consumes its flag,** and each branch is measured from there. Both branches must have the same net effect: `x 0 < cond [ 0 ] else [ x ]` is +1 either way. A branch without an else must be net 0. A branch whose last call is `abort` or `exit` is exempt. A branch may consume values below it (a word's parameters), but only if the other branch has the same net effect: `cond [ drop ] else [ ]` is rejected (-1 against 0), while `cond [ drop 0 ] else [ ]` is fine (0 and 0).
- **`and`/`or` evaluate both sides.** To guard a test that would fail on bad input, use `and_then`: `b block_len 0 > and_then [ b 0 block_get x = ]` evaluates the access only for a non-empty Block and is 0 otherwise; `a or_else [ b ]` is 1 when a is true and evaluates b only otherwise. Their body leaves exactly one value.
- **`when` / `unless` are statements**: `x 0 < when [ "negative" str_print ]` runs the body when the flag is true (`unless`: when it is false) and leaves nothing; the body's net effect is 0.
- **A fold's `from`** can be any expression leaving one value: `from 0`, `from nil`, or a name in scope (`from acc`).
- **A call has its signature's effect**, a word's call to itself included: in `#count ( n:Int -- )`, the body `-> [ n ] n 0 = cond [ ] else [ n 1 - count ]` is -1 for the frame, then 0 for the cond (its else-branch pushes `n 1 -`, +1, and the call `count` takes it, -1), total -1 as the signature says.
- **Record accessors:** a field with a count above 1 takes an index, `v s i Name_field_set` and `s i Name_field`; a count-1 field does not, `v s Name_field_set` and `s Name_field`.
- When a word is rejected with `ArityMismatch`, the message lists the stack depth at the end of each line of the body, relative to entry: the first line whose depth is not what you intended is where the stray value is.
- **Errors are reported at the call.** When the stack runs out, the message names the call, the inputs it takes and what it found: ``The stack runs out at `pa` (line 6), which takes 3 values ( label:Block v:Int n:Int ) and finds 2 ( v:Int n:Int ): the missing one is the deepest, ( label:Block )``. Push the missing value before the others. A TypeError at a call shows what the callee takes beside what the stack holds (deepest first); "check the order of the arguments" means the right values are there in the wrong order: `5 p 0 hwrite` for `p 0 5 hwrite`. One rule fixes most of these: every word that stores into something (a heap cell, a Block, a collection, a file) takes it first and the value last.

---

## 2c. Counted Loops

For a fixed number of iterations, use a counted loop instead of a helper word:

```scrooge
0 10 [times| i | i + ]                      { sum 0..9: leaves 45 }
s 0 81 [for| c | 0 s c Board_cells_set ]     { clear 81 record cells; net 0 }
9 [times| r | 9 [times| c | r 9 * c + ... ] ]   { nested: the inner body sees r }
```

- `n [times| i | body ]` runs i = 0..n-1 and takes one bound; `lo hi [for| i | body ]` runs i = lo..hi-1 and takes two. A value left below them is not a bound but a carried value: `0 5 [times| ...` with a `[for|` in mind carries the 0.
- The body's net effect is 0. To accumulate, leave the accumulator BELOW the loop and have the body replace it (`acc i +`); several accumulators work the same way (`0 1 20 [times| i | swap over + ]`).
- A frame cannot update a name: `0 -> [ s ] 5 [times| i | s i + -> [ s ] ] s` leaves s at 0, because the inner `-> [ s ]` is a new name for one iteration (the compiler rejects it: `AliasRebindsOuter`). Thread the value on the stack instead: `0 5 [times| i | i + ] -> [ s ]`.
- It is faster than the equivalent tail-recursive word (a plain C loop; carried values stay in registers) and has no depth limit.
- **Stopping early**: `until [ c ]` or `while [ c ]` as the first thing in the body ends the loop before a trip (`0 100 [times| i | until [ dup 20 > ] i + ]`), and `n [find| i | c ]` leaves the first index whose c is true, or -1 (`v vec_len [find| i | v i vec_get k = ]`). Write these instead of a helper word whose only job is to stop a loop.

## 2d. A State Record Threaded Through Small Words

A program with state (a decoder, a parser, a simulation) keeps it in one `#record`, made once, and passes it to every word: one value on the stack instead of many. Each word takes the record first, reads the fields it needs, and sets the fields it changes. A bit reader:

```scrooge
use "util"
#record Rd
  buf Bytes 1 rd_buf
  pos Int 1 0
  bits Int 1 0
  nbits Int 1 0
end
#rd_buf ( -- a:Bytes ) 4 bytes_new end
#rd_byte ( r:Rd -- b:Int )
  r Rd_buf r Rd_pos bytes_get
  r r Rd_pos 1 + Rd_pos_set
end
#rd_bit ( r:Rd -- b:Int )
  r Rd_nbits 0 = when [ r r rd_byte Rd_bits_set r 8 Rd_nbits_set ]
  r Rd_bits 1 bitand
  r r Rd_bits 1 bitshr Rd_bits_set
  r r Rd_nbits 1 - Rd_nbits_set
end
#rd_bits ( r:Rd n:Int -- v:Int )
  0 n [times| i | r rd_bit i bitshl bitor ]
end
#test_bits ( -- ok:Int )
  Rd_new -> [ r ]
  r Rd_buf 0 181 bytes_set
  r 3 rd_bits 5 "low 3 bits of 181" expect_eq
  r 5 rd_bits 22 "high 5 bits" expect_eq and
  r Rd_pos 1 "one byte read" expect_eq and
end
```

- A field word takes the record its field belongs to: `r Rd_pos`, never a record that contains it. Reading a field of a nested record is two calls, `z Z_t T_base`, and a mention of `z` with no call to take it is left on the stack (the ArityMismatch lists it with its line).
- A word that changes the record leaves nothing for it (`rd_bit` gives only the bit): the caller still has `r`.
- A field with a Bytes, Ints, Floats, Vec or Dict takes a word that makes it (`rd_buf`), run once by `Rd_new`; nothing is allocated per call after that, so memory stays bounded.
- Before calling a word of another module, read its signature (`--words MODULE`, or `--show NAME MAIN`): a wrong guess costs a rejected build.

## 3. Choose the Right Access Operation by Structure

- **Sequence (Arrays / Lists / Blocks)**: Integer index $\rightarrow$ `b i block_get` (one spelling since v1.83).
- **Map**: key $\rightarrow$ `map_get` / `dict_get`.
- **Heap Pointer (from `hnew`)**: `hread` / `hwrite`. Never use `block_get` on heap pointers. Pointer arithmetic (`ptr 1 +`) is forbidden; compute integer offsets as Ints.
- **Numeric inner loops are kernels**: `a :a 0 :ao b :b 0 :bo n :n floats_dot`, `y :y 0 :yo x :x 0 :xo n :n g :g floats_axpy` (y += g*x), `floats_add`, `floats_mul`, `floats_scale`, `floats_sum`, `floats_max`, `floats_argmax`, `floats_from_bytes` (pixels to floats), `ints_sum`/`ints_max`/`ints_argmax`, and `bytes_be32`/`bytes_le32`/`bytes_be16`/`bytes_le16` for headers. They are written in C and run several times faster than the same loop in Scrooge (a QMNIST trainer went from 7,900 to 22,000 images/s). The `numeric` lexicon's `vec_*` words do the same on Ptr cells, slower.
- **Large numeric or byte data goes in compact arrays**: `n floats_new`, `n ints_new` and `n bytes_new` store 8, 8 and 1 bytes per element, where a Ptr's cells take 16 each, and the words check every index: `a i floats_get`, `a i x floats_set`, `a 0 :start n :count 0.0 :x floats_fill`, `src :src 0 :soff dst :dst 0 :doff n :count floats_move`, `a 0 n ints_sort`. Stream a file through `bytes_read ( fh a start count -- got )`. A record field may hold one (`grid Floats 1`).
- **Bulk heap work**: `hmove ( src soff dst doff count -- )` copies cells (overlap-safe), `hfill ( p start count v -- )` sets a range, `hsort` sorts one (numbers, or Blocks such as strings and rows, lexicographically; a cell holding a Ptr anywhere inside it, `hnull` included, stops the program, so a NULL marker in rows to be sorted must be a number or a Block). Use them instead of a per-cell loop.
- **An absent link**: `hnull` is a Ptr that refers to nothing (a tree's missing child, an empty list head). Test it with `p hnull =`; reading or writing through it is a fatal error.
- **Memory**: a Block owns the Blocks inside it and frees them with itself, and a heap cell owns what it holds, so nested data costs nothing once released. Bracket per-item work with `region [ ... ]` (an `hmark`/`hrelease` pair) so a long run does not keep every allocation alive. The checker rejects storing something made inside the region into a structure made before it (`RegionEscape`); copy results out as numbers or Blocks, or allocate the structure before the region. A Ptr used after its region is a fatal error that names where it was made and released.
- **Codes get their own type**: a token kind, an opcode or a state is an `#enum`, not a number: `#enum Kw select from where union end` gives `Kw_select` .. `Kw_union` (0 .. 3), `Kw_count`, `Kw_name ( k:Kw -- s:Block )` for messages, and `Kw_of`/`Kw_raw` to convert from and to the number (an enum's `Kw_of` stops on a number that is not a code). Declare record fields and parameters as `Kw`, and the checker rejects comparing a code with a plain number (`t Tk_val Kw_union =`), arithmetic on a code, and a number passed where a code is expected; the SQL runs' worst bug (keyword 118 matching the literal 118) is then a compile error. `#type Name Base end` makes any Int, Float or Ptr its own type the same way (`#type Row Int end`, `Row_of`, `Row_raw`). Both cost nothing at run time. Library handles have types too: `map_make` gives an `IntMap`, so a word that takes a map declares `m:IntMap`, not `m:Ptr`.
- **Rows, keys and small results are `#struct` values**: `#struct Row name Block kind Shape age Int end` gives `Row_make` (label it: `"al" :name Shape_circle :kind 25 :age Row_make`), `r Row_age`, and `r 26 Row_with_age`, a new Row. Structs compare with `=` and sort field by field, so they serve as Dict keys, Vec elements and sort keys, and they never change under you. Use a `#record` only for state that changes in place.
- **Heap state with named fields**: declare it with `#record Name  field Type count init ...  end` (spec Sec.5) instead of hand-numbering offsets. Every field names its initial value (`0`, `nil`, `hnull`, `"root"`, an enum member, or a word such as `mkvec`), and `Name_new` stores it. A record is its own type (`b:Board` in signatures, a Ptr at run time). It generates `Name_new`, `Name_size`, and per field a typed getter `Name_field`, a setter `Name_field_set` that takes the record first and the value last (`s i v`, or `s v` for a count-1 field) and `Name_field_off`, the field's first cell, for bulk words such as `hmove`/`hfill`/`fread_into` that take a raw offset and the Ptr (`b Board_raw`): `#record Board cells Int 81 0 solved Int 1 0 end` then `Board_new -> [ b ] b 0 5 Board_cells_set b 1 Board_solved_set b 0 Board_cells print_int`.
- **File Handle (from `fopen`)**: `fgetc` / `fputc` / `fread` / `fwrite`, or the `file.sg` words below. A `File` is opaque in exactly the way a `Ptr` is: arithmetic on it, `hread`/`hwrite` through it, and `_at`/`_get`/`_set` into it are all static `TypeError`s.
- **Command-Line Argument (from `argv`)**: an ordinary `Block` of character codes -- index it, compare it, print it like any other string. `argc`/`argv` use C's indexing exactly: `0 argv` is the program, the first real argument is `1 argv`.

---

## 4. Block-Building Idioms

- **Sequential `cons` (Order-Preserving)**:
  Consing the values onto `nil` last one first (`nil v1 cons v0 cons`) gives them in order (`[v0, v1]`). Do NOT follow with `reverse`.
  ```scrooge
  { Preserves original order [10, 20] }
  nil 20 cons 10 cons
  ```

- **`fold` Accumulation (Inverting)**:
  Accumulating values during `[fold| ... | acc val cons from nil ]` prepends elements one-by-one, which inherently reverses iteration order. Use a trailing `reverse` step when input order must be preserved:
  ```scrooge
  #copy_block ( blk:Block -- copy:Block )
    blk [fold| idx acc val _ | acc val cons from nil ] reverse
  end
  ```

---

## 5. Numeric Conversions & Arithmetic

- **Two kinds of number (v1.89)**: `Int` (`3`, `-7`, `0xff`, `'a'`) and `Float` (`3.0`, `-0.5`, `314e-2`); a literal with a point or an exponent is a Float. Tag every number in a signature with its kind: indexes, counts, sizes, codes and flags are `Int`, measurements are `Float`. `Scalar` means either kind, for the rare word that takes both (`print_float`, a generic helper); a Scalar cannot be passed where an Int or a Float is asked for.
- **One kind per operation**: `+ - * / min max` and the comparisons take two numbers of one kind. An Int with a Float is a TypeError that says what to write: `x 2 *` for a Float x is `x 2.0 *`, `x 0 >` is `x 0.0 >`, and an Int n used with a Float is `n to_float`. `7 2 /` is the Int 3 and `7.0 2.0 /` the Float 3.5, so the kind of a division is always visible. `\`, the bit words and every index, count and loop bound take Ints.
- **Values of unknown kind**: a heap cell (`hread`) or a Block element (`block_get`) can hold either kind, so the checker lets it through anywhere and the program checks it when it runs; give such values their kind as soon as you can (store numbers in a Floats or Ints array, or declare the word that reads them).
- **Float to integer**: `x to_int` truncates toward zero (`-3.9 to_int` is -3); `x floor` rounds down (`-3.9 floor` is -4), and "x 0.5 + floor" rounds to nearest. **Number to text**: `x 3 float_to_str` is the Block `"3.142"` for 3.14159 (exactly what `3 print_float` prints); `n int_to_str` (strings) for an integer. **Which kind of value**: `v type_of` is 0 for an integer, 1 a float, 2 a Block, 3 a Ptr.
- **Real functions and random numbers**: `exp`, `log` (natural), `sqrt` and `pow` ("2 10 pow" is 1024.0) return floats. `rand` gives a float in [0, 1), and `seed` ( s -- ) fixes the sequence; without a seed call every run gives the same numbers, so seed explicitly and record the seed when results must be reproducible. "rand n to_float * to_int" is an integer in 0..n-1.
- **Converting (`to_float`, `to_int`, `floor`)**: a mean of Ints is a Float, so convert both before dividing:
  ```scrooge
  #avg_calc ( total:Int count:Int -- avg:Float )
    total to_float count to_float /
  end
  ```

---

## 6. Standard Library Highlights

Import library lexicons at the top of the file via `use "<lexicon>"`.

- **Binary formats bit by bit (`bitread.sg`)**: a reader of a file or a Bytes, least significant bit first, the order of DEFLATE, gzip, zlib and PNG. `fh 65536 br_from_file -> [ br ]` (or `a start count br_from_bytes`); `br n br_get` reads n bits (0 to 32) as an Int, the first bit read the lowest; `br n br_peek` and `br n br_drop` for table decoding; `br br_align` skips to a byte boundary; `br dst off count br_bytes` copies whole bytes (a stored block, a trailer) and gives how many it got; `v n br_rev` reverses n bits (a Huffman code is packed from its top bit). Reading past the end gives 0 bits and sets `br br_over`, so check it once after a header or a block and report a truncated input yourself; `br br_at_end` says no bit is left and `br br_pos` how many bytes were consumed. Write a bit reader of your own only for another bit order.

- **Collections first (`vec.sg`, `dict.sg`)**: reach for these before writing a heap layout of your own. Both handles are types of their own (`v:Vec`, `d:Dict`), and every word takes the container first.
  - `Vec`, a growable vector: `8 vec_new -> [ v ]`, `v x vec_push`, `v i vec_get`, `v i x vec_set`, `v vec_len`, `v vec_pop`, `v vec_last`, `v vec_to_block`, `b vec_from_block`. An index outside the Vec stops the program, naming the word.
  - Sorting in your own order: write the order as a small word and pass it. `#by_age ( a:Ptr b:Ptr -- f:Int ) a Person_age b Person_age < end` then `v 'by_age vec_sort_by`, or `p 0 n 'by_age sort_by` for heap cells. The sort is stable, so to sort by two keys, sort by the second key first, then by the first. `v vec_sort` sorts in hsort's order (numbers, then strings and rows element by element).
  - `Dict`, a hash map from integer or string keys: `100 dict_new -> [ d ]`, `d k v dict_set`, `d k dict_get` (stops when absent), `d k dict_find -> [ v found ]`, `d k default dict_get_or`, `d k dict_has`, `d k dict_del`, `d k 1 dict_add` (counting), `d dict_keys`, or every slot with `d dict_cap [times| i | d i dict_slot -> [ k v live ] live when [ ... ] ]`.

- **Numeric kernels (`numeric.sg`)**: a vector is a Ptr, a start cell and a length, so one allocation holds a whole matrix (row r of a c-column matrix starts at `r c *`). `vec_dot ( a ao b bo n -- s )`, `vec_axpy ( y yo x xo n g -- )` (y += g*x, like `floats_axpy`), `vec_add`, `vec_scale`, `vec_sum`, `vec_max`, `vec_argmax`, and `vec_be32` / `vec_le32 ( p off -- n )` for a 32-bit integer in four byte cells after `fread_into` (binary headers).
- **Process figures (`procinfo.sg`)**: `proc_peak_kb ( -- kb )` is the peak resident memory (VmHWM) to report; `proc_rss_kb`, and `proc_status_kb ( key -- kb ok )` for any /proc/self/status field.

- **Signed Integer Formatting (`strings.sg`)**:
  `int_to_str ( n:Int -- str:Block )` converts positive and negative integers to digit character blocks (e.g., `-42` $\rightarrow$ `"-42"` prepended with ASCII `-` / 45).

- **Block Equality & Sorting (`util.sg`)**:
  - `#block_eq ( b1:Block b2:Block -- equal:Int )`: Checks length equality first, then folds element-by-element equality (returns `1` if equal, `0` otherwise).
  - `#block_sort ( blk:Block -- sorted:Block )`: Stable ascending sort, O(n log n) (it uses `hsort`). It sorts numbers, and Blocks lexicographically: a Block of strings sorts in byte order, a Block of rows column by column. For a descending order, `reverse` the result.

- **Safe Indexing (`array.sg`)**:
  - `#nth_or_default ( arr:Block idx:Int default:Unknown -- val:Unknown )`: Returns element at `idx` if within bounds (`0 <= idx < arr block_len`), otherwise returns `default`.

---

**Building text.** Collect output in a string builder rather than consing a Block or printing piece by piece: `256 strbuf_new -> [ b ]`, then `b "x=" strbuf_add`, `b n strbuf_add_int`, `b x 2 strbuf_add_float`, `b 10 strbuf_add_char`, and `f_stdout b strbuf_write drop` or `b strbuf_to_str` at the end (`use "strings"`). `s 8 str_pad_left` and `str_pad_right` pad with spaces, `n int_to_hex` gives hex, `s 44 str_split` splits at commas, and `s 0 s block_len str_to_float` reads a decimal number.

**Printing numbers.** `x 3 print_float` prints a number with 3 decimals. For times kept as integer nanoseconds, `ns 3 print_fixed` prints microseconds (`12345 3 print_fixed` is `12.345`), and `n 5 int_to_str_pad` zero-pads to 5 characters; both are in `strings.sg`. Do not hand-roll these.

## 6b. Sequential File I/O (`file.sg`)

A file is read and written as a Block of character codes -- the same representation `strings.sg` uses -- through an opaque `File` handle. Handles 0/1/2 are pre-opened as stdin/stdout/stderr, so the same words serve the standard streams (`f_stdin`, `f_stdout`, `f_stderr`).

**Reach for the whole-file words first.** They open, transfer and close in one step, and report every failure through an `ok` Int flag:
```scrooge
use "file"
#save_report ( text:Block -- ok:Int )
  "report.txt" text f_write_file
end
```
- `f_read_file ( path:Block -- str:Block ok:Int )` / `f_write_file ( path:Block str:Block -- ok:Int )` / `f_append_file ( path:Block str:Block -- ok:Int )`.

**Open explicitly when one handle serves several operations.** Use the named mode helpers, never a bare mode integer:
- `f_open_read` / `f_open_write` / `f_open_append` `( path:Block -- fh:File ok:Int )`, then `fclose ( fh:File -- ok:Int )`.
- `f_read_all ( fh:File -- str:Block )`, `f_write_line ( fh:File str:Block -- ok:Int )`. A line is `fh freadline` (a Block) or `fh a freadline_into` (into a Bytes, no Block per line); a string is written with `fh s fwrite`.

**Check the flag, always.** Nothing in this lexicon aborts on a missing file, a full handle table or a short write -- it returns `ok=0`, `got=0`, or a written count below `str block_len`. A `cond` on that flag is not optional politeness; skipping it means using a handle that was never opened.

**Choose the granularity deliberately.** `freadline` reads a line in one C pass, and `freadline_into` reads it into a Bytes you reuse. `fh p start count fread_into` reads bytes straight into heap cells, with no Block per character, and `fh p start count fwrite_from` writes cells back as bytes in one call: stream a large file through fixed heap buffers that way (collect output in a buffer and write it when full, rather than one `fputc` per byte). `fread`/`fwrite` move a whole chunk as a Block. `fgetc`/`fputc` move one character and cost a word call plus a `cons` copy each, so use them only where the read must stop at some other delimiter. Never hand-write a per-character loop to do what `f_write_str`, `f_read_line` or `f_read_all` already does. `fseek`/`ftell` reposition a file (not a pipe).

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
#limit ( -- n:Int ) "-n" 1000000 arg_int_or end
#verbose ( -- f:Int ) "-v" arg_flag end
#input_path ( -- p:Block ) "-f" "data.csv" arg_value_or end
```

**Iterate with `arg_tail`.** It gives the arguments *without* the program name, as a `Block` of `Block`s -- the shape a `[fold| ... ]` wants. It is also the only word here that materializes every argument, so ask for one argument by index when that is all you need.

**Scan flags with `arg_find`.** `"-v" arg_find` answers "was `-v` passed, and at which index", using the same found-flag convention as `find_sub`. The search starts at index 1, so the program name can never match.

**Distinguish absent from empty.** `argv` reports a missing index as `ok=0`, but an argument that was supplied and is empty (`prog ""`) is `ok=1` with an empty `Block`. Do not treat length 0 as "not given".

**Default paths under the home directory.** `"~/Data/x.csv" f_expand_home` (file.sg) gives the path the shell would; `"HOME" getenv` reads a variable directly. Never hard-code a user's home directory.

**Read `examples/args_demo.sg`** for the whole shape of a command-line program: flags separated from operands, the program named in a diagnostic, and standard input used when no operands were given.

---

## 6d. Your Own Modules

A program of more than a few hundred lines belongs in several files. Each module `use`s the lexicons and modules it calls: a whole-program build also finds a lexicon that only another module imports, but `--check-only` or `--test` on that module alone rejects the call. `use "geo"` loads the file "geo.sg" from the directory of the file that says it (when no library lexicon is called `geo`), and a relative path works too, so a test in `t/` can say `use "../src/geo"`; a module is ordinary Scrooge (word definitions and its own `use` lines), modules may use each other, and each is loaded once. Errors, warnings, runtime word chains and `trace` name the module and its own line: `REJECT UnknownWordError geo.sg line 2 ...`. Give each module a test program that `use`s it.

---

## 7. Failure Checklist (Check Before Emitting Code)

1. **Reserved Words**: Never use reserved words as parameter names or frame aliases (`use`, `lexicon`, `from`, `and`, `or`, `not`, `cond`, `else`, `map`, `fold`, `select`, `nil`, `cons`, `pair`, `end`, `dup`, `drop`, `swap`, `rot`, `over`, `block_len`, `seed`, `rand`, `exp`, `log`, `pow`, `sqrt`, `floor`, `abs`, `max`, `min`, `to_float`, `bitand`, `bitor`, `bitxor`, `bitshl`, `bitshr`, `bitnot`, `hnew`, `hread`, `hwrite`, `print_char`, `print_int`, `abort`, `hmark`, `hrelease`, `fopen`, `fclose`, `fgetc`, `fputc`, `fread`, `fwrite`, `argc`, `argv`, `clock_ns`, `block_slice`, `bitcount`, `bitctz`, `bitclz`, `hsort`, `print_float`, `getenv`, `freadline`, `fread_into`, `fseek`, `ftell`, `trace`, `hmove`, `hfill`, `exit`, `to_int`, `float_to_str`, `type_of`, `hnull`, `when`, `unless`, `and_then`, `or_else`, `sort_cmp`, `fwrite_from`, `fflush`, `to_str`, `bytes_new`, `bytes_len`, `bytes_get`, `bytes_set`, `bytes_fill`, `bytes_move`, `ints_new`, `ints_len`, `ints_get`, `ints_set`, `ints_fill`, `ints_move`, `floats_new`, `floats_len`, `floats_get`, `floats_set`, `floats_fill`, `floats_move`, `bytes_read`, `bytes_write`, `bytes_to_block`, `bytes_from_block`, `ints_sort`, `floats_sort`, `floats_dot`, `floats_axpy`, `floats_add`, `floats_mul`, `floats_scale`, `floats_sum`, `floats_max`, `floats_argmax`, `floats_from_bytes`, `ints_sum`, `ints_max`, `ints_argmax`, `bytes_be32`, `bytes_le32`, `bytes_be16`, `bytes_le16`, `until`, `while`, `region`, `str_to_float`, `freadline_into`). This is the list in spec Sec.10.
2. **Lexicon Shadowing**: Never define a `#word` that shadows a `use`-imported word or standard primitive; the error names what it collides with.
3. **Unbracketed `cond` Condition**: Ensure `cond` condition is unbracketed expression (`flag cond [ ... ] else [ ... ]`).
4. **Only Five Stack Shufflers**: `dup`, `drop`, `swap`, `rot`, `over`. There is no `pk`, `roll` or `nip`: each is an `UnknownWordError` (`pk` and `roll` are reserved for a possible future implementation). When a value is needed deeper than `over` reaches, bind it with a frame.
5. **Bracketed Values Are Data**: a `[ ... ]` used as a value may hold only literals (`[ 1 [ 2 3 ] ]`); build a Block from computed values with `cons` or `pair`. Cond branches, frame bodies and loop bodies are not values and nest freely.
6. **Correct Access Operator**: `block_get` for a Block, `hread` for a heap Ptr, a record's getters for a record, `fgetc`/`fread` for a file.
7. **Stack effects add up** (section 2b): every `cond` branch has the same net effect, a second frame pops new values, and a count-1 record setter takes no index.
8. **Arithmetic edge cases**: integer `/` rounds down and `\` is the matching remainder (the sign of the divisor), so `a = b*(a/b) + a\b` for every sign (`-7 2 /` is -4); integer overflow wraps; `<`/`>` compare numbers only; `a b sort_cmp` is -1, 0 or 1 for two strings (byte order) or rows. A `Ptr` used after the `hrelease` of its region stops the program with a message saying so.
9. **Do not name an alias after one of your words**: `-> [ tbl_name ]` would hide `#tbl_name` until the end of the block, so it is an error (`AliasShadowsWord`). Likewise `%` is not modulo (use `\`), and `&&`/`||` do not exist.
10. **Frame Scope Runs to the End of the Block**: in `-> [ x ] A B`, `B` still sees `x`. A cond branch does not extend that way: an `else` written after a branch's `]` cannot reach a cond inside it.

---

## 8. Checking, Building and Running

From the repository root:
```bash
compiler/scroogec_fast -L library --check-only prog.sg   # ACCEPT, or every error found
compiler/scroogec_fast -L library -O0 -o prog prog.sg     # fast build while developing
compiler/scroogec_fast -L library -o prog prog.sg         # optimised build (-O3)
compiler/scroogec_fast -L library --test src/stats.sg      # run the file's #test_ words (section 1); --test-timeout N (default 600 s)
compiler/scroogec_fast --words src/stats.sg                # every word, its lines and size in tokens
compiler/scroogec_fast -L library --lookup vec_push        # a word's signature and description (add FILE for your own words)
compiler/scroogec_fast -L library --apropos hash string    # words whose name or description has every term
compiler/scroogec_fast --explain TypeError                 # an error class: the rule, a wrong and a corrected example
compiler/scroogec_fast -L library --stack st_var src/stats.sg   # the stack at the end of each line of one word
```

- The compiler exits 0 on ACCEPT and 1 on REJECT, and a rejected build removes any older binary at the `-o` path, so `build && ./prog` never runs a stale program.
- Warnings go to stderr after `ACCEPT`: `MutualRecursion` (words calling each other in tail position where one takes no inputs, so the cycle cannot run as a loop and stops at 65,536 trips; words that pass their state as inputs run as a loop), and `LargeWord` (a word to split, section 1). Take them seriously.
- `exit ( code -- )` ends a program with a status of your choosing.
- For a final speed measurement of a program that already runs correctly, `--no-ptr-check` leaves out the stale-Ptr check (about 7% in heap-read-heavy code). Develop and test with the check on.

**Find where the time goes with `--profile`**, not by guessing (a `--profile` build compiles every call as a real call, so small words show up in the table): `compiler/scroogec_fast --profile -L library -o prog prog.sg` builds a program that prints, at exit, each word's calls, self time and total time to stderr. Its own output is unchanged. Each timed call adds about 10 ns, so read the call counts as well as the times: a tiny word called 100 million times is the place to restructure.

## 8b. Editing Scrooge Source

The compiler edits source a whole word at a time, so you never need a script that searches for and replaces a snippet of text (which breaks on any difference in indentation). It finds definitions with the compiler's own rules, so `end` or `#name` inside a string or a `{ }` comment is never mistaken for code. Reading is `--words` and `--show`; every change to a word is one command, `--edit FILE`, where FILE is the file you are working on: a module you are building and testing on its own, or the main program (since v1.85). The everyday edit is one definition on stdin, which replaces the word of that name (or adds it if it is new):

```bash
compiler/scroogec_fast --words src/token.sg            # every definition: name, signature, lines
compiler/scroogec_fast --show tok_kind src/token.sg    # print one definition, with its comment
compiler/scroogec_fast -L library --edit src/token.sg <<'EOF'
#tok_kind ( c:Int -- k:TokKind ) c is_digit cond [ TokKind_num ] else [ TokKind_word ] ? end
EOF
compiler/scroogec_fast --fmt src/token.sg              # re-indent (two spaces per bracket level)
```

The edit is checked: if FILE (with the modules it loads) compiled before and would not after, nothing is written and the errors are printed. Create a new file with your file tool; change the words in it with `--edit`. Several changes can go in one edit script, a list of steps applied in order to FILE and every module it loads:

```
{ checked: rows with fewer fields are skipped }
#parse_row ( line:Block -- row:Row ok:Int ) ... end
#row_width ( r:Row -- n:Int ) ... end
rename parse_row read_row
delete old_reader
move read_row rows.sg
into rows.sg
#row_valid ( r:Row -- f:Int ) ... end
```

- A definition (`#name ... end`, with the comment above it if any) replaces the word of that name wherever it is, or is added at the end of FILE, or of the file named by the last `into FILE`.
- `delete NAME` removes a word and its comment. `rename OLD NEW` renames the definition, every call and every `'OLD` reference in the program and its modules, but not strings or comments; a private `_word` only in its own module. It refuses a NEW that is already defined or reserved, and an OLD that is also a local name somewhere. `move NAME MODULE` moves a word to the module next to FILE, adds the `use` lines it needs there and `use "FILE"` where it is still called; it refuses while the word calls words that stay behind, so move those first (in the same script).
- A step line starts at column 0; everything else is definition text, checked before anything is written (balanced brackets, every definition ended, the parser accepts it).
- A word's comment is the run of comment lines directly above its `#name` line, with no blank line between: `--show` prints it, `delete` removes it, and a replacement replaces it when the new text brings its own, and keeps it otherwise.
- **The whole script is one checked edit.** The compiler writes the files, checks FILE, and if FILE was accepted before and would now be rejected, it restores every file and prints the errors, so a bad edit never reaches the disk. `--no-check` skips the check. The message lists the steps and ends with `checked: src/token.sg: ACCEPT`.
- To change a few lines inside a long word, `--show` it, edit the text, and give it back to `--edit FILE` on stdin.
- `--fmt` changes only leading whitespace, never the code or the line count, and `--fmt --check` reports whether a file is already formatted.

## 9. Debugging a Program That Runs Wrong

Work from cheapest to most detailed, and stay in Scrooge:

1. **`assert` your invariants** (`use "util"`): `count 81 <= "count past the grid" assert` stops the program with that message the first time the invariant fails, instead of minutes later with a corrupted result.
2. **Read the word chain.** A runtime `Fatal:` error is followed by the words that were running, innermost first, each with its definition line (`in #report (defined line 2)`); start there.
3. **`to_str` any value** for a message or a test: `x to_str str_print` writes numbers, floats (`3.0`), nested Blocks and strings (`[ 104 105 ] { "hi" }`) whole, as Scrooge text.
4. **`trace` a value**: `x trace` prints `trace line N: <value>` to stderr, for any type: numbers, Blocks (the first 64 elements, and as text when they are all printable characters), and a Ptr as its size. It consumes the value, so trace a frame-bound name (`-> [ x ] x trace ... x ...`) or a `dup`. stdout is flushed first, so traces appear in order with the program's output.
5. **Make the program observable**: a debugging flag that prints intermediate results (a parsed structure, a row count per step) finds most logic errors faster than any tool.
6. **Shrink the input.** When a large input fails, find the smallest input that still fails (halve it until it passes), and turn it into a test.
7. **`--debug-stack`** prints whatever the program left on the stack at exit, and **`--profile`** shows which words run how often: a count far from what you expect is a bug, not just a hot spot.

## 10. Long-Running Programs

A program that runs for minutes can also run away: an unbounded join, a leak, a loop that never ends.

- **Cap its memory** when you run it: `(ulimit -v 4000000; ./prog ...)` stops it at about 4 GB instead of letting it exhaust the machine.
- **Start small**: run on the first few inputs (a `-n` flag) before the whole data set, and scale up only when the small run is correct and its time and memory look proportionate.
- **Make it report progress** (a line every N items) so a stalled or slowing run is visible: write it to stderr (`f_stderr`, unbuffered), or to stdout followed by `f_stdout fflush drop`, since redirected stdout is buffered and would show nothing until the buffer fills.
- **Measure memory as resident memory**: `VmHWM` in `/proc/self/status` (`proc_peak_kb` in the procinfo lexicon), or the maximum resident set size from `/usr/bin/time -v`. `VmPeak` counts reserved address space too (every program reserves a 1 GB stack it mostly never touches), so it overstates by about 1 GB.
- **Watch it and stop it early**: if memory keeps growing, progress stops, or the output is already wrong, kill it and fix the cause rather than waiting for it to finish.

Speed and size in numeric code:

- **Every heap cell takes 16 bytes**, whatever it holds (a byte, an integer, a float). A million-byte file read into cells takes 16 MB; when that matters, pack several small values into one integer cell with `bitshl`/`bitor` and take them apart with `bitshr`/`bitand`.
- **Name the operands of a non-commutative update.** In a line with more than two intermediate values, a `-` or `/` applied in the wrong order is accepted and runs (`lr v * w -` is lr*v - w, not w - lr*v): bind the values with a frame first (`-> [ w g ] w lr g * -`), and test a numeric kernel on inputs whose answer you know, or against a second, simpler implementation of the same computation.
- **A counted loop keeps fast heap access when its body calls only small words.** A `[times| ]` or `[for| ]` loop whose body calls no word, or only small non-recursive words (they are compiled in place, section 1), and no `hrelease`, checks each heap address once, before the loop; each `hread`/`hwrite` through a variable from outside the loop then costs one bounds check (measured on three numeric programs: 20-35% faster than when every access re-checked its address). A call to a recursive or large word in the body turns this off for that loop; build with `--loops` to see, for every counted loop, whether it has fast access and, if not, which call prevents it. So split a loop body into small words freely.
- **A value read once and reused in a hot loop is faster after `to_float`** (or `to_int`, for an integer): `c 0 hread to_float -> [ g ]` before a loop that multiplies by `g` on every iteration. The generated code then knows g's kind and drops the checks it would otherwise repeat each time round (measured: a multiply-add loop 30% faster). Values read inside the loop gain little from it.
