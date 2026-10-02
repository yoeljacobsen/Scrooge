# Scrooge v1.69 Workspace Rules & Agent Directives

This rule file ensures the Google Antigravity environment enforces Scrooge language standards and guidelines when reading, writing, or generating Scrooge code. The authority is the specification, `spec/scrooge_spec_v1_69.txt`; the method is the skill guide, `spec/scrooge_skill.md`. Where this file and the spec disagree, the spec wins; fix this file.

---

## 1. Antigravity Agent Directives

1. **Enforce Postfix Stack Syntax:** Scrooge is strictly a postfix stack language. Infix and imperative constructs (`fn`, `ret`, `while`, `.push`, `.pop`, a C-style `for`) do not exist; the counted loops are `n [times| i | body ]` and `lo hi [for| i | body ]`. Counted loops are `[times| ]` / `[for| ]`; other loops are tail-recursive words, and only direct self-recursion in terminal position runs as a loop.
2. **First-Pass Static Verification Invariant:** Code is only valid when the checker prints `ACCEPT`:
   ```bash
   compiler/scroogec_fast -L library --check-only <file.sg>
   ```
   It reports every error at once, in source order, with line numbers (and columns for `cond` and `end` structure). Fix them all before rebuilding. A build is `compiler/scroogec_fast -L library -o <bin> <file.sg>`.
3. **Immutability Model:** Block updates (`_set`) are copy-on-write: they return a new Block and leave the original valid. Pass updated state down the call chain. The heap (`hnew`/`hread`/`hwrite`) is the one mutable store.
4. **No Reserved Names as Identifiers:** Never use a reserved word as a parameter name or frame alias. The list is in spec Sec.10 (85 words, including every primitive and `dup drop swap rot over`); the compiler enforces exactly that list.
5. **Pointer Arithmetic Protection:** Pointers are opaque (`ptr 1 +` is a `TypeError`). Compute the integer offset first, then pass it: `ptr offset hread`, `val ptr offset hwrite` (the value comes first).
6. **Look Signatures Up, Don't Guess:** `library/manifest.sm` has one typed line per library word (`tool`) and per compiler primitive (`prim`), generated and checked against the compiler.
7. **Small Words, Tested One by One:** Build programs from small words (under about 30 tokens, one job each) combined into larger ones; calls to small words are compiled in place, so splitting costs no speed. Give each word `#test_` words ( -- ok:Scalar ) and run them with `compiler/scroogec_fast -L library --test <file.sg>`. The checker warns `LargeWord` above 60 tokens; split such words (skill guide section 1).

---

## 2. Core Scrooge v1.69 Language Reference

### 2.1 Core Data Types
* **Scalar:** 64-bit signed integer or IEEE double (`42`, `3.14`, `-0.5`, `314e-2`). Mixed math promotes to float.
* **Block:** Ordered, fixed-shape array or record in square brackets, every token whitespace-separated: `[ 1 2 3 ]`, never `[1 2 3]`.
* **Strings:** `"Hi"` becomes the Block `[ 72 105 ]` at tokenization.
* **Ptr, File:** Opaque handles from `hnew` and `fopen`.
* **Type tags:** `Scalar Block Ptr Record Map File Unknown`, exactly these spellings.

### 2.2 Words and Frames
* Define a word: `#name ( a:Scalar b:Block -- r:Scalar ) body end`, in any order (a word may call one defined later). Call by bare name.
* Entry point: `#main ( -- ) ... end`, then `main` at top level.
* Name values with a frame: `-> [ a b ] [ body ]`. A frame's scope runs to the end of the enclosing block, so later code and later sibling frames still see `a` and `b`. The body bracket is therefore optional: `-> [ a b ] a b +` is the same code as `-> [ a b ] [ a b + ]`. The names bracket is not.
* Cond branches, frame bodies and map/fold bodies nest freely. Moving an inner loop or conditional into a named word is good style, not a rule (spec Sec.6).
* A string or data literal right after a frame's names is a value, never the frame's body: `-> [ s ] "Hi" str_print` works.

