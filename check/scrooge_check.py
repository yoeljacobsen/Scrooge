#!/usr/bin/env python3
"""
scrooge check — unified conformance toolchain for Scrooge (v1.34 target).

Runs, in order, halting at the first phase that produces errors:
  0. Reserved-word pass   : reserved keywords may not be used as parameter/
                            frame identifiers (v1.34 rule). Runs BEFORE parsing
                            so it replaces the cryptic "unterminated block"
                            crash with a clear ReservedWordIdentifierError.
  1. Parse                : structural / grammar errors.
  2. Arity  (Track 1)     : net stack effect matches each signature.
  3. Types  (Track 2)     : coarse Scalar/Block/Ptr/Unknown consistency.
  (Lexical soundness — unknown-word detection — is enforced inside Track 1.)

Usage:
  python3 scrooge_check.py FILE.sg [FILE2.sg ...]
  python3 scrooge_check.py --suite        # run the bundled conformance corpus

Exit code 0 iff every file passes every phase.

HONESTY NOTE (kept deliberately, in the spirit of the project):
  Passing `scrooge check` proves parse-correctness, stack-arity balance, and
  coarse-type consistency. It does NOT prove runtime correctness, does NOT
  prove nested-element types (Unknown escape hatch), and does NOT execute the
  program. A separate `--run` mode executes via the reference interpreter for
  cases with a known expected result.
"""

import sys
import re
import os
from scrooge import tokenize, extract_macros, parse_nodes, run, ScroogeError, Macro
from verify import verify
from typecheck import typecheck

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)


def load_manifest(path=None, allowed_lexicons=None):
    """Parse manifest.sm into {word_name: Macro(...)}, filtered to only the
    lexicons in allowed_lexicons (None => none, i.e. no imports resolve)."""
    if path is None:
        path = os.path.join(SCRIPT_DIR, "manifest.sm")
    words = {}
    if allowed_lexicons is None:
        allowed_lexicons = set()
    pattern = re.compile(
        r'tool\s+"([^"]+)"\s+name\s+"([^"]+)"\s+sig\s+"\(([^)]+)\)"')
    try:
        with open(path) as f:
            for line in f:
                m = pattern.search(line)
                if m:
                    lexicon, name, sig = m.groups()
                    if lexicon not in allowed_lexicons:
                        continue  # namespace isolation: skip un-imported lexicons
                    toks = sig.split()
                    d = toks.index('--') if '--' in toks else len(toks)
                    words[name] = Macro(name, toks[:d], toks[d + 1:], [])
    except FileNotFoundError:
        pass
    return words


def used_lexicons(tokens):
    """Return the set of lexicon names named in `use` directives."""
    names = set()
    i = 0
    n = len(tokens)
    while i < n - 1:
        if tokens[i] == 'use':
            if tokens[i + 1].startswith('"'):
                names.add(tokens[i + 1].strip('"'))
                i += 2
            elif tokens[i + 1] == '[':
                j = i + 2
                chars = []
                while j < n and tokens[j] != ']':
                    try:
                        chars.append(chr(int(tokens[j])))
                    except ValueError:
                        pass
                    j += 1
                if chars:
                    names.add(''.join(chars))
                i = j + 1
            else:
                i += 1
        else:
            i += 1
    return names

RESERVED = {
    'use', 'lexicon', 'to', 'from', 'and', 'or', 'not', 'cond', 'else',
    'map', 'fold', 'pk', 'select', 'nil', 'cons', 'pair', 'end',
    'fill', 'len', 'seed', 'rand', 'exp', 'log', 'pow', 'sqrt', 'abs',
    'max', 'min', 'bitand', 'bitor', 'bitxor', 'bitshl', 'bitshr', 'bitnot',
    'hnew', 'hread', 'hwrite', 'print_char', 'print_int', 'roll',
}


class Phase:
    """Result of one check phase."""
    def __init__(self, name, ok, errors):
        self.name = name
        self.ok = ok
        self.errors = errors


def reserved_word_pass(tokens):
    """Scan signatures and '-> [ ... ]' frames for reserved identifiers.
    Runs on the raw token stream so it fires before the parser can choke."""
    errors = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        # signature: #name ( a b -- c )
        if t.startswith('#'):
            j = i + 1
            if j < n and tokens[j] == '(':
                j += 1
                while j < n and tokens[j] != ')':
                    tok = tokens[j]
                    if tok not in ('--',) and tok in RESERVED:
                        errors.append(
                            f"ReservedWordIdentifierError: '{tok}' used as a "
                            f"parameter name in signature of {t}")
                    j += 1
            i = j
            continue
        # frame: -> [ v1 v2 ... ]
        if t == '->':
            j = i + 1
            if j < n and tokens[j] == '[':
                j += 1
                while j < n and tokens[j] != ']':
                    tok = tokens[j]
                    if tok in RESERVED:
                        errors.append(
                            f"ReservedWordIdentifierError: '{tok}' used as a "
                            f"frame alias in a '-> [ ... ]' binding")
                    j += 1
            i = j
            continue
        i += 1
    return errors


