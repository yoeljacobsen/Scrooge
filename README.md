# Scrooge Programming Language (v1.57)

Repository status: **Scrooge v1.57.2**.

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

- **Core Language Specification**: [`spec/scrooge_spec_v1_57.txt`](spec/scrooge_spec_v1_57.txt) (defines v1.57 syntax, the `cond` form, plain decimal floats `3.14`, `to_float` casting, inter-macro tagged parameter type validation, arity drift protection, and error class specifications).
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
