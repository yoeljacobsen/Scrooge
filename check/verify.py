"""
Scrooge v1.21 static verifier (section 2, the linter pass).

Implements net-stack-effect analysis with signature-trust at call sites,
cond branch-equality, map/fold body contracts, and literal-only roll/pk.

verify(code) -> list of StaticVerificationError messages (empty == passes).
"""
from scrooge import tokenize, extract_macros, parse_nodes, Macro

# Fixed net deltas for value primitives (pop count, push count) -> net.
# Represented as (pops, pushes).
PRIM_EFFECT = {
    '.': (1, 2), '%': (1, 0), '$': (2, 2), '@': (3, 3), ';': (2, 3),
    'dup': (1, 2), 'drop': (1, 0), 'swap': (2, 2), 'rot': (3, 3), 'over': (2, 3),
    'cons': (2, 1), 'pair': (2, 1),
    'array_at': (2, 1), 'arr_at': (2, 1), 'list_at': (2, 1), 'block_at': (2, 1),
    'array_get': (2, 1), 'arr_get': (2, 1), 'list_get': (2, 1), 'map_get': (2, 1), 'record_get': (2, 1), 'rec_get': (2, 1), 'block_get': (2, 1),
    'array_set': (3, 1), 'arr_set': (3, 1), 'list_set': (3, 1), 'map_set': (3, 1), 'record_set': (3, 1), 'rec_set': (3, 1), 'block_set': (3, 1),
    'hnew': (1, 1), 'hread': (2, 1), 'hwrite': (3, 0),
    'print_char': (1,0), 'print_int': (1,0),
    '+': (2, 1), '-': (2, 1), '*': (2, 1), '/': (2, 1), '\\': (2, 1),
    'and': (2, 1), 'or': (2, 1), 'not': (1, 1),
    '=': (2, 1), '!=': (2, 1), '>': (2, 1), '<': (2, 1),
    'select': (3, 1),
    'exp': (1, 1), 'log': (1, 1), 'pow': (2, 1), 'sqrt': (1, 1),
    'abs': (1, 1), 'max': (2, 1), 'min': (2, 1),
    'fill': (2, 1), 'len': (1, 1), 'seed': (1, 0), 'rand': (0, 1),
    'bitand': (2, 1), 'bitor': (2, 1), 'bitxor': (2, 1),
    'bitshl': (2, 1), 'bitshr': (2, 1), 'bitnot': (1, 1),
    'pk': (1, 2),   # pops the literal index, pushes the dup: net +1
    'roll': (1, 1), # pops index, moves one item to top: net 0 in item count
    # ':' / 'at' and 'to' handled specially (polymorphic) — see analyzer
}


class VerifyError(Exception):
    pass