def check_source(code):
    """Return list of Phase results, stopping at the first failing phase."""
    phases = []

    # Phase 0: reserved words (pre-parse)
    toks = tokenize(code)
    rerr = reserved_word_pass(toks)
    phases.append(Phase("reserved-word", not rerr, rerr))
    if rerr:
        return phases

    # Resolve `use` imports against the manifest, filtered to imported lexicons
    # only (namespace isolation — un-imported lexicons must NOT resolve).
    needed = used_lexicons(toks)
    extern = load_manifest(allowed_lexicons=needed) if needed else {}

    # Phase 1: parse
    try:
        macros, top = extract_macros(toks)
        parse_nodes(top)
        phases.append(Phase("parse", True, []))
    except ScroogeError as e:
        phases.append(Phase("parse", False, [f"ParseError: {e}"]))
        return phases
    except Exception as e:
        phases.append(Phase("parse", False, [f"ParseError: {type(e).__name__}: {e}"]))
        return phases

    # Phase 2: arity (also catches unknown-word / lexical soundness)
    aerr = verify(code, extern=extern)
    phases.append(Phase("arity", not aerr, aerr))
    if aerr:
        return phases

    # Phase 3: coarse types
    terr = typecheck(code, extern=extern)
    phases.append(Phase("types", not terr, terr))
    return phases


def check_file(path):
    with open(path) as f:
        code = f.read()
    phases = check_source(code)
    passed = all(p.ok for p in phases)
    return passed, phases


def _fmt(path, passed, phases):
    lines = []
    status = "PASS" if passed else "FAIL"
    lines.append(f"[{status}] {path}")
    for p in phases:
        mark = "ok" if p.ok else "XX"
        lines.append(f"    {mark}  {p.name}")
        for e in p.errors:
            lines.append(f"          - {e}")
    return "\n".join(lines)


# Bundled conformance corpus: (path, run_expr, expected_top_of_stack)
# run_expr is appended to the source and executed; None means check-only.
SUITE = [
    ("check/corpus/sudoku.scr",      None, None),
    ("check/corpus/lisp_core_v134.scr", None, None),
    ("library/array.sg",   "[ 2 3 ] arr_make . 42 $ [ 1 2 ] arr_set [ 1 2 ] arr_get", 42),
    ("library/map.sg",     "4 map_make . 100 $ 1 map_set 1 map_get", 100),
    ("library/list.sg",    "4 lst_make . 7 $ 1 lst_set 1 lst_get", 7),
    ("library/record.sg",  "4 rec_make . 99 $ 2 rec_set 2 rec_get", 99),
    ("library/memory.sg",  None, None),
    ("library/util.sg",    "[ 10 20 30 ] reverse length", 3),
    ("library/strings.sg", "use \"strings\" 123 int_to_str [fold| idx acc val _ | acc val + from 0 ]", 150),
    ("check/corpus/test_strings.sg", None, None),
]


def run_suite():
    ok_all = True
    print("=" * 60)
    print("SCROOGE CONFORMANCE SUITE")
    print("=" * 60)
    for path, expr, expected in SUITE:
        full_path = os.path.join(ROOT_DIR, path)
        if not os.path.exists(full_path):
            print(f"[SKIP] {path} (missing)")
            continue
        passed, phases = check_file(full_path)
        print(_fmt(path, passed, phases))
        if passed and expr is not None:
            try:
                sys.setrecursionlimit(100000)
                code = open(full_path).read()
                result = run(code + "  " + expr)
                got = result[-1] if result else None
                run_ok = (got == expected)
                print(f"    {'ok' if run_ok else 'XX'}  run -> {got!r} "
                      f"(expected {expected!r})")
                ok_all = ok_all and run_ok
            except Exception as e:
                print(f"    XX  run -> crash: {type(e).__name__}: {e}")
                ok_all = False
        ok_all = ok_all and passed
    print("=" * 60)
    print("SUITE:", "ALL GREEN" if ok_all else "FAILURES PRESENT")
    print("=" * 60)
    return ok_all


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--suite":
        return 0 if run_suite() else 1
    all_ok = True
    for path in argv:
        passed, phases = check_file(path)
        print(_fmt(path, passed, phases))
        all_ok = all_ok and passed
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
