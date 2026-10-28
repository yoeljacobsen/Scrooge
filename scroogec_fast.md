# scroogec_fast / scroogec_fast_x86-64

`scroogec_fast` (and its statically-linked build `scroogec_fast_x86-64`) is a high-performance, single-tool native compiler, static shape-gate verifier, and metrics analyzer for the Scrooge programming language (`.sg`).

## Overview

Compiled from `scroogec_fast.nim` (in the development repository), `scroogec_fast` operates as a **100% self-contained, zero-dependency unified tool** that:
- Performs static verification, shape-gate validation, arity checking, stack effect analysis, and type checking.
- Directly compiles Scrooge source code (`.sg`) into standalone native ELF 64-bit x86-64 executables without requiring external Python tools or runtime script files.
- Dumps intermediate target representation files (C source code and binary bytecode) via dedicated CLI flags.
- Bundles the full Scrooge C runtime environment and automatically compiles native binaries via `gcc`.
- Resolves imported standard library modules (`use "strings"`, `use "util"`, etc.) automatically.

## Usage

```bash
scroogec_fast [options] <file.sg>      # build; scroogec_fast --help lists every option, grouped
```

### Options & Flags

- `<file.sg>` *(Required)*: Path to the Scrooge source file to check, verify, or compile.
- `-L <dir>`, `--lib <dir>`, `--library-dir <dir>`: Specifies a custom directory path for resolving standard library lexicons (e.g., `strings.sg`, `util.sg`, `manifest.sm`).
- `-o <outBinary>`, `--output <outBinary>`: Specifies the output native executable binary name (default: `<basename>` derived from `<file.sg>`). A directory in the path that does not exist is made (since v1.88).
- `--dump-c [path]`, `--dump-c:[path]`: Performs static verification, generates and dumps intermediate C source code to `path` (or `<basename>.c`), and exits immediately.
- `--dump-bytecode [path]`, `--dump-bytecode:[path]`, `--dump-scc [path]`: Performs static verification, generates and dumps intermediate binary bytecode (`.scc`) to `path` (or `<basename>.scc`), and exits immediately.
- `--check-only` (one file or several, each under `== FILE`): Only performs static analysis and outputs `ACCEPT` or `REJECT` without emitting a native binary executable.
- A build of a file that defines words but has no top-level code is refused (`NothingRuns`, an error since v2.04): the program would do nothing. `--check-only` accepts such a module.
- `--debug-stack`: Ends the generated `main` with `print_stack()`, so the program prints whatever it left on the stack as `STACK: [...]` after its own output. Off by default.
- `--profile`: Builds a program that prints, at exit, each word's calls, self time and total time, and (since v2.04) the allocations made in the word itself (Blocks, heap cells, arrays) with the memory they asked for, to stderr. A word that copies or allocates far more often than expected shows there.
- `-O0` / `-O1` / `-O2` / `-O3`: the optimisation level passed to gcc (default `-O3`). Behaviour is identical at every level; `-O0` builds a large program about ten times faster, for checking and small tests, but runs much slower (40 times in a numeric kernel): any run that does real work uses the default.
- `--loops`: with a build (or `--dump-c`), print one line per counted loop (`[times| ]`, `[for| ]`) in the program's own words: `fast access through p, w` when its heap reads and writes through outer variables compile to one bounds check each, or `checked access (calls #helper at line N)` naming the word call (or `hrelease`) that prevents it.
- `--no-ptr-check`: leave out the check that a Ptr's allocation has not been released by `hrelease` and reused (one comparison per `hread`/`hwrite`; about 7% in a program made almost only of heap reads). For benchmark builds of a program already tested with the check on; a Ptr to a released slot that has not been reused is still caught.
- Source editing, a whole word at a time: `--words FILE...` (every definition with its size in tokens), `--show NAME FILE`, `--edit FILE` (definitions and steps on stdin: a definition replaces the word of that name or is added after the file's last definition, and `delete NAME`, `rename OLD NEW`, `move NAME MODULE`, `into FILE`; checked, and nothing is written if the program would be rejected; a definition named like a word of another file replaces that word, and the message says so; since v1.98 nothing is written if a file changed while the edit ran, after it was read), `--fmt [--check] FILE` (re-indent only), `--test FILE` (runs the `#test_` words; since v1.99 it also says how many warnings the build has, which `--check-only` lists), `--name-carries FILE` (rewrites loops in the pre-v1.97 form, whose state sat unnamed below the loop, into the named form `[times| i sum |`, in one call: nested loops, `until [ dup ... ] drop` latches, labels for calls of 4 or more inputs). See the skill guide, section 8b.
- Looking things up: `--lookup NAME [FILE]` (a word's signature and comment, a primitive, a library word or one of FILE's), `--apropos TERMS` (words whose description has every term), `--explain [CLASS]` (every error and warning class, or one with its rule, a bad and a good example), `--stack WORD FILE` (the stack at the end of each line of one word), `--unchecked-calls FILE` (calls whose arguments are neither labelled nor passed by a matching name).
- `--test FILE` runs FILE's `#test_` words; `--deep` also tests every module FILE loads; `--test-timeout N` sets the limit in seconds.
- `--log FILE`, with any command, appends one tab-separated line to FILE: the time, seconds, exit status, verdict, errors by class, warnings, arguments and the first error line.
- `--edit MAIN.sg`: give it the program file; a definition replaces the word of that name in whichever module holds it, and the whole program is checked. `--no-check` writes without checking.
- `--labels-required N`: the number of inputs from which a call must name every argument (default 4; 0 makes labels optional).
- `--stage2`: Enables Stage 2 verification rules (enabled by default).
- `--metrics`: Calculates transitive static stack metrics and branch count for the entry point macro and outputs a JSON summary.

## Modes of Operation

### 1. Direct Native Binary Compilation (Default)

Performs static verification. If the code passes verification (`ACCEPT`), `scroogec_fast` automatically compiles the program and all imported library modules into a native ELF executable:

```bash
# Compiles app.sg to native executable ./app
compiler/scroogec_fast app.sg

# Execute native binary directly
./app
```

To specify a custom output binary name:
```bash
compiler/scroogec_fast app.sg -o my_app
```

To specify a custom library search directory:
```bash
compiler/scroogec_fast -L /path/to/library app.sg -o my_app
```

### 2. Intermediate File Dumping (`--dump-c` & `--dump-bytecode`)

Performs static verification (`ACCEPT`), dumps the requested intermediate representation file, and exits without generating an executable:

- **Dump C Source Code:**
  ```bash
  compiler/scroogec_fast --dump-c out.c app.sg
  ```
- **Dump Binary Bytecode (.scc):**
  ```bash
  compiler/scroogec_fast --dump-bytecode out.scc app.sg
  ```

### 3. Static Verification Mode (`--check-only`)

Performs static verification only without compiling a binary executable or dumping intermediate files:

- **Success Output:**
  ```text
  ACCEPT
  ```
- **Failure Output:**
  ```text
  REJECT <ErrorClass> <WordName>
  ```
  *(Example: `REJECT TypeError at`)*

### 4. Metrics Mode (`--metrics`)

Calculates static execution metrics for the entry word in the target file and outputs formatted JSON:

```json
{
  "transient_stack_depth": 4,
  "static_branch_count": 2
}
```

## Key Characteristics

- **100% Self-Contained**: Operates without the retired Python toolchain.
- **Statically Linked**: `scroogec_fast_x86-64` has zero external runtime library dependencies.
- **Intermediate Inspection**: Built-in support for inspecting intermediate C and bytecode output.
- **Library Module Resolution**: Automatically resolves imported library modules from specified or standard library locations (`library/`, `../Scrooge/library/`).
