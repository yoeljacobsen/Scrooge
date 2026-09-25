# Scrooge Programming Language (v1.49)

Repository status: **Scrooge v1.49**.

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

The compiler ships prebuilt in `compiler/`: `compiler/scroogec_fast` (dynamically linked), `compiler/scroogec_fast_x86-64` (static, Linux x86-64) and `compiler/scroogec_fast_arm64` (static, Linux arm64). It is the static verifier, type checker and C code generator for Scrooge v1.49, and it builds executables by running `gcc`. Its Nim source, the test gates and the manifest tooling live in the development repository and are not part of this one.

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

- **Core Language Specification**: [`spec/scrooge_spec_v1_49.txt`](spec/scrooge_spec_v1_49.txt) (defines v1.49 syntax, the `cond` form, plain decimal floats `3.14`, `to_float` casting, inter-macro tagged parameter type validation, arity drift protection, and error class specifications).
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

The directory name is a claim, and for four of its seven files it was false -- three obsolete pre-lexicon engine forks plus one program with a redundant local `#pair`, all rejected under v1.48's `DuplicateWordError` rules and all left behind by the v1.48 upgrade. The forks now live in `check/corpus/legacy_pre_v148/` (with a README explaining why they no longer compile and which maintained engines superseded them), and that directory is deliberately not gated.

### Lexicon Gate (Gate M)

Every standard-library lexicon must pass the checker standalone:

Run in the development repository: `python3 scratch/test_gates_lexicon.py`.

Library source is concatenated into a program for *codegen* but never reaches `checkSource` -- `reservedWordPass`, `checkNesting`, the Track 1 arity analyzer and Track 2 all see only the user's file, with lexicon words supplied as pre-typed externs from `manifest.sm`. So `library/*.sg` was the one place in the tree where "code either passes the checker or is rejected" did not hold. Running each lexicon as a top-level source file puts library code under the same rules as everything else; all nine pass.

### Refcount Leak Gate (Gate L)

Per-primitive refcount leak gates, one probe per op:

Run in the development repository: `python3 scratch/test_gates_leak.py`.

The contract each probe enforces: a value popped off the stack carries a reference, and the op that popped it must **return** it, **store** it into a structure, or **release** it. An op doing none of the three leaks permanently, in proportion to its call count. Every probe allocates a *fresh* Block each iteration and asserts peak RSS is flat across a 16x range of iteration counts -- the freshness matters, since leaking a reference to one long-lived Block costs no memory.

Ten ops pass flat (`len`, `at`, `block_get`, `=`, `!=`, both `select` branches, plus `cons`, `block_set` and `hwrite` as known-correct controls). Three probes are tracked as known-cause `XFAIL`s: `block_decref` does not recurse into Block-typed elements, so `pair`, a nested `cons`, and a Block written into a heap cell and then `hrelease`d all leak their elements. That is a separate ownership question, recorded in `BUGFIX_TASK_PLAN.md` in the development repository as Task 9.
