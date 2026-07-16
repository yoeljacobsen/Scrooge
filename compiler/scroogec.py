#!/usr/bin/env python3
import sys
import os
import re
import struct
from dataclasses import dataclass

# --------------------------------------------------------------------------
# Bytecode Opcode Registry (Scrooge v1.43 Byte Specification)
# --------------------------------------------------------------------------
OP_CONST         = 0x01
OP_DUP           = 0x02
OP_DROP          = 0x03
OP_SWAP          = 0x04
OP_ROT           = 0x05
OP_OVER          = 0x06
OP_RET           = 0x07
OP_NIL           = 0x08
OP_ADD           = 0x10
OP_SUB           = 0x11
OP_MUL           = 0x12
OP_DIV           = 0x13
OP_MOD           = 0x14
OP_EQ            = 0x15
OP_NE            = 0x16
OP_GT            = 0x17
OP_LT            = 0x18
OP_AND           = 0x19
OP_OR            = 0x1A
OP_NOT           = 0x1B
OP_SELECT        = 0x1C
OP_HNEW          = 0x20
OP_HREAD         = 0x21
OP_HWRITE        = 0x22
OP_PRINT_CHAR    = 0x30
OP_PRINT_INT     = 0x31
OP_LEN           = 0x24
OP_GET           = 0x25
OP_JUMP_IF_FALSE = 0x40
OP_JUMP          = 0x41
OP_CALL          = 0x42
OP_CONS          = 0x43
OP_PAIR          = 0x44
OP_ENTER_FRAME   = 0x45
OP_LEAVE_FRAME   = 0x46
OP_STORE         = 0x47
OP_LOAD          = 0x48

PRIMITIVE_OPCODES = {
    '.': OP_DUP,
    '%': OP_DROP,
    '$': OP_SWAP,
    '@': OP_ROT,
    ';': OP_OVER,
    '+': OP_ADD,
    '-': OP_SUB,
    '*': OP_MUL,
    '/': OP_DIV,
    '\\': OP_MOD,
    '=': OP_EQ,
    '!=': OP_NE,
    '>': OP_GT,
    '<': OP_LT,
    'and': OP_AND,
    'or': OP_OR,
    'not': OP_NOT,
    'select': OP_SELECT,
    'hnew': OP_HNEW,
    'hread': OP_HREAD,
    'hwrite': OP_HWRITE,
    'print_char': OP_PRINT_CHAR,
    'print_int': OP_PRINT_INT,
    'nil': OP_NIL,
    'cons': OP_CONS,
    'pair': OP_PAIR,
    'len': OP_LEN,
    ':': OP_GET,
}

# --------------------------------------------------------------------------
# Tokenizer & Parser (Adapted from scrooge.py)
# --------------------------------------------------------------------------
class ScroogeError(Exception):
    pass

_FLOAT_RE = re.compile(r'^-?\d+e-?\d+$')
_INT_RE   = re.compile(r'^-?\d+$')

def expand_string_literals(source_code: str) -> str:
    def to_ascii_block(match):
        content = match.group(1)
        bytes_content = content.encode('utf-8').decode('unicode_escape')
        ascii_values = [str(ord(char)) for char in bytes_content]
        return f"[ {' '.join(ascii_values)} ]"
    string_pattern = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
    return re.sub(string_pattern, to_ascii_block, source_code)

def tokenize(code: str):
    code = expand_string_literals(code)
    out = []
    i = 0
    n = len(code)
    buf = []
    while i < n:
        c = code[i]
        if c == '{':
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
    raw = text.split()
    norm = []
    for tok in raw:
        if tok.startswith('[') and len(tok) > 1:
            norm.append('[')
            norm.append(tok[1:])
        else:
            norm.append(tok)
    return norm

def _parse_block_tokens(tokens, i):
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
        m, e = tok.split('e')
        return float(m) * (10.0 ** int(e))
    if _INT_RE.match(tok):
        return int(tok)
    if tok == 'nil':
        return []
    return None