### 2.3 Operator Registry Highlights
* Stack Shufflers: `dup`, `drop`, `swap`, `rot`, `over`, the only five. `pk`, `roll` and `nip` do not exist (`pk`/`roll` are reserved for a possible future implementation). Prefer frames: shufflers erase types to `Unknown`.
* Block Operations: `cons`, `pair`, `len`, `nil`, and the `_at`/`_get`/`_set` access words (spec Sec.4).
* Heap: `size hnew -> ptr`, `ptr idx hread -> val`, `val ptr idx hwrite`, `hmark`/`hrelease`; bulk `hmove`, `hfill`, `hsort`.
* Records: `#record Name  field Type count ...  end` generates `Name_new`, `Name_size` and typed `Name_field` / `Name_field_set` accessors; use it instead of hand-numbered heap offsets (spec Sec.5).
* Look things up instead of guessing: `compiler/scroogec_fast -L library --lookup NAME [FILE]`, `--apropos TEXT`, `--explain ErrorClass`, `--stack WORD FILE` (the stack after each line).
* Collections: `use "vec"` (a growable `Vec`: vec_new, vec_push, vec_get, vec_set, vec_len, vec_pop; `v 'less vec_sort_by` and `p off n 'less sort_by` sort stably in the order of a word you pass) and `use "dict"` (a `Dict` from integer or string keys: dict_new, dict_set, dict_get, dict_find, dict_get_or, dict_has, dict_del, dict_add). Container first. `x to_str` gives any value as text.
* Codes: `#enum Kw select from where end` (members `Kw_select` .. `Kw_where`, `Kw_count`, `Kw_name`, `Kw_of`/`Kw_raw`) and `#type Row Scalar end` (`Row_of`/`Row_raw`) declare types of their own; a code compared with a plain number, or used in arithmetic, is a TypeError (spec Sec.5).
* Logic: `not` is LOGICAL (`6 not` is `0`); `bitnot` is bitwise (`6 bitnot` is `-7`). `and`/`or` are eager: guard risky work with `cond`, not with `and`/`or`.
* Comparison: `=`, `!=`, `>`, `<` are primitives; `>=` and `<=` come from `use "util"`.
* Clock: `clock_ns ( -- ns:Scalar )`, monotonic nanoseconds; subtract two readings.
* Bits: `bitcount`, `bitctz`, `bitclz` (popcount, trailing and leading zeros; `0` gives 64).
* Sorting: `ptr start count hsort` sorts heap cells in place; `block_sort` (util) sorts a Block in O(n log n).
* Environment: `name getenv -> [ value ok ]` (read-only); `f_expand_home` (file) expands `~/`. Flags: `arg_flag`, `arg_value_or`, `arg_int_or` (args).
* Control Flow:
  - `flag cond [ true-branch ] else [ false-branch ]`. The flag is unbracketed; both branches must have the same net stack effect.
  - `flag cond [ true-branch ]` omits the else-branch, which then means `else [ ]`, so the true-branch must have net effect 0.
  - A closing `?` after the last branch is optional (older code writes `... else [ f ] ?`). A `?` or `else` anywhere else is a ParseError.
  - Iterators: `[map| idx val ctx | body ]` and `[fold| idx acc val ctx | body from init ]` (spec Sec.3).
  - Statements: `a when [ body ]` / `a unless [ body ]` run the body (net effect 0) when a is true / false. Short-circuit values: `a and_then [ b ]` is b if a is true, else 0; `a or_else [ b ]` is 1 if a is true, else b (b evaluated only when needed). `and`/`or` evaluate both sides.
  - Counted loops: `n [times| i | body ]` (i = 0..n-1) and `lo hi [for| i | body ]` (i = lo..hi-1); the body is net 0 and threads accumulators left below the loop (`0 10 [times| i | i + ]`). No `break`: an early-exit loop is a self-recursive word.
* Debugging: `x trace` prints a value and its line to stderr; `flag msg assert` (util) stops on a failed invariant; spec Sec.7 and the skill guide's debugging section.
* Files: `f_read_line` (one pass per line), `fread_into` (bytes into heap cells), `fseek`/`ftell`.
* Learning: learn Scrooge from the spec, the skill guide (sections 0 and 0b: how to learn, how to build) and `library/manifest.sm`, then by running small probe programs; not from generated C or compiler internals.
* Modules: `use "name"` loads your own name.sg beside the program when no library lexicon has that name.
* Editing: `scroogec_fast --words/--show/--replace/--insert-before/--insert-after/--delete/--fmt` edit a whole definition at a time (skill guide 8b), instead of ad-hoc search-and-replace scripts.
* Builds: `-O0` for fast builds while iterating, default `-O3` for measurements; REJECT exits 1.
* Conversions: `to_int`, `float_to_str`, `type_of`; `hnull` for an absent Ptr; `exit` for a status.
* Profiling: build with `--profile` to get each word's calls, self and total time on stderr at exit.
* Output: `print_char`, `print_int`, `x decimals print_float`; `print_fixed` and `int_to_str_pad` in `strings.sg`. A program prints only what it prints; `--debug-stack` adds a final `STACK: [...]` line showing what was left on the stack.

---

## 3. Versioning & Tagging Policy

- **Absolute Version Lockstep:** A release tag (e.g., `v1.55`), applied in both the development repository and this published repository, freezes the compiler, checker, standard library, specification and skill guide together.
- **Spec Changes Trigger Versioning:** A change to the specification (`spec/scrooge_spec_v<major>_<minor>.txt`) or to primitive semantics that results in a new version MUST rename the spec file to the new version and create Git tags matching the version exactly (`v1.55`).
