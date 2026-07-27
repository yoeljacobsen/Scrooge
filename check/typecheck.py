r"""
Scrooge v1.28 Track-2 coarse type checker: Scalar / Block / Ptr / Unknown.
Propagates a type tag per stack slot alongside arity, enforcing:
  +,-,*,/,\,and,or,<,>,=,!=  : Scalar Scalar -> Scalar
  hnew  : Scalar -> Ptr
  hread : Ptr Scalar -> Scalar (or Unknown value)
  hwrite: Scalar Ptr Scalar -> ()
  :     : Block Scalar -> (elem)
  len   : Block -> Scalar
Reports the first type contradiction it can prove. Unknown is permissive.
This is intentionally coarse and only flags PROVABLE violations.
"""
from scrooge import tokenize, extract_macros, parse_nodes

S, B, P, R, M, U = 'Scalar', 'Block', 'Ptr', 'Record', 'Map', 'Unknown'

TYPE_MAP = {
    'Scalar': S, 'float': S, 'int': S,
    'Block': B, 'Array': B, 'List': B,
    'Ptr': P,
    'Record': R,
    'Map': M,
    'Unknown': U
}

def parse_sig_type(inp):
    if ':' in inp:
        tname = inp.split(':')[-1]
        return TYPE_MAP.get(tname, U)
    if inp in TYPE_MAP:
        return TYPE_MAP[inp]
    return U

class TypeError_(Exception): pass

# (input types bottom..top, output types) ; None = any/unknown allowed
PRIM_TYPES = {
    '+': ([S,S],[S]), '-': ([S,S],[S]), '*': ([S,S],[S]), '/': ([S,S],[S]),
    '\\': ([S,S],[S]), 'and':([S,S],[S]), 'or':([S,S],[S]),
    '=':([U,U],[S]), '!=':([U,U],[S]), '>':([S,S],[S]), '<':([S,S],[S]),
    'not':([S],[S]),
    'hnew':([S],[P]), 'hread':([P,S],[U]), 'hwrite':([U,P,S],[]),
    'len':([U],[S]), 'cons':([U,B],[B]), 'pair':([U,U],[B]),
    'fill':([S,U],[B]),
    'print_char':([S],[]), 'print_int':([S],[]),
    'bitand':([S,S],[S]), 'bitor':([S,S],[S]), 'bitxor':([S,S],[S]),
    'bitshl':([S,S],[S]), 'bitshr':([S,S],[S]), 'bitnot':([S],[S]),
    '&': ([S,S],[S]), '|': ([S,S],[S]), '^': ([S,S],[S]), '~': ([S],[S]),
}

