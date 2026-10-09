# Scrooge Programming Language (v1.96)

Repository status: **Scrooge v1.96**.

Scrooge is a small concatenative (postfix) language whose compiler checks every word's stack effect, types and argument order before it builds a native program through C. It is designed to be written by language models: one required, explicit, checked form for each thing.

## Start here: learning Scrooge and writing a program in it

1. **The cheat sheet** ([`spec/scrooge_cheatsheet.md`](spec/scrooge_cheatsheet.md)): the language on one screen, with the mistakes that cost the most.
2. **The specification** ([`spec/scrooge_spec_v1_96.txt`](spec/scrooge_spec_v1_96.txt)), once, end to end: it is short and normative.
3. **The skill guide** ([`spec/scrooge_skill.md`](spec/scrooge_skill.md)): how to work. Section 0: how to learn the language; 0b: how to build a program (design top down, name the library words of each layer, then build and test bottom up, one module per layer, and run the whole program early); **0d: which library words do which job**; section 1: small words (one word, one step), each with `#test_` words; 8b: changing words with `--edit`.
4. **A whole program built that way**: [`examples/wavstat/`](examples/wavstat/) and its [`examples/wavstat/DESIGN.md`](examples/wavstat/DESIGN.md): four modules, a state record, a file read as a stream, its own error line, tests and stop tests in every module. Copy its shape.
5. **The library**: [`library/manifest.sm`](library/manifest.sm) lists every word with its signature; `--lookup NAME`, `--apropos TERMS`, `--explain ErrorClass` and `--stack WORD FILE` answer most questions without leaving the terminal.
6. **Small probe programs** for whatever is still unclear.

## The compiler

`compiler/scroogec_fast` (dynamically linked), `compiler/scroogec_fast_x86-64` (static, Linux x86-64) and `compiler/scroogec_fast_arm64` (static, Linux arm64) check a program and build it by running `gcc`.

```bash
compiler/scroogec_fast -L library --check-only prog.sg      # ACCEPT, or every error found
compiler/scroogec_fast -L library -O0 -o prog prog.sg        # fast build while developing
compiler/scroogec_fast -L library -o prog prog.sg            # optimised build (-O3)
compiler/scroogec_fast -L library --test --deep prog.sg      # every module's #test_ words
compiler/scroogec_fast -L library --edit src/mod.sg < script # change words, checked, undone if it breaks
compiler/scroogec_fast -L library --lookup NAME              # a word's signature and description
```

Skill guide section 8 lists every command; [`compiler/scroogec_fast.md`](compiler/scroogec_fast.md) describes the compiler's internals.

## What is here

- `spec/`: the cheat sheet, the specification and the skill guide.
- `library/`: the lexicons (`use "vec"`, `use "file"`, `use "bitread"`, ...) and `manifest.sm`, generated from them.
- `examples/`: `wavstat/` (a whole program in modules); `tokens/` (a tokenizer), `wordfreq/` (counting and a sorted table) and `matvec/` (a numeric kernel on Floats), one file each; `colstats/` (an older, smaller program); `examples/args_demo.sg` (a command line).
- `check/corpus/`: programs the compiler is checked against.
- [`CHANGES.md`](CHANGES.md): what changed in each release, and how each release is verified.
