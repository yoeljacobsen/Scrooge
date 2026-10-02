# Scrooge Programming Language (v1.74)

Repository status: **Scrooge v1.74**.

### What changed in v1.74

Refactoring that cannot leave a program worse. The language is unchanged.

- **Every edit is checked.** `--replace`, `--insert-before`, `--insert-after` and `--delete`, and the new commands below, check the result.
  - What is checked: the edited files, or the whole program with `--program main.sg`.
  - If a file that was accepted would now be rejected, every file is restored and the errors are printed.
  - `--no-check` turns this off.
- **`--replace-all FILE`** replaces, or adds, several words given on stdin, as one edit.
- **`--rename OLD NEW MAIN`** renames a word's definition, its calls and its `'OLD` references across the program and its modules. Strings and comments are left alone, and a private `_word` is renamed only in its own module. It refuses a name that is taken or reserved, and a name that is also a local name somewhere.
- **`--move NAME FROM TO`** moves a word into a module. It adds the `use` lines the word needs, makes FROM `use` TO when FROM still calls the word, and refuses while the word's callees stay behind.

### What changed in v1.73

Records as values. Every program in this project's corpus that compiled under v1.72 still compiles, with the same output. A word named `struct` is still a word.

- **`#struct Pt x Scalar y Scalar end`** declares an immutable value of its own type, stored as a Block at run time.
  - It generates `Pt_make`, whose inputs are the field names, so a call can be labelled: `1 :x 2 :y Pt_make`.
  - Each field gets a getter (`p Pt_x`) and an update that returns a new value and leaves the old one as it was (`p 5 Pt_with_x`).
  - `=` and sorting compare field by field, `to_str` writes the whole value, and a struct can be a `Dict` key.
  - A `#record` remains the mutable heap layout.
- **`dict` keys** may now be any Block: a key's nested strings and floats are hashed too.
- **Labels:** a word's declared result name counts as a check when it matches, and no longer draws a false `ArgumentOrder` warning when it does not.

### What changed in v1.72

Compact arrays. The new primitive names are reserved, so a word or frame of the same name is now rejected; no program in the corpus had one. Apart from that, every program in this project's corpus that compiled under v1.71 still compiles, with the same output.

- **Three new types: `Bytes`, `Ints` and `Floats`.** Each is an array of raw elements: 1, 8 and 8 bytes each, where a heap cell takes 16.
  - Words for each kind: `_new`, `_len`, `_get`, `_set`, `_fill` and `_move` (`n floats_new`, `a i floats_get`, `a i x floats_set`).
  - More words: `bytes_read` and `bytes_write` for streaming a file, `bytes_to_block` and `bytes_from_block`, and `ints_sort` and `floats_sort`.
  - Every index and value is checked, and an error names the word.
  - In a counted loop, access is hoisted as `hread` is, and is faster than `hread`.
- **Labels:** an argument whose parameter type no other parameter of the call has (the one Ptr, Bytes or Dict among Scalars) needs no label, because a swap there is a TypeError already.

### What changed in v1.71

Argument labels, against arguments that type-check but are in the wrong order. **This release breaks code:** a call with 4 or more inputs must now name every argument (`--labels-required 0` turns that off).

- **`x :name`** after a value says which parameter it is for: `5 :v p :p 0 :i hwrite`. The checker compares it with the callee's parameter names, and nothing is reordered.
  - Labels are optional and may be partial, and they cost nothing at run time.
  - A label that names another parameter is an `ArgumentLabel` error, which shows what the word takes beside what was passed.
- **Names count as labels.** An argument passed by a frame name, an input name or a word's declared result name equal to the parameter's name is checked without a label: `fh p start count fread_into`.
  - Name a step word's results like its inputs, and the loop's recursive call is checked too.
  - Names in each other's places (`b a sub` for `sub ( a b )`) draw the warning `ArgumentOrder`.
- **`--labels-required N`** (default 4): a call with N or more inputs must have every argument labelled or passed by a matching name. 0 makes labels optional everywhere.
- **`--unchecked-calls FILE`** lists the calls whose arguments are neither labelled nor named.
- **The library, the examples and the documents conform.** Step words in the library now name their results like their inputs (`val2:Scalar` became `val:Scalar`).

### What changed in v1.70

Documents to learn from. Every program in this project's corpus that compiled under v1.69 still compiles, with the same output.

- **`spec/scrooge_cheatsheet.md`** is the language, the library and the tools on one screen, ending with a program that runs (a gate builds it). Read it first.
- **Implicit entry frames everywhere.** The library, the examples and the code in the spec and the skill guide now let a word's inputs bind themselves (`#avg ( s:Scalar n:Scalar -- m:Scalar ) s to_float n / end`). They no longer begin bodies with `-> [ s n ] [ ... ]`, which earlier runs copied into 98 of 141 words.
  - The rewrite was mechanical, and the generated C differs only in line numbers.
  - A gate keeps the old style from coming back.
- **A `#record` field named `size` or `new`** is now rejected with a message that names the clash with the record's own `_size`/`_new` word. Before, it was a confusing DuplicateWordError.

### What changed in v1.69

Looking things up, instead of probing. In earlier runs, about half of all compiler calls were probe programs.

