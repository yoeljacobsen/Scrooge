# Scrooge on one screen (v1.95)

Postfix: every word takes its inputs from the stack and leaves its outputs there, so `3 4 + 2 *` is 14. The spec (`spec/scrooge_spec_v1_95.txt`) is normative; the skill guide (`spec/scrooge_skill.md`) is the method.

**Words.** `#name ( inputs -- outputs ) body end`, every parameter tagged: Int, Float, Scalar (either kind of number), Block (an immutable array; a string is a Block of character codes), Ptr (heap cells), File, Unknown, or a type the program declares. Inputs are names in the body: `#avg ( total:Int count:Int -- mean:Float ) total to_float count to_float / end`. Name each parameter for what it is, as the primitives and the library do (`vec_set ( vec index value )`): labels, frame names and ArgumentOrder are checked against these names. The body must change the stack by outputs minus inputs, which is checked. Top-level code after the words runs the program: `main`.

**Stack and names.** `dup drop swap over rot` exist, but prefer names: `-> [ a b ]` binds the top two values (a is the deeper one) until the end of the block. Every mention of a name pushes it again. A name is never also a word: an alias or input spelled like one of your words is an error (AliasShadowsWord, ParamNamedLikeWord). `x :name` labels a value with the parameter it is for, checked at the call: `p :p 0 :i 5 :v hwrite`; a label does not name the value (to use it again, `-> [ h ]`). A call with 4 or more inputs must have every argument labelled or passed by a matching name, except one whose type no other parameter has (the one Ptr or Float among Ints).

