# Scrooge `check` toolchain (v1.37 target)

A complete, self-contained conformance toolchain for the Scrooge language:
reference interpreter, static verifier (arity + coarse types), modular-import
resolution, manifest integrity checking, and four test batteries.

Every claim about what this toolchain does was established by running it, not
by assertion. The batteries below are the proof; run them.

## Quick start

```
python3 check_all.py          # run the entire battery (the one command that matters)
```

Exit 0 iff all four batteries pass.

Individual tools:

```
python3 scrooge_check.py FILE.sg [FILE2 ...]   # check specific files
python3 scrooge_check.py --suite               # conformance corpus (check + run)
python3 manifest_check.py                      # manifest.sm vs. lib/ sources
python3 negative_tests.py                      # prove each phase rejects bad input
python3 modular_tests.py                       # prove import isolation is exact
```

## Layout

```
scrooge.py          Reference interpreter: tokenizer, two-pass macro loader,
                    tree-walking evaluator with TCO trampoline, `use` stripping.
verify.py           Track 1 — arity checker (net stack effect vs. signature;
                    also catches unknown words). Accepts injected extern sigs.
typecheck.py        Track 2 — coarse type checker (Scalar/Block/Ptr/Unknown),
                    fold init-type inference + body descent. Accepts externs.
scrooge_check.py    Unified driver: reserved-word -> parse -> arity -> types,
                    with manifest-driven `use` import resolution.
manifest_check.py   Cross-checks every manifest.sm signature against the actual
                    word definition in its lib/*.sg source (drift detection).
check_all.py        Runs all four batteries; single CI-style entry point.
negative_tests.py   8 cases, each must fail at the expected phase.
modular_tests.py    4 cases pinning down exact import isolation.
manifest.sm         Flat MCP-style discovery manifest (tool/name/sig/desc lines).
lib/                Verified standard-library lexicons (array, list, map,
                    record, memory).
corpus/             Larger verified programs (sudoku, lisp_core).
```

## The four check phases (scrooge_check.py)

0. **reserved-word** — reserved keywords (`end`, `pair`, `cond`, `use`, ...) may
   not be parameter or frame-alias names. Runs before parsing, so it emits a
   clear `ReservedWordIdentifierError` instead of a cryptic parse crash.
1. **parse** — grammar/structural errors.
2. **arity** — net stack effect must equal each signature; catches unknown
   words and unbalanced `cond` branches. Imported words resolve via the manifest.
3. **types** — coarse type consistency: pointer arithmetic, index-into-scalar,
   fold accumulator type stability.

## Modular imports

`use "lexicon"` at the top of a file:
- is stripped from the executable token stream (in the interpreter AND both
  checkers — they must agree, or a program passes static checks then crashes);
- resolves ONLY the words tagged with that lexicon in `manifest.sm`
  (namespace isolation — importing `memory` does NOT make `array` words visible);
- injects those signatures as *trusted at the call site* (their bodies are not
  re-checked — they are external).

`manifest_check.py` closes the trust gap: it verifies the manifest's declared
signatures actually match the lexicon source files, so a client that passes
`scrooge check` cannot be relying on a manifest that has drifted from `lib/`.

## What passing PROVES and does NOT prove

**Proves:** parse-correctness; stack-arity balance against every signature;
recursion/mutual-recursion consistency under signature trust; absence of
*provable* coarse-type contradictions (pointer arithmetic, scalar indexing,
type-unstable fold accumulators); exact import isolation; manifest-vs-source
agreement.

**Does NOT prove:** runtime correctness (a passing program can compute the wrong
answer — hence the suite also *executes* the lexicons and checks results);
nested-element types (the `Unknown` escape hatch is used wherever coarse tags
can't decide, by design and by decidability necessity); or termination.

## Known limitations (honest)

- **Iterator element types are `Unknown`.** A fold/map body that misuses an
  element's type is not caught. This is the deliberate decidability boundary —
  full element-type inference is the undecidable shape-inference wall documented
  across the project's history. This is the biggest real hole; it is a design
  choice, not an oversight.
- **`manifest_check.py` maps lexicon->file via a hardcoded `LEXICON_FILES`
  table.** The cross-check *mechanism* is sound and tested; the file resolution
  is a stand-in for a real package-path resolver.
- **The corpus is small.** Seven programs won't catch every regression; the
  negative and modular suites exist precisely because a positive-only suite is
  blind to permissiveness bugs (the namespace-pollution bug was one such — it
  made the checker too lenient, which only a negative test detects).

## Current battery status

All four green, verified by running `check_all.py`:
- Conformance: sudoku, lisp_core, and array/list/map/record/memory all pass
  four static phases; the data-structure lexicons also execute to expected
  results.
- Manifest integrity: all 18 declared signatures match their sources.
- Negative: all 8 bad inputs rejected at the correct phase.
- Modular: all 4 isolation cases correct (imports resolve exactly; un-imported
  words do not).
