# Scrooge Programming Language (v1.48)

Repository status: **Scrooge v1.48**.

This repository contains the Scrooge static compiler, standard library, language specifications, automated test harness, and benchmark suite.

---

## 1. Compiler Toolchain & Binary Executable

The Nim static compiler executable `./scroogec_fast` (and its statically-linked binary `compiler/scroogec_fast_x86-64`) is the sole static verifier, type checker, and C code generation compiler for Scrooge v1.48 in this environment.

### Quick Commands

```bash
# Rebuild static compiler binary from source
nim c -d:release scroogec_fast.nim

# Perform static verification only (outputs ACCEPT or REJECT)
./scroogec_fast --check-only my_program.sg

# Compile Scrooge source file into a native ELF executable
./scroogec_fast -L library -o my_program my_program.sg

# Dump generated intermediate C source code
./scroogec_fast --dump-c out.c -L library my_program.sg
```

For complete technical documentation on compiler architecture, C codegen optimizations (`make_int_array`), AST line-number tracking (`lineNum: int`), and diagnostic formats, refer to [`compiler/scroogec_fast.md`](file:///home/yoel/Experiments/Scrooge/scrooge_dev/compiler/scroogec_fast.md).

---

## 2. Language Specification & Skill Guide

- **Core Language Specification**: [`spec/scrooge_spec_v1_48.txt`](file:///home/yoel/Experiments/Scrooge/scrooge_dev/spec/scrooge_spec_v1_48.txt) (defines v1.48 syntax, plain decimal floats `3.14`, `to_float` casting, inter-macro tagged parameter type validation, arity drift protection, and error class specifications).
- **LLM Skill & Pattern Guide**: [`spec/scrooge_skill.md`](file:///home/yoel/Experiments/Scrooge/scrooge_dev/spec/scrooge_skill.md) (operational guide for LLM generation, block-building idioms, unbracketed `cond` rules, and standard library usage).
- **System Prompt**: [`spec/system_prompt_v1.48.txt`](file:///home/yoel/Experiments/Scrooge/scrooge_dev/spec/system_prompt_v1.48.txt) (system prompt for LLM generation).

---

## 3. Standard Library & Discovery Manifest

Standard library lexicon modules reside in `library/`:
- `library/strings.sg`: Signed integer formatting (`int_to_str`), string printing (`str_print`), character predicates (`is_digit`, `is_space`, `is_upper`, `is_lower`).
- `library/util.sg`: Block equality (`block_eq`), stable sorting (`block_sort`), reversal (`reverse`), length (`length`), sum (`sum`), search (`contains`, `index_of`), filtering (`filter_eq`), concatenation (`concat`), comparisons (`>=`, `<=`).
- `library/array.sg`: Safe indexing (`nth_or_default`), N-dimensional heap arrays (`arr_make`, `arr_get`, `arr_set`, `arr_offset`, `arr_size`).
- `library/memory.sg`: Heap operations (`hclear`, `hloop_fill`, `hloop_add`, `h_find_val`).
- `library/list.sg`, `library/map.sg`, `library/record.sg`: Growable lists, hash maps, static records.

The v1.48 discovery manifest is synchronized at [`library/manifest.sm`](file:///home/yoel/Experiments/Scrooge/scrooge_dev/library/manifest.sm). Verify 100% manifest synchronization with:
```bash
python3 manifest_check.py
```

---

## 4. Automated Test Suite (Gates A through J)

Execute the standard automated test harness to verify compiler correctness, inter-macro type validation, decimal float support, signed string formatting, and manifest integrity:

```bash
python3 scratch/test_gates_a_j.py
```

### Test Gate Coverage
- **Gate A**: Heuristic eradication (`Block` parameter named `src` PASSES).
- **Gate B**: Positional signature rejection (`Ptr` with `at` REJECTED statically).
- **Gate C**: Tagged signature rejection (`data:Ptr` with `at` REJECTED statically).
- **Gate D**: Arity mismatch guard (Frame vs signature input mismatch REJECTED).
- **Gate E**: Local provenance rejection (`hnew -> [ p ] [ p 0 at ]` REJECTED statically).
- **Gate F**: Local block provenance acceptance (`nil -> [ b ] [ b 0 at ]` PASSES).
- **Gate G1**: Call-site macro parameter order swap (Passing `Block` to tagged `Ptr` REJECTED statically).
- **Gate G2**: Correct call-site macro parameter order (PASSES).
- **Gate H**: Bare decimal float literal compilation & execution (`3.14` PASSES).
- **Gate I**: Signed string formatting (`int_to_str` on `-42` outputs `"-42"` PASSES).
- **Gate J**: Library manifest 100% synchronization check (PASSES).
