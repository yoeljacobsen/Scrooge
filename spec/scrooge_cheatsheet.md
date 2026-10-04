# Scrooge on one screen (v1.75)

Postfix: every word takes its inputs from the stack and leaves its outputs there, so `3 4 + 2 *` is 14. The spec (`spec/scrooge_spec_v1_75.txt`) is normative; the skill guide (`spec/scrooge_skill.md`) is the method.

**Words.** `#name ( inputs -- outputs ) body end`, every parameter tagged: Scalar (an integer or a float), Block (an immutable array; a string is a Block of character codes), Ptr (heap cells), File, Unknown, or a type the program declares. Inputs are names in the body: `#avg ( s:Scalar n:Scalar -- m:Scalar ) s to_float n / end`. The body must change the stack by outputs minus inputs, which is checked. Top-level code after the words runs the program: `main`.

**Stack and names.** `dup drop swap over rot` exist, but prefer names: `-> [ a b ]` binds the top two values (a is the deeper one) until the end of the block. Every mention of a name pushes it again. `x :name` labels a value with the parameter it is for, checked at the call: `5 :v p :p 0 :i hwrite`. A call with 4 or more inputs must have every argument labelled or passed by a matching name.

| Construct | Stack effect | Notes |
|---|---|---|
| `f cond [ t ] else [ e ]` | ( f -- ... ) | both branches have the same net effect; with no `else`, the true branch is net 0 |
| `f when [ b ]`, `f unless [ b ]` | ( f -- ) | body net 0 |
| `a and_then [ b ]`, `a or_else [ b ]` | ( a -- v ) | short-circuit; the body leaves one value |
| `n [times| i | b ]`, `lo hi [for| i | b ]` | ( n -- ), ( lo hi -- ) | body net 0; carry state on the stack below: `0 10 [times| i | i + ]` leaves 45 |
| `blk [map| i v _ | b ]` | ( blk -- blk' ) | b ( i v -- v' ) |
| `blk [fold| i acc v _ | b from init ]` | ( blk -- acc ) | b ( i acc v -- acc' ) |
| `'w` before a word with a `f:Word(..--..)` input | | compile-time word parameter: `v 'by_age vec_sort_by` |

Other loops are words that call themselves in tail position.

**Numbers.** `+ - * /` (integer `/` truncates; `\` is the remainder), `< > =  !=`, `and or not` (0 is false), `to_float`, `to_int`, `min max abs`. `>=` and `<=` are in `util`.

**Heap.** `n hnew` gives n cells, each the integer 0 (so set a Block field to `nil` in your constructor); `p i hread`; `v p i hwrite` (the value comes first). A range is a start and a count everywhere (`hmove`, `hfill`, `bytes_to_block`), except `block_slice`, which takes start and stop. For numbers or bytes in bulk use a compact array: `n floats_new` (also `ints_`, `bytes_`), `a i floats_get`, `a i x floats_set`. `#record Pt x Scalar 1 y Scalar 1 end` gives `Pt_new`, `p Pt_x`, `v p Pt_x_set`.

**Types of your own.** `#enum Tok num ident op end` gives `Tok_num` .. `Tok_op`, `Tok_name`, `Tok_of` and `Tok_raw`; a Tok compared with a plain number is a TypeError. `#type Row Scalar end` gives `Row_of` and `Row_raw`. `#struct Pt x Scalar y Scalar end` is an immutable value: `1 :x 2 :y Pt_make`, `p Pt_x`, `p 5 Pt_with_x` (a new Pt); `=` and sorting go field by field.

**Library** (`use "name"` at the top of each file that calls it):
- `vec` (`Vec`): `vec_new vec_push vec_get vec_set vec_len vec_pop vec_sort vec_sort_by sort_by`.
- `dict` (`Dict`, integer or string keys): `dict_new dict_set dict_get dict_find dict_get_or dict_has dict_del dict_add`.
- `strings` (`str_print int_to_str str_to_int find_sub`); `file` (`f_read_file f_write_file f_read_line`); `args`; `util` (`assert expect expect_eq`, `>=`); `numeric`.
- `x to_str` gives any value as text; `x trace` prints it to stderr with its line.

**Tests.** A file's `#test_name ( -- ok:Scalar )` words run with `--test FILE`; `expect_eq ( got want label -- ok )` says what differed.

**Tools.**
- `scroogec_fast -L library --lookup NAME [FILE]` (a signature), `--apropos TERMS`, `--explain ErrorClass`, `--stack WORD FILE` (the stack after each line), `--words FILE`.
- Edits, each checked and undone if it breaks the program: `--show NAME FILE`, `--replace NAME FILE < new`, `--replace-all FILE < new`, `--rename OLD NEW MAIN`, `--move NAME FROM TO`.
- `--check-only FILE` checks; `-o prog FILE` builds; `--unchecked-calls FILE` lists calls with unlabelled arguments; `--labels-required N` (default 4, 0 for never).

**Mistakes that cost the most.**
1. A name mentioned once too often, or not at all (ArityMismatch: read the per-line depths, or run `--stack`).
2. Arguments in the wrong order: `v p i hwrite`, not `p i v`. Look the word up, and label them.
3. A code compared with a number: give codes an `#enum`.
4. Large words: keep each word under 30 tokens, with a test.
5. Writing a list, a hash map or a sort yourself: use `vec`, `dict` and `sort_by`.

```scrooge
use "vec"
use "strings"
#enum Shape circle square end
#record Item shape Shape 1 width Scalar 1 end
#item ( s:Shape n:Scalar -- p:Ptr ) Item_new -> [ p ] s p Item_shape_set n p Item_width_set p end
#by_width ( a:Ptr b:Ptr -- f:Scalar ) a Item_width b Item_width < end
#show_item ( p:Ptr -- ) p Item_shape Shape_name str_print 32 print_char p Item_width print_int 10 print_char end
#main ( -- )
  4 vec_new -> [ v ]
  v Shape_square 3 item vec_push
  v Shape_circle 1 item vec_push
  v Shape_square 2 item vec_push
  v 'by_width vec_sort_by
  v vec_len [times| i | v i vec_get show_item ]
end
main
```
prints `circle 1`, `square 2` and `square 3` on three lines.
