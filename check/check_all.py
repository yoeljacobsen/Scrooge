#!/usr/bin/env python3
"""
check_all.py — run the entire Scrooge verification battery in one command.

Runs, in order:
  1. Conformance suite   (scrooge_check.py --suite): parse+arity+types+run
  2. Manifest integrity  (manifest_check.py): manifest.sm vs. lib/*.sg sources
  3. Negative tests      (negative_tests.py): every phase must reject bad input
  4. Modular tests       (modular_tests.py): import isolation is exact

Exit 0 iff all four batteries pass. This is the single command a CI hook or a
"is the language still sound?" check should run.
"""
import subprocess
import sys

BATTERIES = [
    ("Conformance suite",  [sys.executable, "scrooge_check.py", "--suite"]),
    ("Manifest integrity", [sys.executable, "manifest_check.py"]),
    ("Negative tests",     [sys.executable, "negative_tests.py"]),
    ("Modular tests",      [sys.executable, "modular_tests.py"]),
]


def main():
    all_ok = True
    for name, cmd in BATTERIES:
        print(f"\n{'=' * 64}\n  {name}\n{'=' * 64}")
        r = subprocess.run(cmd)
        ok = (r.returncode == 0)
        all_ok = all_ok and ok
        print(f"  -> {name}: {'PASS' if ok else 'FAIL'}")
    print(f"\n{'#' * 64}")
    print("  BATTERY RESULT:", "ALL GREEN" if all_ok else "FAILURES PRESENT")
    print(f"{'#' * 64}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