- **`--lookup NAME [FILE]`** shows a name's signature and description. It knows primitives, library words (and the lexicon to `use`), a lexicon's types (with the words that take them), constructs (`--lookup fold`), and, given your file, your own words with their comments, plus the words a declaration generates. A name it does not know gets a list of similar names.
- **`--apropos TERMS...`** lists every word whose name or description contains all the terms.
- **`--explain CLASS`** gives the rule behind an error or warning class, with a wrong example and the corrected one. A gate compiles every example, so they stay true. A rejection now ends with a pointer to it.
- **`--stack WORD FILE`** prints the stack at the end of each line of a word: names and types, the depth relative to the entry, and what each frame binds.
- **An input named like a primitive or reserved word** that the body mentions (`#f ( len:Scalar -- ) len print_int end`) is now a ReservedWordIdentifierError. The mention was the primitive, not the input.

### What changed in v1.68

Batteries: a growable vector, a hash map, sorting with your own order, and text for any value. A word or frame name `to_str` is now rejected, because `to_str` is a new primitive. Apart from that, every program in this project's corpus that compiled under v1.67 still compiles, with the same output.

- **`to_str ( v -- s )`** writes any value as text: `42`, `3.0`, `[ 1 [ 2 3 ] ]`, `[ 104 105 ] { "hi" }` and `Ptr#3(10 cells)`. Use it for messages and tests.
- **`use "vec"`** adds `Vec`, a growable vector of any values. It is its own type, every word takes the container first, and indexes are checked.
  - Words: `vec_new`, `vec_push`, `vec_get`, `vec_set`, `vec_len`, `vec_pop`, `vec_last`, `vec_clear`, `vec_reserve`, `vec_data`, `vec_from_block`, `vec_to_block`, `vec_sort`.
  - Sorting with a word you pass: `v 'by_age vec_sort_by`, and `p off n 'by_age sort_by` for heap cells. Both are stable merge sorts; the comparator word is compiled into the loop.
- **`use "dict"`** adds `Dict`, a hash map from integer or string keys to any values: `dict_new`, `dict_set`, `dict_get`, `dict_find`, `dict_get_or`, `dict_has`, `dict_del`, `dict_add`, `dict_len`, `dict_keys`, and `dict_slot` for visiting every entry.
- **Library words can take word parameters.** The checker reads their bodies from the lexicon. A message about an instance names the lexicon file and its line.

### What changed in v1.67

Library lexicons can declare types. Every program in this project's corpus that compiled under v1.66 still compiles, with the same output.

- **A lexicon's `#type` and `#enum`** reach every program that uses the lexicon. Such a program can name the types in its own signatures and record fields, but cannot declare a type of the same name.
  - If a type is used without its `use` line, the error names the lexicon to add.
  - `library/manifest.sm` and spec section 8 list each lexicon's types and the words they generate. The manifest generator gets them from the compiler, with the new `scroogec_fast --declarations FILE`.
- **`map`'s handle is now an `IntMap`.** This change can break code: a word that takes a map must declare `m:IntMap`, not `m:Ptr`. A map passed where a Ptr or a list is expected, or the reverse, is a TypeError. The message says to declare the type where the value comes from.
- **`--words`** shows `#type` and `#enum` declarations and the words they generate.

### What changed in v1.66

Distinct types and enums, so that a code is not a number. This change only adds: every program that compiled under v1.65 still compiles, with the same output (a word named `type` or `enum` is still a word).

- **`#enum Kw select from where union end`** declares the type `Kw` and generates:
  - a word for each member, `Kw_select` .. `Kw_union`, giving the codes 0 .. 3;
  - `Kw_count`;
  - `Kw_name ( k:Kw -- s:Block )`, the member's name, for messages;
  - `Kw_of` and `Kw_raw`, to convert from and to the number. An enum's `Kw_of` stops on a number that is not one of its codes.
- **`#type Row Scalar end`** declares a type that is a Scalar (or a Ptr, Block or File) at run time but its own type to the checker. It generates `Row_of` and `Row_raw`.
- **The checker:**
  - Values of one distinct type compare with each other (`=`, `!=`, `<`, `>`, `min`, `max`).
  - These are TypeErrors, each with a hint naming the fix:
    - comparing a code with a plain number: the SQL runs' bug, where keyword 118 matched the literal 118;
    - arithmetic on a code;
    - a code passed where a number is expected, or the reverse;
    - a word whose declared result type does not match what its body leaves.
- **Cost:** both are erased; they cost nothing at run time. Use them as tags in signatures, record fields and word parameters.

### What changed in v1.65

Errors are reported at the call. Only messages change: every program that compiled under v1.64 still compiles, with the same output.

