# Legacy corpus: pre-lexicon engine snapshots

These files are **not expected to compile** under v1.48 and are kept only as
historical snapshots. They must not live in `check/corpus/passing/`, whose
name is a claim that everything in it passes the checker (Gate N enforces
that).

## Why they no longer compile

Each is an early fork of the SQL engine that predates the standard library
lexicons it imports. `impl_scrooge_select1.sg` defines 39 words; the
maintained engine it grew into (`scrooge_dev/programs/impl_scrooge_select1.sg`)
defines 156. Among those 39 are local definitions of `nth`, `reverse`,
`length`, `lst_make`, `lst_get`, `lst_set` and `lst_push` — every one of
which now exists in `util.sg` or `list.sg`, while the file still says
`use "util"` and `use "list"`. Under v1.48 a local definition shadowing an
imported lexicon word is a `DuplicateWordError`, so each of these fails on
the first such collision:

```text
REJECT DuplicateWordError line 14: '#nth' collides with an imported lexicon definition
```

They were left in `passing/` through the v1.48 upgrade, so that directory
had been making a false claim about four of its seven files.

## What to use instead

The maintained engines are in `scrooge_dev/programs/`:
`impl_scrooge_select1.sg`, `impl_scrooge_select2.sg`, `impl_scrooge_select3.sg`
and `impl_scrooge_multi.sg`. All of them ACCEPT, and `select1`/`select2` are
the ones checked against `scrooge_dev/baseline/` in the verification protocol.

## Fixing one, if that is ever wanted

Deleting the seven colliding definitions and relying on the lexicons is *not*
automatically safe: the local `lst_*` words are an older list representation
and are not known to match `list.sg`'s 3-cell header layout. `nth`,
`reverse` and `length` do look equivalent to their lexicon counterparts. The
honest route would be to drop the `use` lines these forks do not actually
need, rather than assume the local and lexicon versions agree.