class Analyzer:
    def __init__(self, macros):
        self.macros = macros
        self.errors = []

    def sig_effect(self, macro):
        return len(macro.outputs) - len(macro.inputs)

    def effect_of_nodes(self, nodes, where, locals_in_scope):
        """Return net stack effect (pushes-pops) of a node sequence.
        locals_in_scope: set of alias names that resolve to a stack push (+1).
        Frame carve-out: a frame's aliases remain visible to all subsequent
        sibling nodes (this models both consecutive-frame inheritance and the
        frame-visible-cond rule)."""
        net = 0
        i = 0
        scope = set(locals_in_scope)
        while i < len(nodes):
            node = nodes[i]
            k = node[0]
            if k == 'lit':
                net += 1
            elif k == 'block':
                net += 1  # pushes one array/closure value
            elif k == 'gate':
                pass
            elif k == 'frame':
                varnames, body = node[1], node[2]
                net -= len(varnames)             # consumes named count
                scope = scope | set(varnames)    # persists to later siblings
                net += self.effect_of_nodes(body, where, scope)
            elif k == 'cond':
                te = self.effect_of_nodes(node[1], where, scope)
                fe = self.effect_of_nodes(node[2], where, scope)
                net -= 1  # cond pops the flag
                if te != fe:
                    self.errors.append(
                        f"{where}: cond branches have unequal net effect "
                        f"(true={te}, false={fe})")
                net += te
            elif k == 'map':
                ctxn = node[3]
                net -= (1 if ctxn == '_' else 2)
                net += 1
                self.check_iter_body('map', node, where, scope)
            elif k == 'fold':
                ctxn = node[4]
                net -= (1 if ctxn == '_' else 2)
                net += 1
                self.check_iter_body('fold', node, where, scope)
            elif k == 'word':
                net += self.word_effect(node[1], nodes, i, where, scope)
            i += 1
        return net

    def word_effect(self, w, nodes, i, where, locals_in_scope):
        if w in locals_in_scope:
            return 1  # alias reference pushes its value
        if w in (':', 'at'):
            # polymorphic: slice terminator (net handled by 'to') or index.
            # Heuristic: if a 'to' word precedes in this sequence unmatched,
            # this ':' closes a slice (block start end -> block[start:end]):
            # net for the whole 'start to end :' is -2. We model 'to' as -1
            # and ':' as -1 so the pair sums to -2; a lone ':' index is -1.
            return -1
        if w == 'to':
            return -1
        if w in PRIM_EFFECT:
            pops, pushes = PRIM_EFFECT[w]
            # literal-arg check for roll/pk
            if w in ('roll', 'pk'):
                if i == 0 or nodes[i-1][0] != 'lit':
                    self.errors.append(
                        f"{where}: '{w}' requires an immediate literal index "
                        f"argument (got non-literal)")
            return pushes - pops
        if w in self.macros:
            return self.sig_effect(self.macros[w])
        self.errors.append(f"{where}: unknown word '{w}'")
        return 0

    def check_iter_body(self, kind, node, where, locals_in_scope):
        if kind == 'map':
            _, idxn, valn, ctxn, body = node
            locals_ = set(locals_in_scope) | {idxn, valn}
            if ctxn != '_':
                locals_.add(ctxn)
            eff = self.effect_of_nodes(body, where + f"/{kind}-body", locals_)
            if eff != 1:
                self.errors.append(
                    f"{where}: map body must have net effect +1 "
                    f"(idx val -- val'); got {eff}")
        else:
            _, idxn, accn, valn, ctxn, body, initn = node
            locals_ = set(locals_in_scope) | {idxn, accn, valn}
            if ctxn != '_':
                locals_.add(ctxn)
            eff = self.effect_of_nodes(body, where + f"/{kind}-body", locals_)
            if eff != 1:
                self.errors.append(
                    f"{where}: fold body must have net effect +1 "
                    f"(idx acc val -- acc'); got {eff}")

    def check_macro(self, macro):
        eff = self.effect_of_nodes(macro.body, f"#{macro.name}", set())
        want = self.sig_effect(macro)
        if eff != want:
            self.errors.append(
                f"#{macro.name}: body net effect {eff} != signature "
                f"({len(macro.inputs)} -- {len(macro.outputs)}) = {want}")


def _strip_use(tokens):
    out = []; i = 0
    while i < len(tokens):
        if tokens[i] == 'use' and i+1 < len(tokens) and tokens[i+1].startswith('"'):
            i += 2; continue
        out.append(tokens[i]); i += 1
    return out


def verify(code, extern=None):
    tokens = tokenize(code)
    # strip leading `use "lex"` directives before parsing
    tokens = _strip_use(tokens)
    macros, top = extract_macros(tokens)
    extern_names = set(extern.keys()) if extern else set()
    if extern:
        merged = dict(extern); merged.update(macros); macros = merged
    az = Analyzer(macros)
    az.extern_names = extern_names
    for name, m in macros.items():
        if name in az.extern_names:
            continue
        az.check_macro(m)
    return az.errors


if __name__ == "__main__":
    import sys
    errs = verify(open(sys.argv[1]).read())
    if errs:
        print(f"StaticVerificationError ({len(errs)}):")
        for e in errs:
            print("  ", e)
        sys.exit(1)
    print("PASS: all macros satisfy their signatures.")
