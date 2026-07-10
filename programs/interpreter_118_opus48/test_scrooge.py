"""Regression tests for the Scrooge v1.18 interpreter."""
import sys
sys.setrecursionlimit(5000000)
from scrooge import run


def check(name, got, want):
    ok = got == want
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got!r}"
          + ("" if ok else f"  want {want!r}"))
    return ok


def main():
    results = []
    R = lambda n, c, w: results.append(check(n, run(c), w))

    # --- primitives ---
    R("add", "3 4 +", [7])
    R("sub", "10 3 -", [7])
    R("mul", "6 7 *", [42])
    R("intdiv", "17 5 /", [3])
    R("mod", "17 5 \\", [2])
    R("float", "314e-2", [3.14])
    R("promote", "1 2e0 +", [3.0])
    R("dup", "5 .", [5, 5])
    R("drop", "5 6 %", [5])
    R("swap", "1 2 $", [2, 1])
    R("rot", "1 2 3 @", [2, 3, 1])
    R("over", "1 2 ;", [1, 2, 1])
    R("pk", "10 20 30 2 pk", [10, 20, 30, 10])
    R("cons", "7 [ 8 9 ] cons", [[7, 8, 9]])
    R("nil", "nil", [[]])
    R("index", "[ 10 20 30 ] 1 :", [20])
    R("slice", "[ 10 20 30 40 50 ] 1 to 3 :", [[20, 30]])
    R("fill", "3 9 fill", [[9, 9, 9]])
    R("len", "[ 1 2 3 4 ] len", [4])
    R("select_t", "100 200 1 select", [100])
    R("select_f", "100 200 0 select", [200])
    R("cmp", "3 5 <", [1])
    R("and", "1 0 and", [0])
    R("or", "1 0 or", [1])
    R("not", "0 not", [1])
    R("max", "3e0 5e0 max", [5.0])
    R("min", "3e0 5e0 min", [3.0])
    R("abs", "-7 abs", [7])
    R("bitxor", "12 10 bitxor", [6])
    R("bitshl", "1 4 bitshl", [16])

    # --- structured ---
    R("macro", "#dbl ( x -- y ) -> [ x ] [ x x + ] end  21 dbl", [42])
    R("cond_t", "#t ( -- r ) 5 cond [ 1 ] else [ 0 ] ? end  t", [1])
    R("cond_f", "#t ( -- r ) 0 cond [ 1 ] else [ 0 ] ? end  t", [0])
    R("map", "[ 1 2 3 ] [map| idx val _ | val val * ]", [[1, 4, 9]])
    R("map_ctx", "10 [ 1 2 3 ] [map| idx val ctx | val ctx + ]", [[11, 12, 13]])
    R("map_idx", "[ 5 5 5 ] [map| idx val _ | val idx + ]", [[5, 6, 7]])
    R("fold", "[ 1 2 3 4 ] [fold| idx acc val _ | acc val + from 0 ]", [10])
    R("fold_ctx", "3 [ 1 2 3 ] [fold| idx acc val ctx | acc val ctx * + from 0 ]", [18])
    R("frame_inherit", "#f ( a b -- r ) -> [ a b ] [ a b + ] -> [ s ] [ s a * ] end  3 4 f", [21])

    # --- recursion / mutual recursion ---
    R("recursion",
      "#cd ( n a -- s ) -> [ n a ] [ n 0 = ] cond [ a ] else [ n 1 - n a + cd ] ? end  5 0 cd",
      [15])

    passed = sum(results)
    print(f"\n{passed}/{len(results)} passed")
    return passed == len(results)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
