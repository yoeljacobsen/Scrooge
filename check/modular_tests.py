"""Modular-import regression tests: isolation must be exact.
Un-imported lexicons must NOT resolve; imported ones must."""
import sys
from scrooge_check import check_source
from scrooge import run

def failing_phase(phases):
    for p in phases:
        if not p.ok: return p.name
    return None

ok = True

# 1. Importing memory, using a memory word -> passes
src1 = 'use "memory"\n#z ( ptr -- ) -> [ p ] [ p 0 100 hclear ] end'
p1 = failing_phase(check_source(src1))
r1 = (p1 is None)
print(f"[{'PASS' if r1 else 'FAIL'}] memory import + hclear resolves (got fail={p1})")
ok &= r1

# 2. Importing ONLY memory, using an array word -> must FAIL at arity (isolation)
src2 = 'use "memory"\n#z ( sb -- ptr ) -> [ sb ] [ sb arr_make ] end'
p2 = failing_phase(check_source(src2))
r2 = (p2 == 'arity')
print(f"[{'PASS' if r2 else 'FAIL'}] memory-only import must NOT leak arr_make (got fail={p2})")
ok &= r2

# 3. No imports, using a library word -> must FAIL (unknown)
src3 = '#z ( ptr -- ) -> [ p ] [ p 0 100 hclear ] end'
p3 = failing_phase(check_source(src3))
r3 = (p3 == 'arity')
print(f"[{'PASS' if r3 else 'FAIL'}] no import must NOT resolve hclear (got fail={p3})")
ok &= r3

# 4. Interpreter runs a use-program without crashing
try:
    got = run('use "memory"\n#t ( -- r ) 42 end  t')
    r4 = (got == [42])
except Exception as e:
    r4 = False; got = f"crash {e}"
print(f"[{'PASS' if r4 else 'FAIL'}] interpreter strips use, runs (got {got})")
ok &= r4

print("\nMODULAR SUITE:", "ALL GREEN" if ok else "PROBLEMS")
sys.exit(0 if ok else 1)