| Construct | Stack effect | Notes |
|---|---|---|
| `f cond [ t ] else [ e ]` | ( f -- ... ) | the only branch (there is no `if`); both branches have the same net effect; with no `else`, the true branch is net 0 |
| `f when [ b ]`, `f unless [ b ]` | ( f -- ) | body net 0 |
| `a and_then [ b ]`, `a or_else [ b ]` | ( a -- v ) | short-circuit; the body leaves one value |
| `n [times| i | b ]`, `lo hi [for| i | b ]` | ( n -- ), ( lo hi -- ) | body net 0; carry state on the stack below: `0 10 [times| i | i + ]` leaves 45; `until [ c ]` / `while [ c ]` first in the body stops it |
| `n [find| i | c ]` | ( n -- i ) | the first i whose c is true, or -1 |
| `blk [map| i v _ | b ]` | ( blk -- blk' ) | b ( i v -- v' ) |
| `blk [fold| i acc v _ | b from init ]` | ( blk -- acc ) | b ( i acc v -- acc' ) |
| `'w` before a word with a `f:Word(..--..)` input | | compile-time word parameter: `v 'by_age vec_sort_by` |

Other loops are words that call themselves in tail position.

**Numbers.** `3` is an Int and `3.0` a Float. `+ - * / min max` and `< > >= <= = !=` take two numbers of one kind: `x 2.0 *` and `x 0.0 >` for a Float x, and an Int with a Float is a TypeError; convert with `to_float`, `to_int` or `floor`. Indexes, counts, loop bounds, flags (`and or not`, 0 is false), `\` and the bit words are Ints; a shift takes the value, then the count: `1 k bitshl` is 2^k (`k 1 bitshl` is 2k). Int `/` and `\` round down: `-7 2 /` is -4, `-7 2 \` is 1; `7.0 2.0 /` is 3.5. `'a'` is the Int 97 (`'\n'` 10). Print a Float with decimals: `x 2 print_float`, or `x 2 float_to_str`.

**Heap.** `n hnew` gives n cells, each the integer 0; `p i hread`; `p i v hwrite`. `region [ body ]` frees everything the body allocated when it ends; storing it into something older is a RegionEscape error. Every word that stores into something takes it first and the value last: `p i v hwrite`, `b x cons`, `fh ch fputc`, `d k v dict_set`. A range is a start and a count everywhere (`hmove`, `hfill`, `bytes_to_block`, `block_slice`). For numbers or bytes in bulk use a compact array: `n floats_new` (also `ints_`, `bytes_`), `a i floats_get`, `a i x floats_set`. Inner loops: `floats_dot`, `floats_axpy`, `floats_sum`, `floats_argmax` and the rest (in C). `#record Pt x Float 1 0.0 y Float 1 0.0 end` (each field: name, type, count, initial value: a number, `nil` for a Block, `hnull`, an enum member, or a word that makes a Floats, Vec or Dict) gives the type `Pt`, `Pt_new`, `p Pt_x`, `p v Pt_x_set` (record first); a field word takes the record, so read-modify-write names it twice: `p p Pt_x 1.0 + Pt_x_set`.

**Types of your own.** `#enum Tok num ident op end` gives `Tok_num` .. `Tok_op` (members are always prefixed), `Tok_name`, `Tok_count`, `Tok_of` and `Tok_raw` (so no member may be named `name`, `count`, `of` or `raw`); a Tok compared with a plain number is a TypeError. `#type Row Int end` gives `Row_of` and `Row_raw`. `#struct Pt x Int y Int end` is an immutable value: `1 :x 2 :y Pt_make`, `p Pt_x`, `p 5 Pt_with_x` (a new Pt); `=` and sorting go field by field.

**Library** (`use "name"` at the top of each file that calls it):
- `vec` (`Vec`): `vec_new vec_push vec_get vec_set vec_len vec_pop vec_sort vec_sort_by sort_by`.
- `dict` (`Dict`, integer or string keys): `dict_new dict_set dict_get dict_find dict_get_or dict_has dict_del dict_add`.
- `strings` (`str_print int_to_str str_to_int find_sub str_split str_pad_left`, and the builder `n strbuf_new`, `b s strbuf_add`, `b strbuf_to_str`); `file` (`f_read_file f_write_file`); `args`; `util` (`assert expect expect_eq`); `numeric`; `bitread` (bits of a file or Bytes, LSB first: `fh 65536 br_from_file`, `br n br_get`, `br br_align`, `br dst off n br_bytes`). Lines: `fh freadline`, or `fh a freadline_into` into a Bytes.
- `x to_str` gives any value as text; `x trace` prints it to stderr with its line. Which words for which job (a file as a stream, bits, a list, a table, arguments, stopping with a message): skill guide section 0d. A whole program in modules with tests: `examples/wavstat/`.

**Tests.** A file's `#test_name ( -- ok:Int )` words run with `--test FILE`; `expect_eq ( got want label -- ok )` says what differed, and several checks end in one flag: `a 1 "a" expect_eq b 2 "b" expect_eq and`. A test whose code must stop the program begins `"msg" expect_stop` and passes when it stops with msg on stderr. A runtime fault exits with status 70; `abort` and `1 exit` with 1.

**Tools.**
- `scroogec_fast -L library --lookup NAME [FILE]` (a signature), `--apropos TERMS`, `--explain ErrorClass`, `--stack WORD FILE` (the stack after each line), `--words FILE...`; `--profile` builds a program that prints the time per word.
- Before calling into another module, read its signatures with `--words MODULE`. Read with `--words FILE` and `--show NAME FILE`; change a word with `--edit FILE` and its new definition on stdin (FILE: the module you are working on), checked and undone if it breaks FILE; one edit may also `delete NAME`, `rename OLD NEW`, `move NAME MODULE`. `--test --deep MAIN` runs every module's tests.
- `--check-only FILE...` checks each file; `-o prog FILE` builds; `--unchecked-calls FILE` lists calls with unlabelled arguments; `--labels-required N` (default 4, 0 for never).

**Mistakes that cost the most.**
1. A name mentioned once too often, or not at all (ArityMismatch: read the per-line depths and the values left with their lines, or run `--stack`). A value left before `[times|` (one bound) or `[for|` (two) is carried through the loop, not a bound.
2. Arguments in the wrong order. The container (cell, Block, collection, file) comes first and the value last, in every word. Look the word up, and label them.
3. A code compared with a number: give codes an `#enum`.
4. Large words. One word, one step: under 30 tokens and at most one `cond` or loop; a branch inside a branch is a word of its own, named after what it decides. Each word gets a test.
5. Writing a list, a hash map or a sort yourself: use `vec`, `dict` and `sort_by`.
6. Progress that never appears: stdout is block-buffered when redirected to a file. Print progress to `f_stderr`, or follow it with `f_stdout fflush drop`.
7. Memory that only grows: heap cells, compact arrays, records, Vec and Dict are not collected. Allocate working arrays once (record fields) and pass them in, or put `region [ ... ]` around each unit of work (a block, a query, a file); everything it allocated is freed at its end. The compiler warns `AllocInLoop` when a loop allocates.
8. A field word takes its record: `st St_pos` leaves only the field, so `st St_pos n step` with `step ( st pos n )` is one value short. Push the record once for each word that takes it: `st st St_pos n step`.

```scrooge
use "vec"
use "strings"
#enum Shape circle square end
#record Item shape Shape 1 Shape_circle width Int 1 0 end
#make_item ( shape:Shape width:Int -- item:Item ) Item_new -> [ item ] item shape Item_shape_set item width Item_width_set item end
#by_width ( left:Item right:Item -- flag:Int ) left Item_width right Item_width < end
#show_item ( item:Item -- ) item Item_shape Shape_name str_print 32 print_char item Item_width print_int 10 print_char end
#main ( -- )
  4 vec_new -> [ v ]
  v Shape_square 3 make_item vec_push
  v Shape_circle 1 make_item vec_push
  v Shape_square 2 make_item vec_push
  v 'by_width vec_sort_by
  v vec_len [times| i | v i vec_get show_item ]
end
main
```
prints `circle 1`, `square 2` and `square 3` on three lines.
