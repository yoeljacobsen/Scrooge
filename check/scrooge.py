"""
Scrooge v1.18 (Interpreter-Ready Standard) — a tree-walking interpreter.

Public API:
    run(code: str, stack=None) -> list
        Execute Scrooge source and return the final stack (list; top == last).

Design notes / deliberate deviations from the spec, stated honestly:
  * The spec's language is "compiler" with a "static shape-gate verification
    pass". This is a *runtime* tree-walking interpreter. Shape gates ( | ... | )
    are PARSED but treated as no-ops (not statically verified). Everything else
    is implemented operationally.
  * Two-pass loading is real: pass 1 registers all `#name` macros (so forward
    references and mutual recursion resolve), pass 2 executes top-level code.
  * `->` frames and the "frame inheritance" / "frame-visible cond" carve-outs
    are implemented via a lexical scope chain that branch/child bodies share.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field


# --------------------------------------------------------------------------
# Values: ints and floats are Python int/float. Arrays are Python lists
# (immutable by convention — we never mutate in place, we build new lists).
# --------------------------------------------------------------------------

class ScroogeError(Exception):
    pass


class _SliceStart:
    """Internal marker: 'to' leaves this so ':' knows it's a slice, not an index."""
    __slots__ = ('start',)
    def __init__(self, start):
        self.start = start


# --------------------------------------------------------------------------
# Tokenizer
# --------------------------------------------------------------------------

# multi-char / symbolic tokens that must stand alone
_FLOAT_RE = re.compile(r'^-?\d+e-?\d+$')      # mantissa notation, e.g. 314e-2, 0e0, 1e-5
_INT_RE   = re.compile(r'^-?\d+$')


def expand_string_literals(source_code: str) -> str:
    """
    Scans for double-quoted string literals and converts them into
    bracketed space-separated ASCII decimal arrays.
    """
    def to_ascii_block(match):
        content = match.group(1)
        bytes_content = content.encode('utf-8').decode('unicode_escape')
        ascii_values = [str(ord(char)) for char in bytes_content]
        return f"[ {' '.join(ascii_values)} ]"

    string_pattern = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
    return re.sub(string_pattern, to_ascii_block, source_code)


def tokenize(code: str):
    code = expand_string_literals(code)
    # strip { ... } comments (non-nested, per spec)
    out = []
    i = 0
    n = len(code)
    buf = []
    while i < n:
        c = code[i]
        if c == '{':
            # flush, skip to matching }
            depth = 1
            i += 1
            while i < n and depth > 0:
                if code[i] == '{':
                    depth += 1
                elif code[i] == '}':
                    depth -= 1
                i += 1
            continue
        buf.append(c)
        i += 1
    text = ''.join(buf)
    # whitespace tokenize; the symbolic tokens are already whitespace-isolated
    # in well-formed Scrooge ( [ ] | -> ? etc. are written with surrounding
    # spaces per the spec's examples).
    raw = text.split()
    # normalize glued iterator openers: '[map|' -> '[' 'map|', '[fold|' -> '[' 'fold|'
    norm = []
    for tok in raw:
        if tok.startswith('[') and len(tok) > 1:
            norm.append('[')
            norm.append(tok[1:])
        else:
            norm.append(tok)
    return norm


# --------------------------------------------------------------------------
# Parser -> nested instruction lists
#
# We parse into a flat list of "nodes". Structured nodes:
#   ('lit', value)
#   ('word', name)                       primitive or macro invocation
#   ('block', [nodes])                   a [ ... ] block (array-literal or closure)
#   ('frame', [varnames], bodyblock)     -> [ vars ] [ body ]
#   ('map', idx,val,ctx, bodyblock)
#   ('fold', idx,val,ctx, bodyblock, initblock-as-nodes)
#   ('cond', trueblock, falseblock)
#   ('gate', raw_tokens)                 | ... |  (parsed, ignored)
# --------------------------------------------------------------------------

@dataclass
class Macro:
    name: str
    inputs: list
    outputs: list
    body: list  # list of nodes


def _parse_block_tokens(tokens, i):
    """tokens[i] == '['. Return (list_of_raw_inner_tokens, index_after_])."""
    assert tokens[i] == '['
    depth = 1
    i += 1
    inner = []
    while i < len(tokens):
        t = tokens[i]
        if t == '[':
            depth += 1
            inner.append(t)
        elif t == ']':
            depth -= 1
            if depth == 0:
                return inner, i + 1
            inner.append(t)
        else:
            inner.append(t)
        i += 1
    raise ScroogeError("unterminated [ block")