- **Where the stack runs out**, an ArityMismatch names the call, the inputs it takes, the values it found (named when they come from the word's inputs) and the missing ones: "The stack runs out at `pa` (line 6), which takes 3 values ( label:Block v:Scalar n:Scalar ) and finds 2 ( v:Scalar n:Scalar ): the missing one is the deepest, ( label:Block )". Top-level code gets the same message.
- **A TypeError at a call** is one error per call. It names each parameter that does not match (primitives included: "'hwrite' parameter 'p' expects Ptr but got Scalar"), shows what the callee takes beside what the top of the stack holds, and, when the right kinds of values are there in another order, says "check the order of the arguments".

### What changed in v1.64

Every program in this project's corpus that compiled under v1.63 still compiles, with the same output. A word named `fflush` is now rejected (it is a new primitive).

- **`fflush ( fh -- ok )`** writes out buffered output now: redirected stdout is block-buffered, so a long run's progress lines on stdout stayed invisible until the end.
- **`--test` stops a test that never ends**, after 600 s by default (`--test-timeout N`), keeping the PASS/FAIL lines already printed, and reports the timeout as a failure.
- **Clearer messages.** An input name that is unbound because the body begins with its own frame says so and shows the frame to write; `LargeWord` names its limit (60 tokens or 3 levels) plainly; `--words` marks a word over 60 tokens.
- **Docs.** A record field's offset word takes no record (`Tab_cols_off`, not `t Tab_cols_off`); `hsort` stops on a row holding a Ptr, `hnull` included; each module must `use` the lexicons it calls (a whole-program build is more lenient than checking the module alone); progress output and `fflush`.

### What changed in v1.63

Every program in this project's corpus that compiled under v1.62 still compiles, with the same output.

- **Hex and binary literals**: `0xEDB88320`, `0x1f`, `0b1011`, `-0x10`, up to 64 bits.
- **Top-level code is arity-checked from an empty stack**: a top-level call with too few arguments is rejected with the line, instead of stopping the program with `Fatal: Stack underflow`.
- **`--words` counts tokens exactly as `LargeWord` does**, so the small-word rule can be audited from its output.
- **Docs**: what a tail-recursive word does with its frames on each trip; `argc` under `--test`.

### What changed in v1.62: `when` is a statement

**Breaking:** `when` and `unless` are now statements, as in Common Lisp, and their value forms have their own names. A program that used `a when [ b ]` for a value is rejected with a message naming the replacement: write `a and_then [ b ]`. (`a unless [ b ]`, which was b when a is false, else 0, has no direct replacement; `a or_else [ b ]` is 1 when a is true, else b.) Words named `and_then` or `or_else` are now rejected (reserved). Every other program in the corpus compiles as before.

- **`x 0 < when [ "negative" str_print ]`** runs the body when the flag is true (`unless`: false) and leaves nothing; the body's net effect must be 0.
- **`a and_then [ b ]`** is b when a is true, else 0, and **`a or_else [ b ]`** is 1 when a is true, else b; b is evaluated only when needed. These are the short-circuit `and` and `or` (the words `and` and `or` evaluate both sides).

### What changed in v1.61: inputs are names

Every program in this project's corpus that compiled under v1.60 still compiles, with the same output.

- **A word's input names can be used directly.** `#sq ( x:Scalar -- y:Scalar ) x x * end` and `#dist2 ( x:Scalar y:Scalar -- d:Scalar ) x sq y sq + end` bind their inputs as if they began with `-> [ x ]` / `-> [ x y ]`. This applies when a body uses an input name that no frame binds; a body that binds its names itself, or works on the stack, means what it did. An input named like a word stays a call to the word (warning `ParamNamedLikeWord`).

### What changed in v1.60

Every program in this project's corpus that compiled under v1.59.1 still compiles, with the same output. A word named `fwrite_from` is now rejected (it is a new primitive).

- **`fwrite_from ( fh p start count -- written )`** writes heap cells as bytes in one call, the mirror of `fread_into`, so a program that streams output (a decompressor) need not call `fputc` per byte.
- **A `die` helper exempts its branch.** A cond branch ending in a call to a word whose body always ends in `abort` or `exit` is exempt from branch matching, like `abort` itself.
- **Fixes.** `--test` rejected any file with a comment over several lines; an editing command refused a snippet that passes a `'word` to a word of the file; `--words` counted a data literal element by element (it now counts one token, as `LargeWord` does).
- **Clearer error.** Numbers right after `-> [ names ]` are that frame's body, not a data literal; the ArityMismatch now says so.

### What changed in v1.59.1

- **A rejected word shows its alias warnings.** A frame alias spelled like a word (`-> [ lab nl ]` beside a `#nl` word) makes every later `nl` push the value instead of calling the word; the warning that says so was printed only after ACCEPT, so the ArityMismatch it explained came alone. It now comes with it.
- **`SimilarWords` warning**: words that are the same except for a call or two (`#safe_add`, `#safe_sub`, ... differing only in the operator) are named together, with the word parameter that would make them one.
- **Docs.** The skill guide says plainly that a small helper in a hot loop and a word parameter both cost nothing (both were believed otherwise), that a record getter consumes its Ptr, and that braces in comment text must pair; the spec's comment rule is corrected (braces need no surrounding spaces).

### What changed in v1.59: word parameters

Every program in this project's corpus that compiled under v1.58 still compiles, with the same output.

- **A word can take words as parameters**, so two words that differ in one step share their skeleton instead of copying it: `#each_cell ( p:Ptr n:Scalar step:Word(Ptr,Scalar--) -- ) -> [ p n step ] n [times| i | p i step ] end`, called as `p 3 'add_step each_cell`. The word passed must have the declared effect, checked at the call. Each distinct set of words passed compiles as an ordinary word (`each_cell<add_step>`), so it costs nothing and is checked and optimised like any other. There are no function values at run time.
- `examples/colstats/stats.sg` uses one: `st_min` and `st_max` share one loop, passed `'min` or `'max`.

### What changed in v1.58: small words

Programs are meant to be built from small words, each doing one job, combined into larger ones. This release removes the reasons not to.

Every program in this project's corpus that compiled under v1.57.2 still compiles, with the same output. A word named `expect`, `expect_eq` or `expect_near` in a program that uses `util` is now rejected (util has them).

- **Small words cost nothing.** A call to a non-recursive word of up to about 60 tokens (counting the small words it calls) is compiled as its body in place, and a counted loop that calls it keeps fast heap access. A two-read helper in a hot loop cost 3.7x the same code written inline; it now costs 1.2x. Error traces are unchanged: a word that calls others still appears in the word chain.
- **`--test FILE`** runs every `#test_name ( -- ok:Scalar )` word in a file and prints PASS/FAIL for each; `expect`, `expect_eq` and `expect_near` (util) say what failed. A module can carry its own tests.
- **Private words.** In a module, a word whose name starts with `_` is visible only in that file, so helpers do not collide across modules.
- **Size is visible.** `--words` lists each word's size in tokens, and the checker warns (`LargeWord`) about a word over 60 tokens or nested more than 3 deep.
- **Clearer arity errors.** An ArityMismatch names the line where the stack runs out, which is where a call got too few values.
- **Checker fix.** `rot` was typed as if it did nothing, so a correct call after `rot` could be rejected.
- **Docs.** The skill guide's section 1 is a workflow for writing, testing and combining small words, with flat frames (`-> [ x ]` needs no body bracket) and its one trap; `examples/colstats/` is a program written that way.

### What changed in v1.57.2

Every program in this project's corpus that compiled under v1.57.1 still compiles, with the same output. A program that uses `args` and defines its own `#arg_float_or` is now rejected (the lexicon has one); drop the local definition.

- **`use "../src/m"` works wherever Scrooge is installed.** With the Scrooge clone inside the working directory, a `use` with a path in it could resolve to the program's own module as if it were a library lexicon, and then none of its words were known. A name with a path is now always a module. A library file that the manifest does not list is an error that says so.
- **`--loops`** prints, for every counted loop, whether its heap accesses compile to one bounds check each (`fast access through p`) or which word call prevents it.
- **Loop, map and fold body errors show the stack depth at the end of each body line**, like the whole-word ArityMismatch.
- **`arg_float_or`** (args): a decimal command-line value, `-l 0.02`.
- **Docs.** The spec says which operand of `-`, `/` and `\` is which ("w lr v * -" is w - lr*v), and that `_set` copies a Block while `hwrite` and record setters write a heap cell in place.

### What changed in v1.57.1

An ArityMismatch for a word with an empty body says the body is empty (it printed an empty list of line depths).

### What changed in v1.57

Every program in this project's corpus that compiled under v1.56.3 still compiles, with the same output. A `use "numeric"` or `use "procinfo"` now loads the new library lexicons, and a module file named like any library lexicon is an error instead of being silently ignored.

- **Faster heap loops.** A counted loop (`[times| ]`, `[for| ]`) whose body calls no word checks each heap address it uses once, before the loop; each `hread`/`hwrite` inside is then one bounds check. Three numeric training programs run 20-35% faster, with identical results; errors are reported exactly as before.
- **`numeric` lexicon**: `vec_dot`, `vec_axpy`, `vec_add`, `vec_scale`, `vec_sum`, `vec_max`, `vec_argmax` over ranges of heap cells, and `vec_be32` / `vec_le32` for 32-bit integers in byte cells (binary file headers).
- **`procinfo` lexicon**: `proc_peak_kb` (peak resident memory, VmHWM), `proc_rss_kb`, `proc_status_kb`.

### What changed in v1.56.3

No program's behaviour changed; two error messages say more.

- **An unclosed `[` says where the `]` is probably missing.** The error named only the line of the outermost open bracket; it now uses the indentation to point at the `]` that closes the wrong bracket: `unterminated [ block (probably a ']' is missing before line 6, closing the '[' at line 4 ...)`.
- **A non-Ptr address says what it was**: `hwrite address must be a Ptr, got the integer 0 (a Ptr comes from hnew, a #record's _new, or a cell that holds one)`.

### What changed in v1.56.2

Every program in this project's corpus that compiled under v1.56.1 still compiles, with the same output. `print_int` of a float is now a fatal error (it printed the float with six decimals).

- **A loop that rebinds an outer name warns.** `0 -> [ s ] [ 5 [times| i | s i + -> [ s ] ] s ]` leaves s at 0, since the inner frame makes a new name for one iteration; the compiler now says so (`AliasRebindsOuter`), and the spec states the rule.
- **Clearer errors.** A name used after the block that bound it says where it was bound and why it is gone. A word named like one a `#record` generates names the record; `--words` lists the words each record generates.
- **Small things.** `--fmt --check` says `already formatted`; the skill guide says `use` takes a relative path (`use "../src/geo"`).

### What changed in v1.56.1

- **Faster float arithmetic.** `+`, `-` and `*` on two floats take a direct path: a multiply-add loop is 33% faster and a larger float-heavy program 9% faster, with identical results; integer code is unchanged.
- **A word's comment moves with it.** The comment lines directly above a `#name` line belong to the word: `--show` prints them, `--delete` removes them, `--insert-before` goes above them, and `--replace` replaces them when the new text brings its own comment.
- **Docs.** Each heap cell takes 16 bytes (spec Sec.5); the skill guide shows how to pack small values, and that `to_float` on a value reused in a hot loop speeds the loop up. The spec and skill guide titles now say v1.56.

### What changed in v1.56

Every program in this project's corpus that compiled under v1.55.2 still compiles, to the same output. A word or alias named `floor` is now rejected (it is a new primitive).

- **Real functions.** `exp`, `log`, `sqrt` and `pow`, reserved since early versions, are implemented: they take integers or floats and return floats (`2 10 pow` is 1024.0). `floor` rounds down to an integer (`-2.5 floor` is -3).
- **Random numbers.** `rand` is a pseudo-random float in [0, 1) (xorshift64*, 53 bits) and `s seed` restarts its sequence. A program that never calls `seed` gets the same numbers on every run.

### What changed in v1.55.2

`fold`/`map` over a value that is not a Block stop with a message (`str_print` of a number crashed); a crash prints the running words and keeps the program's output; `--profile` prints its table when a program is stopped by `timeout` or Ctrl-C; the spec states plainly that a frame's first name gets the deepest value.

### What changed in v1.55.1

`--no-ptr-check` leaves the stale-pointer check out of a build, for benchmark measurements of a program already tested with it on (about 7% faster in code made almost only of heap reads).

### What changed in v1.55

Every program in this project's corpus that compiled under v1.54 still compiles, to the same output. A word named `sort_cmp` is now rejected (it is a new primitive), and two things that silently went wrong now stop the program with a message: arithmetic or `<`/`>` on a Block, and a Ptr used after the `hrelease` of its region.

- **Unclosed comments and strings are errors.** An unclosed `{` used to turn the rest of its file, and every module loaded after it, into comment, and the program was accepted. Now each file is checked on its own and the error names the file, line and column.
- **Stale pointers are caught.** A Ptr used after its `hmark`/`hrelease` region was released (even after its slot was reused) is a fatal error that says so, instead of reading or writing someone else's allocation. This costs one comparison per `hread`/`hwrite` (about 7% in a program made almost only of heap reads, nothing measurable in a larger one).
- **Defined arithmetic.** Arithmetic on a non-number is a fatal error (it returned a garbage number); integer overflow wraps around; min-int `/ -1` no longer crashes. The spec now says exactly what `/` (truncates) and `\` (floored remainder) do.
- **`sort_cmp ( a b -- c )`** orders two values as `hsort` does: -1, 0 or 1, so two strings compare in byte order.
- **Killed programs keep their output.** A program stopped by `timeout` or Ctrl-C flushes what it has printed before it dies.

### What changed in v1.54

Every program in this project's corpus that compiled under v1.53.2 still compiles, to the same output. A word, parameter or alias named `when` or `unless` is now rejected (both are reserved).

- **Short-circuit forms.** `a when [ b ]` is the value of b when a is true, else 0, and b is not evaluated otherwise; `a unless [ b ]` is b when a is false, else 0. `b len 0 > when [ b 0 block_get x = ]` guards an access that `and` (which evaluates both sides) would perform anyway.
- **Hints and warnings.** `%` and `mod` point to `\`, and `&&`/`||` to `and`/`or`/`when`. A frame alias spelled like one of your own words gets a warning, since it hides the word.
- **Docs.** Every library word in `library/manifest.sm` now has a real description (17 had none, including the whole `array`, `list`, `record` and `map_make`). The spec says a fold's `from` takes any expression. The skill guide says to measure resident memory (`VmHWM`), not `VmPeak`.

### What changed in v1.53.2

Source-editing commands in the compiler, working on whole word definitions: `--words`, `--show`, `--replace`, `--insert-before`, `--insert-after`, `--delete` and `--fmt` (skill guide section 8b). New definitions are checked before anything is written. No language change.

### What changed in v1.53.1

Two fixes: a `fold` or `map` nested inside a `fold` body released its loop variables twice (a crash or corrupted data once v1.53 freed nested Blocks), and a fold's `from` expression was not checked (an unknown word there was accepted and then failed to build).

### What changed in v1.53

Every program in this project's corpus that compiled under v1.52 still compiles, to the same output. A word, parameter or alias named after one of the five new primitives (`exit`, `to_int`, `float_to_str`, `type_of`, `hnull`) is now rejected, and a `use` that names neither a library lexicon nor a file beside the program is now an error (it was ignored).

- **User modules.** `use "name"` loads your own name.sg from the program's directory when no library lexicon has that name. Modules load transitively and once each, and every error, warning, runtime word chain and `trace` names the module file and its own line.
- **No more nested-Block leak.** A Block now owns the Blocks inside it and frees them with itself. A program that keeps many rows built from pairs went from 4.0 GB to 197 MB; freeing that memory costs about 20% more time in such programs.
- **No allocation limit.** The heap allocation table grows on demand; `hnew` used to stop at 1,000,000 live allocations.
- **Build speed.** `-O0` to `-O3` choose gcc's optimisation level (default `-O3`); `-O0` builds a large program about ten times faster while developing it.
- **New primitives:** `exit ( code -- )`, `to_int ( x -- n )`, `float_to_str ( x decimals -- s )`, `type_of ( v -- t )`, `hnull ( -- p )`.
- **Sorting Blocks.** `hsort` and `block_sort` order strings (byte order) and rows (column by column) as well as numbers.
- **Checker.** Frames may bind 64 names (was 16); the mutual-recursion warning no longer fires on tree recursion such as an expression evaluator; a fold nested in a fold body now parses.
- **Docs.** Spec Sec.8 lists every library word with its signature. The skill guide explains how to learn Scrooge from its documents and small experiments, how to design top down and build bottom up in tested increments, and how to run long programs safely; it no longer suggests reading the generated C.

### What changed in v1.52.1

No compiler, library or specification behaviour changed. Old sample programs (early forks of a large application, and a hashing test) were removed from `check/corpus/` so that benchmarks written against this repository start from a clean slate.

### What changed in v1.52

Every program in this project's corpus that compiled under v1.51 still compiles, to the same output. Three things behave differently: a REJECT now exits with status 1 (it exited 0), a runtime fatal error is followed by the list of words that were running, and a negative shift count is a fatal error (it was undefined).

- **Counted loops.** `n [times| i | body ]` runs i = 0..n-1 and `lo hi [for| i | body ]` runs i = lo..hi-1. The body sees `i` and every name in scope, must leave the stack as deep as it found it, and threads accumulators left below the loop: `0 10 [times| i | i + ]` is 45. Loops nest, compile to C `for` loops, and run about twice as fast as the equivalent tail-recursive word (spec Sec.3, skill guide section 2c).
- **Safer builds.** A REJECT exits 1, and a build first removes any old binary at the output path, so a rejected build never leaves a stale program to be run by mistake.
- **All errors at once.** Type errors are reported in the same run as unknown-word and stack-effect errors.
- **Runtime errors say where.** A `Fatal:` message is followed by the running words, innermost first, each with its definition line (`in #report (defined line 2)`). `print_fixed` given a float now stops before printing anything.
- **Shifts are defined.** A count of 64 or more gives 0; a negative count is fatal; `bitshr` is documented as a logical shift.
- **Records.** Each field gets `Name_field_off ( -- n )`, its first cell, for `hmove`, `hfill` and `fread_into`.
- **Fixes.** `hread` truncated its offset to 32 bits (offset 2^32+1 read cell 1).
- **Faster.** Words that call no other word skip call tracking: two sudoku solvers run 5-13% faster.
- **Docs.** Words may be defined in any order (the old "define helpers before callers" rule was never enforced); the skill guide explains how stack effects add up; stale text about `block_sort`, `getenv` and the file primitives is fixed.

### What changed in v1.51

Every program in this project's corpus that compiled under v1.50 still compiles, to the same output. A word, parameter or alias named after one of the seven new primitives (`freadline`, `fread_into`, `fseek`, `ftell`, `trace`, `hmove`, `hfill`) is now rejected. Output to stdout is now buffered, so a program killed by a signal can lose output it had not yet flushed; normal exit, `abort` and runtime errors flush it.

- **Records.** `#record Name  field Type count ...  end` declares a heap layout and generates `Name_new`, `Name_size` and a typed getter and setter per field, with computed offsets (spec Sec.5). A word named `record` (`#record ( ... )`) is still an ordinary definition.
- **`--profile`** builds a program that prints each word's calls, self time and total time to stderr at exit.
- **Debugging.** `trace ( v -- )` prints a value of any type and its source line to stderr; `assert ( ok msg -- )` in `util.sg`; a debugging section in the skill guide, including how to read `--dump-c` output.
- **Clearer errors.** An unknown word that a lexicon defines names it (`'<=': it is defined in lexicon "util"; add: use "util"`), a parenthesis is explained, and the misleading ArityMismatch that followed an unknown word is gone. A definition named after a reserved word says so; a collision names the lexicon or primitive it collides with.
- **Warning for loops written as mutual recursion.** Words that call each other round a cycle of tail calls get a `WARNING MutualRecursion` on stderr after `ACCEPT`: only direct self-recursion runs as a loop, so such a cycle stops at 65,536 trips with `Fatal: Max frames exceeded`.
- **Faster output and input.** Printing no longer flushes on every call (5.8x faster). `freadline` reads a line in one pass, and `f_read_line` uses it (7x faster); `fread_into` reads bytes straight into heap cells; `fseek`/`ftell` reposition a file.
- **Bulk heap work.** `hmove` (overlap-safe cell copy) and `hfill`.
- **Fix.** `memory.sg`'s `h_find_val` failed with `Max frames exceeded` on allocations over 65,536 cells; it is now a single loop.

### What changed in v1.50

Every program in this project's corpus that compiled under v1.49 still compiles, to the same output. Nothing v1.49 accepted is rejected, except a word, parameter or alias named after one of the seven new primitives. One construct changes meaning: a string or data literal right after a frame's names (see Fixes).

- **Much faster generated code.** Word variables are C locals, words compile to C functions with parameters and returns, the stack is cached in C temporaries, values are 16 bytes, and the C is built with `-O3`. Call-heavy benchmark programs run many times faster (over 100x on the largest) with identical output; a sudoku solver's throughput rose 3.8x.
- **Faster checking.** The parser is linear in the number of frames in a block: checking a 1.2 MB generated program went from 280 s and 27 GB to 0.5 s.
- **New primitives (68):** `bitcount`, `bitctz`, `bitclz` (popcount and bit scans); `hsort` (sort heap cells in place, stable); `print_float ( x decimals -- )`; `getenv ( name -- value ok )`, read-only; `block_slice`.
- **Library:** `block_sort` is O(n log n) (it was an O(n^2) insertion sort); `length` is O(1); `bs_count`/`bs_first` use the bit primitives; `print_fixed` and `int_to_str_pad` in `strings.sg`; `f_expand_home` in `file.sg`; `arg_flag`, `arg_value_or`, `arg_int_or` in `args.sg`.
- **Fixes.** A string literal right after a frame's names is a value, not the frame's body. Writing over a Block held in a heap cell, or releasing a heap region holding Blocks, no longer leaks. `ArityMismatch` shows the stack depth at the end of each line of the word. The spec says what is true: a frame's body bracket is optional, and code blocks nest freely.
- **Docs.** `.agents/rules/scrooge_rules.md` is current (it described v1.41). Old corpus files now live in `check/corpus/historical/`, labelled as not showing current style.

### What changed in v1.49

Every program in this project's corpus that compiled under v1.48 still compiles, to the same behaviour. Two differences are visible:

- Programs no longer print a trailing `STACK: []` (see `--debug-stack` below).
- Three things v1.48 accepted are now rejected: a shuffler name (`dup`, `drop`, `swap`, `rot`, `over`) used as a frame alias, which silently shadowed the primitive; a word or alias named `clock_ns`, now a primitive; and a last definition with no `end`, which silently swallowed the call to `main`.

The rest:

- **`cond` is easier to write.** The closing `?` is optional (`flag cond [ t ] else [ f ]` is complete), and the else-branch may be omitted (`flag cond [ t ]` means `else [ ]`). Old code with `?` and `else [ ]` is unchanged.
- **Better errors.** `cond` parse errors give a line and column and name the cond they mean; a stray `?`, `else` or `end`, or a definition missing its `end`, is reported where it stands. The checker now also checks top-level code, and reports every error, in source order, each once (it stopped at 10, in arbitrary order).
- **`clock_ns ( -- ns:Scalar )`**, a monotonic clock primitive (61 primitives).
- **`library/manifest.sm` lists every primitive** as a typed `prim` line, checked against the compiler.
- **One reserved-word list.** The compiler, spec Sec.10 and the skill guide now agree; `dup drop swap rot over` can no longer be used as frame aliases. `pk`/`roll` are no longer shown as callable (they are reserved but not implemented).
- **`--debug-stack`** restores the old trailing `STACK: [...]` line, now off by default.

This repository contains the Scrooge static compiler, standard library, language specifications, automated test harness, and benchmark suite.

---

## 1. Compiler Toolchain & Binary Executable

The compiler ships prebuilt in `compiler/`: `compiler/scroogec_fast` (dynamically linked), `compiler/scroogec_fast_x86-64` (static, Linux x86-64) and `compiler/scroogec_fast_arm64` (static, Linux arm64). It is the static verifier, type checker and C code generator for Scrooge v1.55, and it builds executables by running `gcc`. Its Nim source, the test gates and the manifest tooling live in the development repository and are not part of this one.

### Quick Commands

```bash
# Perform static verification only (outputs ACCEPT or REJECT)
compiler/scroogec_fast -L library --check-only my_program.sg

# Compile Scrooge source file into a native ELF executable
compiler/scroogec_fast -L library -o my_program my_program.sg

# Dump generated intermediate C source code
compiler/scroogec_fast -L library --dump-c out.c my_program.sg
```

A complete command-line program to start from: `examples/args_demo.sg`.

For complete technical documentation on compiler architecture, C codegen optimizations (`make_int_array`), AST line-number tracking (`lineNum: int`), and diagnostic formats, refer to [`compiler/scroogec_fast.md`](compiler/scroogec_fast.md).

---

## 2. Language Specification & Skill Guide

- **Cheat sheet**: [`spec/scrooge_cheatsheet.md`](spec/scrooge_cheatsheet.md), the language on one screen.
- **Core Language Specification**: [`spec/scrooge_spec_v1_74.txt`](spec/scrooge_spec_v1_74.txt) (defines v1.74 syntax, the `cond` form, plain decimal floats `3.14`, `to_float` casting, inter-macro tagged parameter type validation, arity drift protection, and error class specifications).
- **LLM Skill & Pattern Guide**: [`spec/scrooge_skill.md`](spec/scrooge_skill.md) (operational guide for LLM generation, block-building idioms, unbracketed `cond` rules, and standard library usage).
- **System Prompt**: the specification itself is written as the system prompt for LLM generation; there is no separate file.

---

## 3. Standard Library & Discovery Manifest

Standard library lexicon modules reside in `library/`:
- `library/strings.sg`: Signed integer formatting (`int_to_str`), string printing (`str_print`), character predicates (`is_digit`, `is_space`, `is_upper`, `is_lower`).
- `library/util.sg`: Block equality (`block_eq`), stable sorting (`block_sort`), reversal (`reverse`), length (`length`), sum (`sum`), search (`contains`, `index_of`), filtering (`filter_eq`), concatenation (`concat`), comparisons (`>=`, `<=`).
- `library/array.sg`: Safe indexing (`nth_or_default`), N-dimensional heap arrays (`arr_make`, `arr_get`, `arr_set`, `arr_offset`, `arr_size`).
- `library/memory.sg`: Heap operations (`hclear`, `hloop_fill`, `hloop_add`, `h_find_val`).
- `library/list.sg`, `library/map.sg`, `library/record.sg`: Growable lists, hash maps, static records.
- `library/bitset.sg`: 64-bit bitsets as plain Scalars (`bs_add`, `bs_test`, `bs_union`, `bs_inter`, `bs_minus`, `bs_count`, `bs_first`).
- `library/file.sg`: Sequential file I/O over the opaque `File` handle -- whole-file transfer (`f_read_file`, `f_write_file`, `f_append_file`), explicit open/close (`f_open_read`/`f_open_write`/`f_open_append`), streaming reads and writes (`f_read_all`, `f_read_line`, `f_write_str`, `f_write_line`), and the pre-opened standard streams (`f_stdin`, `f_stdout`, `f_stderr`).
- `library/args.sg`: Command-line arguments over the `argc`/`argv` primitives -- the program name (`arg_prog`), a total accessor taking a default (`arg_or`), the arguments without the program name as a Block of Blocks (`arg_tail`), and flag scanning (`arg_find`).

The discovery manifest is synchronized at [`library/manifest.sm`](library/manifest.sm). It is generated, not hand-maintained: `tools/build_manifest.py` (in the development repository) is the single canonical source of truth, deriving every entry (and the matching spec §8 lexicon word-lists) directly from `library/*.sg`. It also lists every compiler primitive as a `prim` line; those come from a table in the tool that `--check` holds against the compiler's own primitive tables (every primitive present once, matching arity and types), so they cannot drift either. The compiler reads only the `tool` lines. Regenerate it after any library change, or just verify it's in sync:
(`python3 tools/build_manifest.py --check` verifies it in the development repository.)

---

## 4. Automated Test Suite (Gates A through J)

These gates run in the development repository, which holds the compiler source; they are listed here as a record of what every release is verified against. They cannot be run from this repository, which contains the prebuilt compiler, the library, the specification and the corpus.

Execute the standard automated test harness to verify compiler correctness, inter-macro type validation, decimal float support, signed string formatting, and manifest integrity:

Run in the development repository: `python3 scratch/test_gates_a_j.py`.

### Test Gate Coverage
- **Gate A**: Heuristic eradication (`Block` parameter named `src` PASSES).
- **Gate B**: Positional signature rejection (`Ptr` with `at` REJECTED statically).
- **Gate C**: Tagged signature rejection (`data:Ptr` with `at` REJECTED statically).
- **Gate D**: Arity mismatch guard (Frame vs signature input mismatch REJECTED).
- **Gate E**: Local provenance rejection (`hnew -> [ p ] [ p 0 at ]` REJECTED statically).
- **Gate F**: Local block provenance acceptance (`nil -> [ b ] [ b 0 at ]` PASSES).
- **Gate G1**: Call-site macro parameter order swap (Passing `Block` to tagged `Ptr` REJECTED statically).
- **Gate G2**: Correct call-site macro parameter order (PASSES).
- **Gate G3**: Library call-site type checking at parity with local (a library word called with swapped arguments must be rejected with the *same number* of `TypeError`s as an identically-shaped local word -- guards against `manifest.sm` losing its type tags again).
- **Gate H**: Bare decimal float literal compilation & execution (`3.14` PASSES).
- **Gate I**: Signed string formatting (`int_to_str` on `-42` outputs `"-42"` PASSES).
- **Gate J**: Library manifest + spec §8 100% synchronization check (PASSES).

### File I/O Gate (Gate K)

File I/O has its own harness, covering the static guarantees the `File` type provides, the runtime behaviour of all six file primitives and every public word in `library/file.sg`, and a memory regression test for Bug 17:

Run in the development repository: `python3 scratch/test_gates_file_io.py`.

- **Gate K1-K4**: Static rejection of `File` misuse (arithmetic, `hread`, `_at`, swapped `fputc` arguments).
- **Gate K5**: Whole-file read/write round trip, byte for byte.
- **Gate K6**: Line-at-a-time round trip, empty lines preserved.
- **Gate K7**: `stdin` to `stdout` copy through `f_stdin`/`f_stdout`.
- **Gate K8**: Every partial outcome reported through a flag, never a crash (missing file, append, closing a standard stream, double close).
- **Gate K9**: `fread` partial/short/at-EOF results and `fwrite`'s written count.
- **Gate K10**: `--selftest` primitive-surface exhaustiveness across both backends.
- **Gate K11**: Bug 17 regression -- a chained-frame tail-recursive accumulator stays flat in memory under a 256MB cap.

### Command-Line Argument Gate (Gate O)

Run in the development repository: `python3 scratch/test_gates_args.py`.

Covers the static guarantees (`argv`'s index must be a `Scalar`; its result is a `Block`, not a `Scalar` or a `File`), the C indexing `argc`/`argv` promise (`argc == 1` with no arguments, `argv[0]` is the program as invoked), arguments preserved verbatim including spaces and an empty one, out-of-range in both directions giving `ok=0`, the **present-but-empty** case that must give `ok=1` rather than `ok=0`, and every public word in `library/args.sg`.

### Corpus Gate (Gate N)

Every file in `check/corpus/passing/` must actually pass the checker:

Run in the development repository: `python3 scratch/test_gates_corpus.py`.

The directory name is a claim, and for four of its seven files it was false -- three obsolete pre-lexicon programs plus one program with a redundant local `#pair`, all rejected under v1.48's `DuplicateWordError` rules and all left behind by the v1.48 upgrade. The obsolete programs were moved out of the gated directory.

### Lexicon Gate (Gate M)

Every standard-library lexicon must pass the checker standalone:

Run in the development repository: `python3 scratch/test_gates_lexicon.py`.

Library source is concatenated into a program for *codegen* but never reaches `checkSource` -- `reservedWordPass`, `checkNesting`, the Track 1 arity analyzer and Track 2 all see only the user's file, with lexicon words supplied as pre-typed externs from `manifest.sm`. So `library/*.sg` was the one place in the tree where "code either passes the checker or is rejected" did not hold. Running each lexicon as a top-level source file puts library code under the same rules as everything else; all nine pass.

### Refcount Leak Gate (Gate L)

Per-primitive refcount leak gates, one probe per op:

Run in the development repository: `python3 scratch/test_gates_leak.py`.

The contract each probe enforces: a value popped off the stack carries a reference, and the op that popped it must **return** it, **store** it into a structure, or **release** it. An op doing none of the three leaks permanently, in proportion to its call count. Every probe allocates a *fresh* Block each iteration and asserts peak RSS is flat across a 16x range of iteration counts -- the freshness matters, since leaking a reference to one long-lived Block costs no memory.

Ten ops pass flat (`len`, `at`, `block_get`, `=`, `!=`, both `select` branches, plus `cons`, `block_set` and `hwrite` as known-correct controls). The probes that once leaked by design all pass now: a Block written into a heap cell (fixed in v1.50), and `pair` and a nested `cons`, fixed in v1.53 when a Block became the owner of the Blocks inside it and releases them when it is freed.
