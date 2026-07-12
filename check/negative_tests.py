"""Negative tests: each must FAIL at the expected phase. A checker that only
passes good code is untrustworthy; these prove each phase has teeth."""
from scrooge_check import check_source

CASES = [
    # (name, source, expected_failing_phase)
    ("reserved param",
     "#t ( a end -- ) -> [ a end ] [ a % end % ] end", "reserved-word"),
    ("unbracketed frame body",
     "#t ( a -- b ) -> [ a ] a a + end", "parse"),
    ("bad arity",
     "#t ( a -- b ) -> [ a ] [ a a ] end", "arity"),
    ("unbalanced cond",
     "#t ( n -- r ) -> [ n ] [ n 0 = ] cond [ 1 ] else [ 1 2 ] ? end", "arity"),
    ("unknown word",
     "#t ( -- r ) -> [ ] [ nonexistent ] end", "arity"),
    ("ptr arithmetic (type)",
     "#t ( -- r ) 4 hnew 1 + end", "types"),
    ("index into scalar (type)",
     "#t ( -- r ) 5 3 : end", "types"),
    ("fold type-shift (type)",
     "#t ( a -- r ) [fold| i acc v _ | acc % v nil cons from 0 ] end", "types"),
]

def failing_phase(phases):
    for p in phases:
        if not p.ok:
            return p.name
    return None

ok = True
for name, src, expected in CASES:
    phases = check_source(src)
    got = failing_phase(phases)
    good = (got == expected)
    ok = ok and good
    print(f"[{'PASS' if good else 'FAIL'}] {name}: failed at {got!r} "
          f"(expected {expected!r})")
print("\nNEGATIVE SUITE:", "ALL GREEN" if ok else "PROBLEMS")
import sys; sys.exit(0 if ok else 1)
