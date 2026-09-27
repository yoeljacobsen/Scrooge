# Historical corpus: do not learn Scrooge from these files

Everything under this directory is an old snapshot, kept as a record. None of
it shows how Scrooge is written today, and none of it is checked by any gate.
To learn the language, read the specification (`spec/`), the skill guide
(`spec/scrooge_skill.md`), the standard library (`library/`) and
`examples/args_demo.sg`.

| File | From | State under the current compiler |
|------|------|----------------------------------|
| `sudoku.scr` | an early sudoku peer-relation sketch | ACCEPTs, but in old style: several words work their inputs with shufflers instead of naming them in a frame, and every `cond` ends with `?`, which is now optional |
| `lisp_core_v134.scr` | v1.24 to v1.34, a metacircular evaluator core | ACCEPTs, but in old style: `?` after every `cond`, and it predates the standard library |

The `.scr` extension is historical too. Current Scrooge source files use `.sg`.