def parse_nodes(tokens):
    nodes = []
    i = 0
    N = len(tokens)
    while i < N:
        t = tokens[i]
        if t == '->':
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
            inner, j = _parse_block_tokens(tokens, i)
            if inner and inner[0] == 'map|':
                nodes.append(_parse_map(inner))
            elif inner and inner[0] == 'fold|':
                nodes.append(_parse_fold(inner))
            else:
                nodes.append(('block', parse_nodes(inner)))
            i = j
            continue
        if t == 'cond':
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
            j = i + 1
            while j < N and tokens[j] != '|':
                j += 1
            nodes.append(('gate', tokens[i+1:j]))
            i = j + 1
            continue
        lit = parse_literal(t)
        if lit is not None or t == 'nil':
            nodes.append(('lit', lit if lit is not None else []))
            i += 1
            continue
        nodes.append(('word', t))
        i += 1
    return nodes

def _split_on_bars(inner):
    header = []
    i = 1
    while i < len(inner) and inner[i] != '|':
        header.append(inner[i])
        i += 1
    if i >= len(inner):
        raise ScroogeError("map/fold header not terminated by |")
    body_tokens = inner[i+1:]
    return header, body_tokens

def _parse_map(inner):
    header, body = _split_on_bars(inner)
    if len(header) != 3:
        raise ScroogeError(f"map header must be 'idx val ctx', got {header}")
    idx, val, ctx = header
    return ('map', idx, val, ctx, parse_nodes(body))

def _parse_fold(inner):
    header, body = _split_on_bars(inner)
    if len(header) != 4:
        raise ScroogeError(f"fold header must be 'idx acc val ctx', got {header}")
    idx, acc, val, ctx = header
    if 'from' not in body:
        raise ScroogeError("fold body must contain 'from init'")
    fi = body.index('from')
    body_tokens = body[:fi]
    init_tokens = body[fi+1:]
    return ('fold', idx, acc, val, ctx, parse_nodes(body_tokens), parse_nodes(init_tokens))

@dataclass
class Macro:
    name: str
    inputs: list
    outputs: list
    body: list

def extract_macros(tokens):
    macros = {}
    top = []
    i = 0
    N = len(tokens)
    while i < N:
        t = tokens[i]
        if t.startswith('#'):
            name = t[1:]
            if tokens[i+1] != '(':
                raise ScroogeError(f"macro {name} missing signature")
            j = i + 2
            sig = []
            while tokens[j] != ')':
                sig.append(tokens[j])
                j += 1
            if '--' in sig:
                d = sig.index('--')
                inputs, outputs = sig[:d], sig[d+1:]
            else:
                inputs, outputs = sig, []
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

def _strip_use(tokens):
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        if tokens[i] == 'use':
            if i+1 < n and tokens[i+1].startswith('"'):
                i += 2
                continue
            elif i+1 < n and tokens[i+1] == '[':
                i += 2
                while i < n and tokens[i] != ']':
                    i += 1
                if i < n:
                    i += 1
                continue
        out.append(tokens[i])
        i += 1
    return out

# --------------------------------------------------------------------------
# Constant Pool Builder
# --------------------------------------------------------------------------
class ConstantPoolBuilder:
    def __init__(self):
        self.pool = []
        self.value_to_idx = {}

    def add_constant(self, val):
        if isinstance(val, list):
            # Pure data block containing other constants
            indices = []
            for item in val:
                indices.append(self.add_constant(item))
            key = ('block', tuple(indices))
            if key in self.value_to_idx:
                return self.value_to_idx[key]
            
            # Cyclic check (enforced structurally since children must exist before block)
            for idx in indices:
                if idx >= len(self.pool):
                    raise ValueError("Cyclic dependency detected in constant pool!")
            
            idx = len(self.pool)
            self.pool.append(key)
            self.value_to_idx[key] = idx
            return idx
        elif isinstance(val, (int, float)):
            if type(val) is int:
                key = ('int', val)
            else:
                key = ('float', val)
            if key in self.value_to_idx:
                return self.value_to_idx[key]
            idx = len(self.pool)
            self.pool.append(key)
            self.value_to_idx[key] = idx
            return idx
        else:
            raise ValueError(f"Invalid constant type for constant pool: {type(val)}")

    def serialize(self) -> bytes:
        out = bytearray()
        out.extend(struct.pack('>I', len(self.pool)))
        for entry in self.pool:
            if entry[0] == 'int':
                out.append(0x01)
                out.extend(struct.pack('>q', entry[1]))
            elif entry[0] == 'float':
                out.append(0x02)
                out.extend(struct.pack('>d', entry[1]))
            elif entry[0] == 'block':
                out.append(0x03)
                indices = entry[1]
                out.extend(struct.pack('>I', len(indices)))
                for idx in indices:
                    out.extend(struct.pack('>I', idx))
        return bytes(out)

