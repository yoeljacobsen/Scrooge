"""Manifest integrity check: every signature declared in manifest.sm must match
the actual word definition in its lexicon .sg file, AND every public word
defined in a lexicon .sg file must be declared in manifest.sm. Closes the
trust gap where a client program passes `scrooge check` against a manifest
that has drifted from the real library source.

Two-way by design:
  - manifest -> source: every declared entry must exist in source with a
    matching arity (drift / stale-entry detection).
  - source -> manifest: every source word NOT explicitly listed as a private
    helper in PRIVATE_HELPERS must be declared in the manifest (missing-entry
    detection). This is the direction that a purely manifest-driven check can
    never perform, and it is what let `util.sg`'s `<=`/`>=` go undeclared.

Word names are matched as opaque strings, not identifiers: Scrooge word names
may be pure operator symbols (`<=`, `>=`, `<`, ...), so nothing here assumes
alphanumeric-only tokens.
"""
import os
import sys
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHECK_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "check"))
if CHECK_DIR not in sys.path:
    sys.path.insert(0, CHECK_DIR)

from scrooge import tokenize, extract_macros  # noqa: E402

# maps lexicon name -> the .sg file that implements it, resolved relative to
# this script's own directory so the check works regardless of invocation cwd
LEXICON_FILES = {
    "memory": "memory.sg",
    "array": "array.sg",
    "map": "map.sg",
    "list": "list.sg",
    "record": "record.sg",
    "util": "util.sg",
    "strings": "strings.sg",
}

# Words defined with '#name ( ... )' in a lexicon source file that are
# intentionally NOT part of the public manifest surface (internal helpers
# used only to implement a public word in the same file, per the "internal
# helper words are not part of the public contract" rule in the language
# spec). Anything defined in source and not listed here must appear in the
# manifest, or the two-way check flags it as missing.
PRIVATE_HELPERS = {
    "util": {"feq_step", "idx_step"},
    "strings": {"sp_step", "its_loop"},
    "memory": {
        "hclear_step", "hclear_loop",
        "hfill_step", "hfill_loop",
        "hadd_step", "hadd_loop",
        "h_find_val_check", "h_find_val_loop",
    },
    "map": {"map_hash"},
    "array": set(),
    "list": set(),
    "record": set(),
}

WORD_DEF_RE = re.compile(r"#(\S+)\s*\(")


def _resolve(f):
    return f if os.path.isabs(f) else os.path.join(SCRIPT_DIR, f)


def parse_manifest_full(path=None):
    """Return list of (lexicon, name, inputs, outputs)."""
    if path is None:
        path = os.path.join(SCRIPT_DIR, "manifest.sm")
    out = []
    pat = re.compile(r'tool\s+"([^"]+)"\s+name\s+"([^"]+)"\s+sig\s+"\(([^)]*)\)"')
    with open(path) as f:
        for line in f:
            m = pat.search(line)
            if m:
                lex, name, sig = m.groups()
                t = sig.split()
                d = t.index('--') if '--' in t else len(t)
                out.append((lex, name, t[:d], t[d + 1:]))
    return out


def extract_source_words(path):
    """Return the set of '#name' word names defined in a lexicon source file,
    including symbol-only names like '<=' -- names are matched as the
    non-whitespace run before '(', not as identifier tokens."""
    with open(path) as f:
        text = f.read()
    text = re.sub(r"\{[^}]*\}", " ", text)  # strip { ... } comments
    return set(WORD_DEF_RE.findall(text))


def check_manifest(path=None):
    errors = []
    entries = parse_manifest_full(path)

    libcache = {}
    manifest_names_by_lexicon = {}

    # Direction 1: manifest -> source (declared entries must exist and match arity)
    for lex, name, mins, mouts in entries:
        manifest_names_by_lexicon.setdefault(lex, set()).add(name)
        f = LEXICON_FILES.get(lex)
        if not f or not os.path.exists(_resolve(f)):
            errors.append(f"manifest: lexicon '{lex}' for word '{name}' has no source file to verify against")
            continue
        if f not in libcache:
            libcache[f] = extract_macros(tokenize(open(_resolve(f)).read()))[0]
        macros = libcache[f]
        if name not in macros:
            errors.append(f"manifest: '{name}' declared for lexicon '{lex}' but not defined in {f}")
            continue
        actual = macros[name]
        if len(actual.inputs) != len(mins) or len(actual.outputs) != len(mouts):
            errors.append(
                f"manifest DRIFT: '{name}' declares ({len(mins)} -- {len(mouts)}) "
                f"but {f} defines ({len(actual.inputs)} -- {len(actual.outputs)})")

    # Direction 2: source -> manifest (every public source word must be declared)
    for lex, f in LEXICON_FILES.items():
        fpath = _resolve(f)
        if not os.path.exists(fpath):
            errors.append(f"source: lexicon '{lex}' has no source file '{f}' to scan for undeclared words")
            continue
        source_words = extract_source_words(fpath)
        private = PRIVATE_HELPERS.get(lex, set())
        declared = manifest_names_by_lexicon.get(lex, set())
        public_words = source_words - private
        missing = sorted(public_words - declared)
        for name in missing:
            errors.append(f"manifest: '{name}' is defined in {f} (lexicon '{lex}') but missing from manifest")
        # words declared in the manifest as public but marked private in source
        misclassified = sorted(declared & private)
        for name in misclassified:
            errors.append(
                f"manifest: '{name}' is declared public for lexicon '{lex}' but is listed as an "
                f"internal helper in PRIVATE_HELPERS -- resolve the contradiction")

    return errors


if __name__ == "__main__":
    e = check_manifest()
    if e:
        print(f"MANIFEST INTEGRITY: {len(e)} problem(s)")
        for x in e:
            print("  ", x)
    else:
        print("MANIFEST INTEGRITY: all declared signatures match their lexicon source, "
              "and all public source words are declared.")
    sys.exit(1 if e else 0)