def parse_literal(tok):
    if _FLOAT_RE.match(tok):
        # mantissa notation: mantissaEexp
        m, e = tok.split('e')
        return float(int(m) * (10 ** int(e))) if False else float(m) * (10.0 ** int(e))
    if _INT_RE.match(tok):
        return int(tok)
    if tok == 'nil':
        return []
    return None


def parse_nodes(tokens):
    """Parse a flat token list (no macro defs, no top-level # ) into nodes."""
    nodes = []
    i = 0
    N = len(tokens)
    while i < N:
        t = tokens[i]

        if t == '->':
            # -> [ vars ] [ body ]
            if tokens[i+1] != '[':
                raise ScroogeError("-> must be followed by [ vars ]")
            vars_inner, j = _parse_block_tokens(tokens, i+1)
            if j >= N or tokens[j] != '[':
                raise ScroogeError("-> [vars] must be followed by [ body ]")
            body_inner, k = _parse_block_tokens(tokens, j)
            nodes.append(('frame', vars_inner, parse_nodes(body_inner)))
            i = k
            continue

        if t == '[':
            # could be: array-literal/closure block, OR a [map|...] / [fold|...]
            inner, j = _parse_block_tokens(tokens, i)
            if inner and inner[0] == 'map|':
                nodes.append(_parse_map(inner))
            elif inner and inner[0] == 'fold|':
                nodes.append(_parse_fold(inner))
            else:
                # array literal (all primitive literals) or closure (has words)
                nodes.append(('block', parse_nodes(inner)))
            i = j
            continue

        if t == 'cond':
            # cond [ true ] else [ false ] ?
            if tokens[i+1] != '[':
                raise ScroogeError("cond must be followed by [ true ]")
            tb, j = _parse_block_tokens(tokens, i+1)
            if tokens[j] != 'else':
                raise ScroogeError("cond ... expected 'else'")
            if tokens[j+1] != '[':
                raise ScroogeError("else must be followed by [ false ]")
            fb, k = _parse_block_tokens(tokens, j+1)
            if tokens[k] != '?':
                raise ScroogeError("cond ... else ... expected '?'")
            nodes.append(('cond', parse_nodes(tb), parse_nodes(fb)))
            i = k + 1
            continue

        if t == '|':
            # shape gate | ... | — parse and ignore
            j = i + 1
            while j < N and tokens[j] != '|':
                j += 1
            nodes.append(('gate', tokens[i+1:j]))
            i = j + 1
            continue

        # literal?
        lit = parse_literal(t)
        if lit is not None or t == 'nil':
            nodes.append(('lit', lit if lit is not None else []))
            i += 1
            continue

        # otherwise a word (primitive or macro name or 'to'/'from' handled inline)
        nodes.append(('word', t))
        i += 1

    return nodes


def _split_on_bars(inner):
    """inner starts with 'map|' or 'fold|'. Header runs until the next lone '|'."""
    # inner[0] is 'map|' or 'fold|'. Collect header names until we hit '|'.
    header = []
    i = 1
    while i < len(inner) and inner[i] != '|':
        header.append(inner[i])
        i += 1
    if i >= len(inner):
        raise ScroogeError("map/fold header not terminated by |")
    body_tokens = inner[i+1:]  # after the closing header bar
    return header, body_tokens


def _parse_map(inner):
    header, body = _split_on_bars(inner)
    # header: idx val ctx
    if len(header) != 3:
        raise ScroogeError(f"map header must be 'idx val ctx', got {header}")
    idx, val, ctx = header
    return ('map', idx, val, ctx, parse_nodes(body))


def _parse_fold(inner):
    header, body = _split_on_bars(inner)
    if len(header) != 4:
        raise ScroogeError(f"fold header must be 'idx acc val ctx', got {header}")
    idx, acc, val, ctx = header
    # body contains ... from init
    if 'from' not in body:
        raise ScroogeError("fold body must contain 'from init'")
    fi = body.index('from')
    body_tokens = body[:fi]
    init_tokens = body[fi+1:]
    return ('fold', idx, acc, val, ctx, parse_nodes(body_tokens), parse_nodes(init_tokens))


# --------------------------------------------------------------------------
# Macro extraction (pass 1)
# --------------------------------------------------------------------------