# --------------------------------------------------------------------------
# Code Validation & Compiler Emitter
# --------------------------------------------------------------------------
def is_pure_data_node(node):
    kind = node[0]
    if kind == 'lit':
        val = node[1]
        if isinstance(val, (int, float)):
            return True
        if val == []:
            return True
        if isinstance(val, list):
            return True
    elif kind == 'block':
        return all(is_pure_data_node(n) for n in node[1])
    return False

def to_python_value(node):
    kind = node[0]
    if kind == 'lit':
        return node[1]
    if kind == 'block':
        return [to_python_value(n) for n in node[1]]
    raise ValueError("Cannot convert non-data node to Python value")

class ScroogeCompiler:
    def __init__(self, macros):
        self.macros = macros
        self.constant_pool = ConstantPoolBuilder()
        self.symbol_table = {}  # name -> byte_offset
        self.bytecode = bytearray()
        self.calls_to_patch = [] # list of (placeholder_offset, target_name)
        self.scopes = []

    def compile_all(self, top_nodes):
        # 1. Compile user-defined macros/words first
        for name, macro in self.macros.items():
            self.symbol_table[name] = len(self.bytecode)
            self.compile_nodes(macro.body)
            # Emit return at the end of each word
            self.bytecode.append(OP_RET)

        # 2. Compile the top-level main block
        main_offset = len(self.bytecode)
        self.compile_nodes(top_nodes)
        self.bytecode.append(OP_RET) # Halt top-level

        # 3. Patch word calls
        for placeholder_offset, target_name in self.calls_to_patch:
            if target_name not in self.symbol_table:
                raise ScroogeError(f"Undefined word called: {target_name}")
            target_offset = self.symbol_table[target_name]
            self.bytecode[placeholder_offset:placeholder_offset+4] = struct.pack('>I', target_offset)

        return main_offset

    def compile_nodes(self, nodes):
        frames_opened = 0
        for node in nodes:
            kind = node[0]
            if kind == 'lit':
                val = node[1]
                if val == []:
                    # nil primitive
                    self.bytecode.append(OP_NIL)
                else:
                    # Constant pool value
                    idx = self.constant_pool.add_constant(val)
                    self.bytecode.append(OP_CONST)
                    self.bytecode.extend(struct.pack('>I', idx))
            elif kind == 'block':
                # Check if it's pure data or code
                if is_pure_data_node(node):
                    val = to_python_value(node)
                    idx = self.constant_pool.add_constant(val)
                    self.bytecode.append(OP_CONST)
                    self.bytecode.extend(struct.pack('>I', idx))
                else:
                    raise ScroogeError("Nested code blocks (closures) on stack not supported in Step-Zero VM.")
            elif kind == 'word':
                name = node[1]
                resolved = False
                for depth, scope in enumerate(reversed(self.scopes)):
                    if name in scope:
                        local_idx = scope[name]
                        resolved_idx = (depth << 4) | local_idx
                        self.bytecode.append(OP_LOAD)
                        self.bytecode.append(resolved_idx)
                        resolved = True
                        break
                
                if resolved:
                    pass
                elif name in PRIMITIVE_OPCODES:
                    self.bytecode.append(PRIMITIVE_OPCODES[name])
                elif name in self.macros:
                    # Emit call instruction
                    self.bytecode.append(OP_CALL)
                    placeholder = len(self.bytecode)
                    self.bytecode.extend(bytes(4))
                    self.calls_to_patch.append((placeholder, name))
                else:
                    raise ScroogeError(f"Unknown word / primitive: {name}")
            elif kind == 'cond':
                tb, fb = node[1], node[2]
                # Emit OP_JUMP_IF_FALSE with a placeholder target
                self.bytecode.append(OP_JUMP_IF_FALSE)
                jif_placeholder = len(self.bytecode)
                self.bytecode.extend(bytes(4))

                # Emit true branch
                self.compile_nodes(tb)

                # Emit OP_JUMP to skip false branch
                self.bytecode.append(OP_JUMP)
                jmp_placeholder = len(self.bytecode)
                self.bytecode.extend(bytes(4))

                # False branch starts right here
                false_branch_start = len(self.bytecode)
                self.bytecode[jif_placeholder:jif_placeholder+4] = struct.pack('>I', false_branch_start)

                # Emit false branch
                self.compile_nodes(fb)

                # End of conditional starts right here
                end_cond = len(self.bytecode)
                self.bytecode[jmp_placeholder:jmp_placeholder+4] = struct.pack('>I', end_cond)
            elif kind == 'frame':
                vars_list = node[1]
                body_nodes = node[2]
                N = len(vars_list)
                
                scope = {var: idx for idx, var in enumerate(vars_list)}
                self.scopes.append(scope)
                frames_opened += 1
                
                self.bytecode.append(OP_ENTER_FRAME)
                self.bytecode.append(N)
                
                for idx in reversed(range(N)):
                    self.bytecode.append(OP_STORE)
                    self.bytecode.append(idx)
                    
                self.compile_nodes(body_nodes)
            elif kind == 'map':
                idx_var, val_var, ctx_var, body_nodes = node[1], node[2], node[3], node[4]
                
                self.bytecode.append(OP_ENTER_FRAME)
                self.bytecode.append(5)
                
                self.bytecode.append(OP_STORE)
                self.bytecode.append(2)
                
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(2)
                self.bytecode.append(OP_LEN)
                self.bytecode.append(OP_STORE)
                self.bytecode.append(3)
                
                self.bytecode.append(OP_NIL)
                self.bytecode.append(OP_STORE)
                self.bytecode.append(4)
                
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(3)
                self.bytecode.append(OP_CONST)
                idx_1 = self.constant_pool.add_constant(1)
                self.bytecode.extend(struct.pack('>I', idx_1))
                self.bytecode.append(OP_SUB)
                self.bytecode.append(OP_STORE)
                self.bytecode.append(0)
                
                loop_start = len(self.bytecode)
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(0)
                self.bytecode.append(OP_CONST)
                idx_neg1 = self.constant_pool.add_constant(-1)
                self.bytecode.extend(struct.pack('>I', idx_neg1))
                self.bytecode.append(OP_GT)
                
                self.bytecode.append(OP_JUMP_IF_FALSE)
                jmp_to_end_placeholder = len(self.bytecode)
                self.bytecode.extend(bytes(4))
                
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(2)
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(0)
                self.bytecode.append(OP_GET)
                self.bytecode.append(OP_STORE)
                self.bytecode.append(1)
                
                scope = {
                    idx_var: 0,
                    val_var: 1,
                    ctx_var: 2
                }
                self.scopes.append(scope)
                
                self.compile_nodes(body_nodes)
                
                self.scopes.pop()
                
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(4)
                self.bytecode.append(OP_CONS)
                self.bytecode.append(OP_STORE)
                self.bytecode.append(4)
                
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(0)
                self.bytecode.append(OP_CONST)
                idx_1 = self.constant_pool.add_constant(1)
                self.bytecode.extend(struct.pack('>I', idx_1))
                self.bytecode.append(OP_SUB)
                self.bytecode.append(OP_STORE)
                self.bytecode.append(0)
                
                self.bytecode.append(OP_JUMP)
                self.bytecode.extend(struct.pack('>I', loop_start))
                
                loop_end = len(self.bytecode)
                self.bytecode[jmp_to_end_placeholder:jmp_to_end_placeholder+4] = struct.pack('>I', loop_end)
                
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(4)
                
                self.bytecode.append(OP_LEAVE_FRAME)

            elif kind == 'fold':
                idx_var, acc_var, val_var, ctx_var, body_nodes, init_nodes = node[1], node[2], node[3], node[4], node[5], node[6]
                
                self.compile_nodes(init_nodes)
                
                self.bytecode.append(OP_ENTER_FRAME)
                self.bytecode.append(5)
                
                self.bytecode.append(OP_STORE)
                self.bytecode.append(1)
                
                self.bytecode.append(OP_STORE)
                self.bytecode.append(3)
                
                self.bytecode.append(OP_CONST)
                idx_0 = self.constant_pool.add_constant(0)
                self.bytecode.extend(struct.pack('>I', idx_0))
                self.bytecode.append(OP_STORE)
                self.bytecode.append(0)
                
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(3)
                self.bytecode.append(OP_LEN)
                self.bytecode.append(OP_STORE)
                self.bytecode.append(4)
                
                loop_start = len(self.bytecode)
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(0)
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(4)
                self.bytecode.append(OP_LT)
                
                self.bytecode.append(OP_JUMP_IF_FALSE)
                jmp_to_end_placeholder = len(self.bytecode)
                self.bytecode.extend(bytes(4))
                
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(3)
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(0)
                self.bytecode.append(OP_GET)
                self.bytecode.append(OP_STORE)
                self.bytecode.append(2)
                
                scope = {
                    idx_var: 0,
                    acc_var: 1,
                    val_var: 2,
                    ctx_var: 3
                }
                self.scopes.append(scope)
                
                self.compile_nodes(body_nodes)
                
                self.scopes.pop()
                
                self.bytecode.append(OP_STORE)
                self.bytecode.append(1)
                
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(0)
                self.bytecode.append(OP_CONST)
                idx_1 = self.constant_pool.add_constant(1)
                self.bytecode.extend(struct.pack('>I', idx_1))
                self.bytecode.append(OP_ADD)
                self.bytecode.append(OP_STORE)
                self.bytecode.append(0)
                
                self.bytecode.append(OP_JUMP)
                self.bytecode.extend(struct.pack('>I', loop_start))
                
                loop_end = len(self.bytecode)
                self.bytecode[jmp_to_end_placeholder:jmp_to_end_placeholder+4] = struct.pack('>I', loop_end)
                
                self.bytecode.append(OP_LOAD)
                self.bytecode.append(1)
                
                self.bytecode.append(OP_LEAVE_FRAME)
            else:
                raise ScroogeError(f"Unsupported AST node type in compiler: {kind}")
        
        for _ in range(frames_opened):
            self.bytecode.append(OP_LEAVE_FRAME)
            self.scopes.pop()

