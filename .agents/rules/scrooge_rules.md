# Scrooge v1.51 Workspace Rules & Agent Directives

This rule file ensures the Google Antigravity environment enforces Scrooge language standards and guidelines when reading, writing, or generating Scrooge code. The authority is the specification, `spec/scrooge_spec_v1_51.txt`; the method is the skill guide, `spec/scrooge_skill.md`. Where this file and the spec disagree, the spec wins; fix this file.

---

## 1. Antigravity Agent Directives

1. **Enforce Postfix Stack Syntax:** Scrooge is strictly a postfix stack language. Infix and imperative constructs (`fn`, `ret`, `for`, `while`, `.push`, `.pop`) do not exist. Loops are tail-recursive words; only direct self-recursion in terminal position runs as a loop.
2. **First-Pass Static Verification Invariant:** Code is only valid when the checker prints `ACCEPT`:
   ```bash
   compiler/scroogec_fast -L library --check-only <file.sg>
   ```
   It reports every error at once, in source order, with line numbers (and columns for `cond` and `end` structure). Fix them all before rebuilding. A build is `compiler/scroogec_fast -L library -o <bin> <file.sg>`.
3. **Immutability Model:** Block updates (`_set`) are copy-on-write: they return a new Block and leave the original valid. Pass updated state down the call chain. The heap (`hnew`/`hread`/`hwrite`) is the one mutable store.
4. **No Reserved Names as Identifiers:** Never use a reserved word as a parameter name or frame alias. The list is in spec Sec.10 (72 words, including every primitive and `dup drop swap rot over`); the compiler enforces exactly that list.
5. **Pointer Arithmetic Protection:** Pointers are opaque (`ptr 1 +` is a `TypeError`). Compute the integer offset first, then pass it: `ptr offset hread`, `val ptr offset hwrite` (the value comes first).
6. **Look Signatures Up, Don't Guess:** `library/manifest.sm` has one typed line per library word (`tool`) and per compiler primitive (`prim`), generated and checked against the compiler.

---

## 2. Core Scrooge v1.51 Language Reference

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
* Debugging: `x trace` prints a value and its line to stderr; `flag msg assert` (util) stops on a failed invariant; spec Sec.7 and the skill guide's debugging section.
* Files: `f_read_line` (one pass per line), `fread_into` (bytes into heap cells), `fseek`/`ftell`.
* Profiling: build with `--profile` to get each word's calls, self and total time on stderr at exit.
* Output: `print_char`, `print_int`, `x decimals print_float`; `print_fixed` and `int_to_str_pad` in `strings.sg`. A program prints only what it prints; `--debug-stack` adds a final `STACK: [...]` line showing what was left on the stack.

---

## 3. Versioning & Tagging Policy

- **Absolute Version Lockstep:** A release tag (e.g., `v1.51`), applied in both the development repository and this published repository, freezes the compiler, checker, standard library, specification and skill guide together.
- **Spec Changes Trigger Versioning:** A change to the specification (`spec/scrooge_spec_v<major>_<minor>.txt`) or to primitive semantics that results in a new version MUST rename the spec file to the new version and create Git tags matching the version exactly (`v1.51`).
