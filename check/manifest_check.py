"""Manifest integrity check: every signature declared in manifest.sm must match
the actual word definition in its lexicon .sg file. Closes the trust gap where
a client program passes `scrooge check` against a manifest that has drifted from
the real library source."""
import re, os
from scrooge import tokenize, extract_macros

# maps lexicon name -> the .sg file that implements it (as present in this repo)
LEXICON_FILES = {
    "memory": "lib/memory.sg",
    "array":  "lib/array.sg",
    "map":    "lib/map.sg",
    "list":   "lib/list.sg",
    "record": "lib/record.sg",
}

def parse_manifest_full(path="manifest.sm"):
    """Return list of (lexicon, name, inputs, outputs)."""
    out = []
    pat = re.compile(r'tool\s+"([^"]+)"\s+name\s+"([^"]+)"\s+sig\s+"\(([^)]+)\)"')
    with open(path) as f:
        for line in f:
            m = pat.search(line)
            if m:
                lex, name, sig = m.groups()
                t = sig.split()
                d = t.index('--') if '--' in t else len(t)
                out.append((lex, name, t[:d], t[d+1:]))
    return out

def check_manifest(path="manifest.sm"):
    errors = []
    entries = parse_manifest_full(path)
    # cache lexicon macros
    libcache = {}
    for lex, name, mins, mouts in entries:
        f = LEXICON_FILES.get(lex)
        if not f or not os.path.exists(f):
            errors.append(f"manifest: lexicon '{lex}' for word '{name}' has no source file to verify against")
            continue
        if f not in libcache:
            libcache[f] = extract_macros(tokenize(open(f).read()))[0]
        macros = libcache[f]
        if name not in macros:
            errors.append(f"manifest: '{name}' declared for lexicon '{lex}' but not defined in {f}")
            continue
        actual = macros[name]
        # compare arity (names may differ; compare counts, which is what arity checking uses)
        if len(actual.inputs) != len(mins) or len(actual.outputs) != len(mouts):
            errors.append(
                f"manifest DRIFT: '{name}' declares ({len(mins)} -- {len(mouts)}) "
                f"but {f} defines ({len(actual.inputs)} -- {len(actual.outputs)})")
    return errors

if __name__ == "__main__":
    e = check_manifest()
    if e:
        print(f"MANIFEST INTEGRITY: {len(e)} problem(s)")
        for x in e: print("  ", x)
    else:
        print("MANIFEST INTEGRITY: all declared signatures match their lexicon source.")
    import sys; sys.exit(1 if e else 0)