# --------------------------------------------------------------------------
# CLI Main
# --------------------------------------------------------------------------
def compile_scrooge_source(source_code: str) -> bytes:
    tokens = tokenize(source_code)
    tokens = _strip_use(tokens)
    macros, top = extract_macros(tokens)
    compiler = ScroogeCompiler(macros)
    main_offset = compiler.compile_all(parse_nodes(top))

    # Binary Format Structure:
    # 1. Header: Magic [4 bytes], Version [2 bytes], Main Offset [4 bytes]
    # 2. Constant Pool Section
    # 3. Symbol Table Section
    # 4. Bytecode Section
    header = bytearray()
    header.extend(b'SCG\x2b')
    header.extend(struct.pack('>H', 143))
    header.extend(struct.pack('>I', main_offset))

    cp_bytes = compiler.constant_pool.serialize()

    sym_bytes = bytearray()
    sym_bytes.extend(struct.pack('>I', len(compiler.symbol_table)))
    for name, offset in compiler.symbol_table.items():
        name_encoded = name.encode('utf-8')
        sym_bytes.extend(struct.pack('>I', len(name_encoded)))
        sym_bytes.extend(name_encoded)
        sym_bytes.extend(struct.pack('>I', offset))

    bytecode_bytes = bytes(compiler.bytecode)
    bytecode_section = struct.pack('>I', len(bytecode_bytes)) + bytecode_bytes

    return bytes(header + cp_bytes + sym_bytes + bytecode_section)

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 scroogec.py <input.sg> <output.scc>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()
        binary = compile_scrooge_source(source)
        with open(output_file, 'wb') as f:
            f.write(binary)
    except Exception as e:
        print(f"Compilation error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