class TC:
    def __init__(self, macros):
        self.macros = macros
        self.errors = []

    def macro_out_types(self, m):
        return [parse_sig_type(o) for o in m.outputs]

    def check(self, m):
        in_t = [parse_sig_type(i) for i in m.inputs]
        if m.body and m.body[0][0] == 'frame':
            entry_vars = m.body[0][1]
            if len(entry_vars) != len(m.inputs):
                self.errors.append(
                    f"#{m.name}: ArityMismatchError: signature declares {len(m.inputs)} inputs, "
                    f"but entry frame binds {len(entry_vars)} variables ({entry_vars})"
                )
                return
        self._walk(m.body, f"#{m.name}", in_t, {})

    def _walk(self, nodes, where, tstack, env):
        i = 0
        scope = dict(env)
        while i < len(nodes):
            n = nodes[i]; k = n[0]
            if k == 'lit':
                v = n[1]
                tstack.append(B if isinstance(v, list) else S)
            elif k == 'block':
                tstack.append(B)
            elif k == 'gate':
                pass
            elif k == 'frame':
                names = n[1]
                # pop len(names) types, bind
                popped = []
                for _ in names:
                    popped.append(tstack.pop() if tstack else U)
                popped.reverse()
                for nm,t in zip(names,popped): scope[nm]=t
                self._walk(n[2], where, tstack, scope)
            elif k == 'cond':
                tstack.pop() if tstack else None
                s1=list(tstack); self._walk(n[1],where,s1,scope)
                s2=list(tstack); self._walk(n[2],where,s2,scope)
                tstack[:] = s1
            elif k in ('map','fold'):
                if k == 'map':
                    ctxn = n[3]
                    if tstack: tstack.pop()
                    ctxt = tstack.pop() if (ctxn!='_' and tstack) else U
                    # check body: idx=Scalar, val=Unknown(elem), ctx=ctxt
                    benv = dict(scope)
                    benv[n[1]] = S; benv[n[2]] = U
                    if ctxn!='_': benv[ctxn] = ctxt
                    self._walk(n[4], where+'/map', [], benv)
                    tstack.append(B)
                else:
                    ctxn = n[4]; initnodes = n[6]
                    if tstack: tstack.pop()
                    ctxt = tstack.pop() if (ctxn!='_' and tstack) else U
                    acct = self._init_type(initnodes)
                    benv = dict(scope)
                    benv[n[1]] = S; benv[n[2]] = acct; benv[n[3]] = U
                    if ctxn!='_': benv[ctxn] = ctxt
                    # descend and check body ops; also capture its output type
                    bstack = []
                    self._walk(n[5], where+'/fold', bstack, benv)
                    out_t = bstack[-1] if bstack else U
                    # v1.30: body output type must match inferred init type
                    if acct != U and out_t != U and out_t != acct:
                        self.errors.append(
                            f"{where}: fold body outputs {out_t} but init "
                            f"type is {acct} (accumulator type must be stable)")
                    tstack.append(acct)
            elif k == 'word':
                self._word(n[1], nodes, i, where, tstack, scope)
            i += 1

    def _init_type(self, initnodes):
        if not initnodes:
            return U
        n = initnodes[0]
        if n[0] == 'lit':
            return B if isinstance(n[1], list) else S
        if n[0] == 'block':
            return B
        if n[0] == 'word' and n[1] == 'nil':
            return B
        return U

    def _word(self, w, nodes, i, where, tstack, scope):
        if w == 'nil':
            tstack.append(B); return
        if w in ('.', '%', '$', '@', ';', ':'):
            self.errors.append(f"{where}: SyntaxError: Retired symbol '{w}' is invalid in Scrooge v1.47 (use keywords dup, drop, swap, rot, over, at)")
            return
        if w in scope:
            tstack.append(scope[w]); return
        if w in ('to',):
            tstack.append(U); return
        if w in ('at', 'array_at', 'arr_at', 'list_at', 'lst_at', 'block_at'):
            if len(tstack)>=2:
                idx=tstack.pop(); blk=tstack.pop()
                if blk == P:
                    self.errors.append(f"{where}: TypeError: '{w}' index into Ptr (should be hread)")
                elif blk == R:
                    self.errors.append(f"{where}: TypeError: '{w}' index into Record (records are heterogeneous, use _get)")
                elif blk == S:
                    self.errors.append(f"{where}: TypeError: '{w}' index into Scalar (not indexable)")
                tstack.append(U)
            return
        if w in ('array_get', 'arr_get', 'list_get', 'lst_get', 'map_get', 'record_get', 'rec_get', 'block_get'):
            if len(tstack)>=2:
                key=tstack.pop(); coll=tstack.pop()
                tstack.append(U)
            return
        if w in ('array_set', 'arr_set', 'list_set', 'lst_set', 'map_set', 'record_set', 'rec_set', 'block_set'):
            if len(tstack)>=3:
                val=tstack.pop(); key=tstack.pop(); coll=tstack.pop()
                tstack.append(coll if coll in (B, R, M) else B)
            return
        if w in ('dup', 'swap', 'rot', 'over', 'roll', 'pk', 'pick'):
            # structural, keep types roughly; simplistic
            if w == 'dup': tstack.append(tstack[-1] if tstack else U)
            elif w == 'over': tstack.append(tstack[-2] if len(tstack)>=2 else U)
            elif w in ('pk', 'pick'):
                if tstack: tstack.pop()
                tstack.append(U)
            # swap,rot,roll: leave as-is (coarse)
            return
        if w == 'drop':
            if tstack: tstack.pop()
            return
        if w in PRIM_TYPES:
            ins, outs = PRIM_TYPES[w]
            got = []
            for expect in reversed(ins):
                t = tstack.pop() if tstack else U
                got.append((expect,t))
            for expect,t in got:
                if expect!=U and t!=U and t!=expect:
                    self.errors.append(f"{where}: '{w}' expects {expect} but got {t}")
            for o in outs: tstack.append(o)
            return
        if w in self.macros:
            m=self.macros[w]
            for _ in m.inputs:
                if tstack: tstack.pop()
            outs = [parse_sig_type(o) for o in m.outputs]
            for o in outs: tstack.append(o)
            return
        tstack.append(U)

def _strip_use_t(tokens):
    out=[]; i=0
    while i<len(tokens):
        if tokens[i]=='use' and i+1<len(tokens) and tokens[i+1].startswith('"'):
            i+=2; continue
        out.append(tokens[i]); i+=1
    return out

def typecheck(code, extern=None):
    macros,_=extract_macros(_strip_use_t(tokenize(code)))
    extern_names=set(extern.keys()) if extern else set()
    if extern:
        merged=dict(extern); merged.update(macros); macros=merged
    tc=TC(macros)
    tc.extern_names=extern_names
    for name,m in macros.items():
        if name in extern_names: continue
        tc.check(m)
    return tc.errors

if __name__=='__main__':
    import sys
    e=typecheck(open(sys.argv[1]).read())
    print(f"type errors: {len(e)}")
    for x in e: print("  ",x)