def extract_macros(tokens):
    """Return (macros_dict, toplevel_tokens)."""
    macros = {}
    top = []
    i = 0
    N = len(tokens)
    while i < N:
        t = tokens[i]
        if t.startswith('#'):
            name = t[1:]
            # signature: ( inputs -- outputs )
            if tokens[i+1] != '(':
                raise ScroogeError(f"macro {name} missing signature")
            j = i + 2
            sig = []
            while tokens[j] != ')':
                sig.append(tokens[j])
                j += 1
            # sig is like: a b -- c
            if '--' in sig:
                d = sig.index('--')
                inputs, outputs = sig[:d], sig[d+1:]
            else:
                inputs, outputs = sig, []
            # body: everything until matching 'end' (macros don't nest defs)
            j += 1
            body_toks = []
            while tokens[j] != 'end':
                body_toks.append(tokens[j])
                j += 1
            macros[name] = Macro(name, inputs, outputs, parse_nodes(body_toks))
            i = j + 1
        else:
            top.append(t)
            i += 1
    return macros, top


# --------------------------------------------------------------------------
# Evaluator
# --------------------------------------------------------------------------

PRIMS_NULLARY = {'rand'}

class Interp:
    def __init__(self, macros):
        self.macros = macros
        self._rng_state = 0x2545F4914F6CDD1D  # default seed
        self._seeded = False
        self._tail_recall = None

    # simple deterministic LCG for reproducible rand (spec has seed/rand)
    def _rand(self):
        # xorshift64* — deterministic, seedable
        x = self._rng_state & 0xFFFFFFFFFFFFFFFF
        x ^= (x >> 12)
        x ^= (x << 25) & 0xFFFFFFFFFFFFFFFF
        x ^= (x >> 27)
        self._rng_state = x & 0xFFFFFFFFFFFFFFFF
        return ((x * 0x2545F4914F6CDD1D) & 0xFFFFFFFFFFFFFFFF) / float(1 << 64)

    def run_nodes(self, nodes, stack, scope, tail_macro=None):
        i = 0
        N = len(nodes)
        while i < N:
            node = nodes[i]
            kind = node[0]

            if kind == 'lit':
                stack.append(node[1])

            elif kind == 'block':
                # An array literal (all lits) evaluates to a list value.
                # A closure (contains words) is pushed as deferred nodes.
                body = node[1]
                if all(n[0] == 'lit' for n in body):
                    stack.append([n[1] for n in body])
                else:
                    stack.append(('__closure__', body))

            elif kind == 'gate':
                pass  # shape gates: parsed, not verified (documented deviation)

            elif kind == 'frame':
                # -> [vars] [body], with inheritance: child scope chains to `scope`
                varnames = node[1]
                body = node[2]
                child = dict(scope)  # inherit unshadowed aliases
                # consume values: leftmost var = deepest
                nvars = len(varnames)
                if len(stack) < nvars:
                    raise ScroogeError(f"frame {varnames} needs {nvars} values, stack has {len(stack)}")
                vals = [stack.pop() for _ in range(nvars)]
                vals.reverse()
                for name, val in zip(varnames, vals):
                    child[name] = val
                # A frame's body may be followed by more frames / a cond that
                # should see these aliases. We execute the body in `child`, and
                # crucially we continue the REST of this node list in `child`
                # too, so a trailing cond sees the frame aliases and consecutive
                # frames inherit. That matches the spec carve-outs.
                self.run_nodes(body, stack, child)
                scope = child

            elif kind == 'cond':
                flag = stack.pop()
                truthy = (flag != 0 and flag != 0.0)
                branch = node[1] if truthy else node[2]
                is_last_c = (i == N - 1)
                self.run_nodes(branch, stack, scope,
                               tail_macro=tail_macro if is_last_c else None)

            elif kind == 'map':
                self._do_map(node, stack, scope)

            elif kind == 'fold':
                self._do_fold(node, stack, scope)

            elif kind == 'word':
                is_last = (i == N - 1)
                w = node[1]
                if is_last and tail_macro is not None and w in self.macros:
                    # tail call: defer to trampoline instead of recursing
                    self._tail_recall = self.macros[w]
                else:
                    self.do_word(w, stack, scope)

            else:
                raise ScroogeError(f"unknown node {kind}")

            i += 1

    # ---- map/fold ----

    def _do_map(self, node, stack, scope):
        # node = ('map', idx, val, ctx, body)
        _, idxn, valn, ctxn, body = node
        # Stack layout: ctx array [map|...]   (array on top, ctx below if used)
        arr = stack.pop()
        ctxval = None
        if ctxn != '_':
            ctxval = stack.pop()
        out = []
        for i, v in enumerate(arr):
            child = dict(scope)
            child[idxn] = i
            child[valn] = v
            if ctxn != '_':
                child[ctxn] = ctxval
            sub = []
            self.run_nodes(body, sub, child)
            # body contract ( idx val -- val' ): result is top of sub-stack
            out.append(sub[-1])
        stack.append(out)

    def _do_fold(self, node, stack, scope):
        # node = ('fold', idx, acc, val, ctx, body, initnodes)
        _, idxn, accn, valn, ctxn, body, initnodes = node
        arr = stack.pop()
        ctxval = None
        if ctxn != '_':
            ctxval = stack.pop()
        # evaluate init
        isub = []
        self.run_nodes(initnodes, isub, scope)
        acc = isub[-1]
        for i, v in enumerate(arr):
            child = dict(scope)
            child[idxn] = i
            child[accn] = acc
            child[valn] = v
            if ctxn != '_':
                child[ctxn] = ctxval
            sub = []
            self.run_nodes(body, sub, child)
            acc = sub[-1]
        stack.append(acc)

    def do_word(self, w, stack, scope):
        # local alias?
        if w in scope:
            stack.append(scope[w])
            return
        # macro?
        if w in self.macros:
            self.call_macro(self.macros[w], stack)
            return
        # primitives
        self.do_prim(w, stack)

    def call_macro(self, macro: Macro, stack):
        # TCO trampoline: re-run body iteratively when it ends in a self tail-call.
        while True:
            self._tail_recall = None
            self.run_nodes(macro.body, stack, {}, tail_macro=macro.name)
            if self._tail_recall is macro:
                continue
            if self._tail_recall is not None:
                # mutual tail call: switch macro, keep looping
                macro = self._tail_recall
                continue
            break

    # ------------------------------------------------------------------
    # primitives
    # ------------------------------------------------------------------
    def do_prim(self, w, stack):
        s = stack
        if w == '.':
            s.append(s[-1])
        elif w == '%':
            s.pop()
        elif w == '$':
            s[-1], s[-2] = s[-2], s[-1]
        elif w == '@':
            # x y z -> y z x   (rotate top three)
            z = s.pop(); y = s.pop(); x = s.pop()
            s.append(y); s.append(z); s.append(x)
        elif w == ';':
            s.append(s[-2])  # over
        elif w == 'roll':
            n = s.pop()
            s.append(s.pop(-(n+1)))
        elif w == 'pk':
            n = s.pop()
            s.append(s[-(n+1)])
        elif w == 'cons':
            L = s.pop(); x = s.pop()
            s.append([x] + list(L))
        elif w == 'pair':
            cdr = s.pop(); car = s.pop()
            s.append([car, cdr])
        elif w == ':':
            top = s.pop()
            block_or_start = s.pop()
            if isinstance(block_or_start, _SliceStart):
                # slice: block start to end :  -> stack was block, then
                # _SliceStart(start) pushed by 'to', then end pushed, then ':'
                end = top
                start = block_or_start.start
                block = s.pop()
                s.append(list(block[start:end]))   # upper bound exclusive
            else:
                idx = top
                block = block_or_start
                s.append(block[idx])
        elif w == 'to':
            # syntax: block start to end :
            # at 'to', top of stack is `start`, `block` below it. Replace start
            # with a marker so ':' can distinguish slice from index.
            start = s.pop()
            s.append(_SliceStart(start))
        elif w == '+':
            b = s.pop(); a = s.pop(); s.append(a + b)
        elif w == '-':
            b = s.pop(); a = s.pop(); s.append(a - b)
        elif w == '*':
            b = s.pop(); a = s.pop(); s.append(a * b)
        elif w == '/':
            b = s.pop(); a = s.pop()
            if isinstance(a, int) and isinstance(b, int):
                s.append(int(a / b) if (a < 0) ^ (b < 0) and a % b != 0 else a // b)
            else:
                s.append(a / b)
        elif w == '\\':
            b = s.pop(); a = s.pop(); s.append(a % b)
        elif w == '=':
            b = s.pop(); a = s.pop(); s.append(1 if a == b else 0)
        elif w == '!=':
            b = s.pop(); a = s.pop(); s.append(1 if a != b else 0)
        elif w == '>':
            b = s.pop(); a = s.pop(); s.append(1 if a > b else 0)
        elif w == '<':
            b = s.pop(); a = s.pop(); s.append(1 if a < b else 0)
        elif w == 'and':
            b = s.pop(); a = s.pop(); s.append(1 if (a != 0 and b != 0) else 0)
        elif w == 'or':
            b = s.pop(); a = s.pop(); s.append(1 if (a != 0 or b != 0) else 0)
        elif w == 'not':
            a = s.pop(); s.append(1 if a == 0 else 0)
        elif w == 'select':
            flag = s.pop(); vf = s.pop(); vt = s.pop()
            s.append(vt if flag != 0 else vf)
        elif w == 'exp':
            import math
            a = s.pop()
            try:
                r = math.exp(a)
                s.append(min(r, 1e9))
            except OverflowError:
                s.append(1e9)
        elif w == 'log':
            import math
            a = s.pop()
            s.append(-1e9 if a == 0 else math.log(a))
        elif w == 'pow':
            b = s.pop(); a = s.pop(); s.append(a ** b)
        elif w == 'sqrt':
            import math; s.append(math.sqrt(s.pop()))
        elif w == 'abs':
            s.append(abs(s.pop()))
        elif w == 'max':
            b = s.pop(); a = s.pop(); s.append(max(a, b))
        elif w == 'min':
            b = s.pop(); a = s.pop(); s.append(min(a, b))
        elif w == 'fill':
            val = s.pop(); length = s.pop(); s.append([val] * length)
        elif w == 'len':
            val = s.pop()
            if isinstance(val, tuple) and len(val) == 2 and val[0] == '__ptr__':
                s.append(len(val[1]))
            else:
                s.append(len(val))
        elif w == 'seed':
            self._rng_state = (s.pop() & 0xFFFFFFFFFFFFFFFF) or 1
        elif w == 'rand':
            s.append(self._rand())
        elif w == 'hnew':
            size = s.pop(); p = ('__ptr__', [0]*size); s.append(p)
        elif w == 'hread':
            idx = s.pop(); p = s.pop(); s.append(p[1][idx])
        elif w == 'hwrite':
            idx = s.pop(); p = s.pop(); val = s.pop(); p[1][idx] = val
        elif w == 'print_char':
            import sys as _s; _s.stdout.write(chr(s.pop()))
        elif w == 'print_int':
            import sys as _s; _s.stdout.write(str(s.pop()))
        elif w == 'bitand':
            b = s.pop(); a = s.pop(); s.append(a & b)
        elif w == 'bitor':
            b = s.pop(); a = s.pop(); s.append(a | b)
        elif w == 'bitxor':
            b = s.pop(); a = s.pop(); s.append(a ^ b)
        elif w == 'bitshl':
            b = s.pop(); a = s.pop(); val = (a << b) & 0xFFFFFFFFFFFFFFFF; s.append(val - 0x10000000000000000 if val >= 0x8000000000000000 else val)
        elif w == 'bitshr':
            b = s.pop(); a = s.pop(); val = (a % (1 << 64)) >> b; s.append(val - 0x10000000000000000 if val >= 0x8000000000000000 else val)
        elif w == 'bitnot':
            a = s.pop(); val = ~a & 0xFFFFFFFFFFFFFFFF; s.append(val - 0x10000000000000000 if val >= 0x8000000000000000 else val)
        else:
            raise ScroogeError(f"unknown word/primitive: {w!r}")


def _strip_use(tokens):
    out = []; i = 0
    n = len(tokens)
    while i < n:
        if tokens[i] == 'use':
            if i+1 < n and tokens[i+1].startswith('"'):
                i += 2; continue
            elif i+1 < n and tokens[i+1] == '[':
                i += 2
                while i < n and tokens[i] != ']':
                    i += 1
                if i < n:
                    i += 1
                continue
        out.append(tokens[i]); i += 1
    return out


def run(code, stack=None):
    tokens = tokenize(code)
    tokens = _strip_use(tokens)
    macros, top = extract_macros(tokens)
    interp = Interp(macros)
    nodes = parse_nodes(top)
    st = list(stack) if stack else []
    interp.run_nodes(nodes, st, {})
    return st
