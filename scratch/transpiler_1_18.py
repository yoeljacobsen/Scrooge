import re
import sys
import math

def strip_comments(code):
    # Remove Forth-style comments (...)
    code = re.sub(r'\(.*?\)', '', code, flags=re.DOTALL)
    # Remove stack state comments {...}
    code = re.sub(r'\{.*?\}', '', code, flags=re.DOTALL)
    return code

def tokenize(code):
    code = strip_comments(code)
    token_specification = [
        ('MACRO_DEF',  r'#[a-zA-Z_][\w\.]*'),
        ('ARROW',      r'->'),
        ('COND',       r'\bcond\b'),
        ('ELSE',       r'\belse\b'),
        ('SELECT',     r'\bselect\b'),
        ('PK',         r'\bpk\b'),
        ('TO',         r'\bto\b'),
        ('FROM',       r'\bfrom\b'),
        ('MAP_START',  r'\[map\|'),
        ('FOLD_START', r'\[fold\|'),
        ('BAR',        r'\|'),
        ('LBRACKET',   r'\['),
        ('RBRACKET',   r'\]'),
        ('FLOAT',      r'-?\d+e-?\d+'), # e.g. 314e-2
        ('INT',        r'-?\d+'),
        ('OP_COMP',    r'!=|==|='),
        ('OP_LOGIC',   r'[><]'),
        ('OP_ARITH',   r'[-+*/\\%$.@;:\?]'), # modulo \, drop %, dup ., swap $, rot @, over ;, lookup :
        ('WORD',       r'[a-zA-Z_][\w\.]*'),
        ('SKIP',       r'[ \t\n\r]+'),
        ('MISMATCH',   r'.'),
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    tokens = []
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f"Unexpected character {value!r}")
        else:
            tokens.append((kind, value))
    return tokens

class Block:
    def __init__(self, elements):
        self.elements = elements
    def __repr__(self):
        return f"Block({self.elements})"

class FoldBlock:
    def __init__(self, elements):
        self.elements = elements
    def __repr__(self):
        return f"FoldBlock({self.elements})"

class MapBlock:
    def __init__(self, elements):
        self.elements = elements
    def __repr__(self):
        return f"MapBlock({self.elements})"

def parse(tokens):
    stack = [[]]
    block_types = []
    for kind, val in tokens:
        if kind == 'LBRACKET':
            stack.append([])
            block_types.append('STANDARD')
        elif kind == 'FOLD_START':
            stack.append([])
            block_types.append('FOLD')
        elif kind == 'MAP_START':
            stack.append([])
            block_types.append('MAP')
        elif kind == 'RBRACKET':
            if len(stack) < 2:
                raise RuntimeError("Unmatched closing bracket ']'")
            completed = stack.pop()
            btype = block_types.pop()
            if btype == 'STANDARD':
                stack[-1].append(Block(completed))
            elif btype == 'FOLD':
                stack[-1].append(FoldBlock(completed))
            elif btype == 'MAP':
                stack[-1].append(MapBlock(completed))
        else:
            stack[-1].append((kind, val))
    if len(stack) != 1:
        raise RuntimeError("Unmatched opening bracket")
    return stack[0]

def sanitize_name(name):
    return name.replace('.', '_').replace('*', '_star')

def indent_code(code, spaces=4):
    indent = " " * spaces
    return "\n".join(indent + line if line.strip() else line for line in code.split("\n"))

def extract_macros(parsed):
    macros = {}
    main_items = []
    i = 0
    while i < len(parsed):
        item = parsed[i]
        if isinstance(item, tuple) and item[0] == 'MACRO_DEF':
            macro_name = item[1][1:] # strip '#'
            body = []
            i += 1
            while i < len(parsed):
                curr = parsed[i]
                if isinstance(curr, tuple) and curr[0] == 'WORD' and curr[1] == 'end':
                    break
                body.append(curr)
                i += 1
            macros[macro_name] = body
            i += 1 # skip 'end'
            continue
        main_items.append(item)
        i += 1
    return macros, main_items

def parse_signatures(code):
    signatures = {}
    pattern = r'#([a-zA-Z_][\w\.]*)\s*\((.*?)\)'
    for name, sig_content in re.findall(pattern, code):
        if '--' in sig_content:
            inputs_part = sig_content.split('--')[0]
        else:
            inputs_part = sig_content
        inputs = [v.strip() for v in inputs_part.split()]
        inputs = [v for v in inputs if v]
        signatures[name] = inputs
    return signatures

def transpile(scrooge_code: str) -> str:
    macro_signatures = parse_signatures(scrooge_code)
    tokens = tokenize(scrooge_code)
    parsed = parse(tokens)
    macros, main_items = extract_macros(parsed)
    
    binding_counter = [0]
    
    primitive_op_mappings = {
        '+': 'op_add',
        '-': 'op_sub',
        '*': 'op_mul',
        '/': 'op_div',
        '\\': 'op_mod',
        '=': 'op_eq',
        '==': 'op_eq',
        '!=': 'op_ne',
        '>': 'op_gt',
        '<': 'op_lt',
        'and': 'op_and',
        'or': 'op_or',
        'not': 'op_not',
        '.': 'op_dup',
        '%': 'op_drop',
        '$': 'op_swap',
        '@': 'op_rot',
        ';': 'op_over',
        'roll': 'op_roll',
        'pk': 'op_pk',
        'cons': 'op_cons',
        ':': 'op_get',
        'to': 'op_to',
        'select': 'op_select',
        '?': 'op_ifelse',
        'len': 'op_len',
        'exp': 'op_exp',
        'log': 'op_log',
        'pow': 'op_pow',
        'sqrt': 'op_sqrt',
        'abs': 'op_abs',
        'max': 'op_max',
        'min': 'op_min',
        'fill': 'op_fill',
        'seed': 'op_seed',
        'rand': 'op_rand',
        'bitand': 'op_bitand',
        'bitor': 'op_bitor',
        'bitxor': 'op_bitxor',
        'bitshl': 'op_bitshl',
        'bitshr': 'op_bitshr',
        'bitnot': 'op_bitnot',
    }

    def is_static_array(block):
        for el in block.elements:
            if isinstance(el, (Block, FoldBlock, MapBlock)):
                return False
            kind, val = el
            if kind not in ('INT', 'FLOAT', 'STRING', 'BIN', 'HEX') and val != 'nil':
                return False
        return True

    def transpile_static_array(block):
        elements = []
        for el in block.elements:
            kind, val = el
            if val == 'nil':
                elements.append("[]")
            elif kind == 'INT':
                elements.append(val)
            elif kind == 'FLOAT':
                # Convert scientific notation to python float representation
                elements.append(str(float(val)))
            elif kind == 'STRING':
                elements.append(val)
            elif kind == 'BIN':
                elements.append(str(int(val[1:], 2)))
            elif kind == 'HEX':
                elements.append(str(int(val[1:], 16)))
        return f"[{', '.join(elements)}]"

    def transpile_items(items, var_mappings, lex_funcs, sig_vars=None):
        code_parts = []
        local_defs = []
        i = 0
        while i < len(items):
            item = items[i]
            if isinstance(item, tuple):
                kind, val = item
                if kind == 'COND' or kind == 'ELSE':
                    # Ignore cond and else keywords at runtime
                    i += 1
                    continue
                elif kind == 'INT':
                    code_parts.append(val)
                elif kind == 'FLOAT':
                    code_parts.append(str(float(val)))
                elif kind == 'STRING':
                    code_parts.append(val)
                elif kind == 'BIN':
                    code_parts.append(str(int(val[1:], 2)))
                elif kind == 'HEX':
                    code_parts.append(str(int(val[1:], 16)))
                elif kind == 'ARROW':
                    # Parse compile-time binding -> [ vars ] [ body ]
                    if i + 2 < len(items) and isinstance(items[i+1], Block) and isinstance(items[i+2], Block):
                        vars_block = items[i+1]
                        body_block = items[i+2]
                        vars_list = [v[1] for v in vars_block.elements if v[0] == 'WORD']
                        
                        new_mappings = dict(var_mappings)
                        pop_lines = []
                        for v in reversed(vars_list):
                            unique_name = f"{sanitize_name(v)}_{binding_counter[0] + 1}"
                            binding_counter[0] += 1
                            new_mappings[v] = var_mappings.get(v, []) + [unique_name]
                            pop_lines.append(f"{unique_name} = stack.pop()")
                            
                        body_code, body_defs = transpile_items(body_block.elements, new_mappings, lex_funcs, sig_vars)
                        
                        # Pack all popped variables and body run into a local function closure
                        binding_counter[0] += 1
                        helper_func_name = f"binding_{binding_counter[0]}"
                        helper_lines = [
                            f"def {helper_func_name}(stack):",
                        ]
                        if body_defs:
                            helper_lines.append(indent_code("\n".join(body_defs), 4))
                        helper_lines.append(indent_code("\n".join(pop_lines), 4))
                        helper_lines.append(indent_code(body_code, 4) if body_code else "    pass")
                        
                        local_defs.append("\n".join(helper_lines))
                        code_parts.append(helper_func_name)
                        i += 3
                        continue
                    else:
                        raise RuntimeError("Invalid compile-time binding arrow syntax")
                elif val == 'nil':
                    code_parts.append("lambda stack: stack.append([])")
                elif val == '_':
                    code_parts.append("lambda stack: stack.append(None)")
                elif val in primitive_op_mappings:
                    code_parts.append(primitive_op_mappings[val])
                elif val in var_mappings:
                    # Retrieve local variable from environment
                    unique_name = var_mappings[val][-1]
                    code_parts.append(f"lambda stack, {unique_name}={unique_name}: stack.append({unique_name})")
                elif sig_vars is not None and val in sig_vars:
                    offset = sig_vars[val]
                    code_parts.append(f"lambda stack: stack.append(stack[-1 - {offset}])")
                elif val in macros:
                    # Invoke top-level macro
                    code_parts.append(f"macro_{sanitize_name(val)}")
                else:
                    # Forward-referenced macro/word
                    code_parts.append(f"macro_{sanitize_name(val)}")
            elif isinstance(item, Block):
                if is_static_array(item):
                    arr_str = transpile_static_array(item)
                    code_parts.append(f"lambda stack: stack.append({arr_str})")
                else:
                    # Compile closure
                    binding_counter[0] += 1
                    func_name = f"binding_{binding_counter[0]}"
                    body_code, body_defs = transpile_items(item.elements, var_mappings, lex_funcs, sig_vars)
                    
                    func_lines = [
                        f"def {func_name}(stack):",
                    ]
                    if body_defs:
                        func_lines.append(indent_code("\n".join(body_defs), 4))
                    func_lines.append(indent_code(body_code, 4) if body_code else "    pass")
                    
                    local_defs.append("\n".join(func_lines))
                    code_parts.append(f"lambda stack: stack.append({func_name})")
            elif isinstance(item, FoldBlock):
                # Parse Fold Block
                bar_idx = -1
                from_idx = -1
                for idx, el in enumerate(item.elements):
                    if isinstance(el, tuple):
                        if el[0] == 'BAR' or el[1] == '|':
                            bar_idx = idx
                        elif el[0] == 'FROM' or el[1] == 'from':
                            from_idx = idx
                            
                if bar_idx == -1 or from_idx == -1:
                    raise RuntimeError("Invalid FoldBlock structure")
                    
                vars_tokens = item.elements[:bar_idx]
                body_elements = item.elements[bar_idx+1:from_idx]
                init_elements = item.elements[from_idx+1:]
                
                var_names = [v[1] for v in vars_tokens if v[0] == 'WORD']
                
                new_mappings = dict(var_mappings)
                i_name = f"i_{binding_counter[0] + 1}"
                a_name = f"a_{binding_counter[0] + 2}"
                v_name = f"v_{binding_counter[0] + 3}"
                binding_counter[0] += 3
                
                new_mappings[var_names[0]] = var_mappings.get(var_names[0], []) + [i_name]
                new_mappings[var_names[1]] = var_mappings.get(var_names[1], []) + [a_name]
                new_mappings[var_names[2]] = var_mappings.get(var_names[2], []) + [v_name]
                
                has_ctx = (var_names[3] != '_')
                if has_ctx:
                    c_name = f"c_{binding_counter[0] + 1}"
                    binding_counter[0] += 1
                    new_mappings[var_names[3]] = var_mappings.get(var_names[3], []) + [c_name]
                    
                init_code, init_defs = transpile_items(init_elements, var_mappings, lex_funcs, sig_vars)
                body_code, body_defs = transpile_items(body_elements, new_mappings, lex_funcs, sig_vars)
                
                fold_func_name = f"fold_{binding_counter[0]}"
                indent = "    "
                
                fold_lines = [f"def {fold_func_name}(stack):"]
                nested = []
                if init_defs: nested.extend(init_defs)
                if body_defs: nested.extend(body_defs)
                if nested:
                    fold_lines.append(indent_code("\n".join(nested), 4))
                    
                fold_lines.append(f"{indent}target = stack.pop()")
                if has_ctx:
                    fold_lines.append(f"{indent}{c_name} = stack.pop()")
                if init_code:
                    fold_lines.append(indent_code(init_code, 4))
                else:
                    fold_lines.append(f"{indent}stack.append(0)")
                fold_lines.append(f"{indent}{a_name} = stack.pop()")
                fold_lines.append(f"{indent}for idx, val in enumerate(target):")
                fold_lines.append(f"{indent}    {i_name} = idx")
                fold_lines.append(f"{indent}    {v_name} = val")
                if body_code:
                    fold_lines.append(indent_code(body_code, 8))
                fold_lines.append(f"{indent}    {a_name} = stack.pop()")
                fold_lines.append(f"{indent}stack.append({a_name})")
                
                local_defs.append("\n".join(fold_lines))
                code_parts.append(fold_func_name)
            elif isinstance(item, MapBlock):
                # Parse Map Block
                bar_idx = -1
                for idx, el in enumerate(item.elements):
                    if isinstance(el, tuple) and (el[0] == 'BAR' or el[1] == '|'):
                        bar_idx = idx
                        break
                        
                if bar_idx == -1:
                    raise RuntimeError("Invalid MapBlock structure")
                    
                vars_tokens = item.elements[:bar_idx]
                body_elements = item.elements[bar_idx+1:]
                
                var_names = [v[1] for v in vars_tokens if v[0] == 'WORD']
                
                new_mappings = dict(var_mappings)
                i_name = f"i_{binding_counter[0] + 1}"
                v_name = f"v_{binding_counter[0] + 2}"
                binding_counter[0] += 2
                
                new_mappings[var_names[0]] = var_mappings.get(var_names[0], []) + [i_name]
                new_mappings[var_names[1]] = var_mappings.get(var_names[1], []) + [v_name]
                
                has_ctx = (var_names[2] != '_')
                if has_ctx:
                    c_name = f"c_{binding_counter[0] + 1}"
                    binding_counter[0] += 1
                    new_mappings[var_names[2]] = var_mappings.get(var_names[2], []) + [c_name]
                    
                body_code, body_defs = transpile_items(body_elements, new_mappings, lex_funcs, sig_vars)
                
                map_func_name = f"map_{binding_counter[0]}"
                indent = "    "
                
                map_lines = [f"def {map_func_name}(stack):"]
                if body_defs:
                    map_lines.append(indent_code("\n".join(body_defs), 4))
                map_lines.append(f"{indent}target = stack.pop()")
                if has_ctx:
                    map_lines.append(f"{indent}{c_name} = stack.pop()")
                map_lines.append(f"{indent}res = []")
                map_lines.append(f"{indent}for idx, val in enumerate(target):")
                map_lines.append(f"{indent}    {i_name} = idx")
                map_lines.append(f"{indent}    {v_name} = val")
                if body_code:
                    map_lines.append(indent_code(body_code, 8))
                map_lines.append(f"{indent}    res.append(stack.pop())")
                map_lines.append(f"{indent}stack.append(res)")
                
                local_defs.append("\n".join(map_lines))
                code_parts.append(map_func_name)
                
            i += 1
            
        # Compile direct execution elements
        steps = []
        for p in code_parts:
            # If the item is digits, floats, or variables, push them. Otherwise execute them.
            if re.match(r'^-?\d+(\.\d+)?$', p) or p.startswith('"'):
                steps.append(f"stack.append({p})")
            elif p.startswith("lambda stack"):
                steps.append(f"({p})(stack)")
            else:
                steps.append(f"execute({p}, stack)")
        return "\n".join(steps), local_defs

    # Compile macros
    macro_defs = []
    for name, body in macros.items():
        # Compile body with signature variables
        inputs = macro_signatures.get(name, [])
        sig_vars = {var_name: offset for offset, var_name in enumerate(reversed(inputs))}
        body_code, body_defs = transpile_items(body, {}, {}, sig_vars)
        func_lines = [
            f"def macro_{sanitize_name(name)}(stack):",
        ]
        if body_defs:
            func_lines.append(indent_code("\n".join(body_defs), 4))
        func_lines.append(indent_code(body_code, 4) if body_code else "    pass")
        macro_defs.append("\n".join(func_lines))
        
    # Compile main execution body
    main_code, main_defs = transpile_items(main_items, {}, {})
    
    # Construct complete python program code
    py_lines = [
        "# Transpiled Scrooge v1.18 Code",
        "import math",
        "import sys",
        "",
        "# Runtime Helper Functions",
        "def execute(blk, stack):",
        "    if callable(blk):",
        "        blk(stack)",
        "    elif isinstance(blk, list):",
        "        for item in blk:",
        "            if callable(item):",
        "                item(stack)",
        "            else:",
        "                stack.append(item)",
        "    else:",
        "        stack.append(blk)",
        "",
        "def op_add(stack): b = stack.pop(); a = stack.pop(); stack.append(a + b)",
        "def op_sub(stack): b = stack.pop(); a = stack.pop(); stack.append(a - b)",
        "def op_mul(stack): b = stack.pop(); a = stack.pop(); stack.append(a * b)",
        "def op_div(stack): b = stack.pop(); a = stack.pop(); stack.append(a // b if isinstance(a, int) and isinstance(b, int) else a / b)",
        "def op_mod(stack): b = stack.pop(); a = stack.pop(); stack.append(a % b)",
        "def op_eq(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a == b))",
        "def op_ne(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a != b))",
        "def op_gt(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a > b))",
        "def op_lt(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a < b))",
        "def op_and(stack): b = stack.pop(); a = stack.pop(); stack.append(int(bool(a) and bool(b)))",
        "def op_or(stack): b = stack.pop(); a = stack.pop(); stack.append(int(bool(a) or bool(b)))",
        "def op_not(stack): a = stack.pop(); stack.append(int(not bool(a)))",
        "def op_dup(stack): stack.append(stack[-1])",
        "def op_drop(stack): stack.pop()",
        "def op_swap(stack): stack[-1], stack[-2] = stack[-2], stack[-1]",
        "def op_rot(stack): stack[-3], stack[-2], stack[-1] = stack[-2], stack[-1], stack[-3]",
        "def op_over(stack): stack.append(stack[-2])",
        "def op_roll(stack): n = stack.pop(); stack.append(stack.pop(-1 - n))",
        "def op_pk(stack): offset = stack.pop(); stack.append(stack[-1 - offset])",
        "def op_cons(stack): lst = stack.pop(); x = stack.pop(); stack.append([x] + lst)",
        "def op_to(stack): stack.append('SENTINEL_TO')",
        "def op_select(stack): flag = stack.pop(); val_false = stack.pop(); val_true = stack.pop(); stack.append(val_true if flag != 0 else val_false)",
        "def op_ifelse(stack):",
        "    false_blk = stack.pop()",
        "    true_blk = stack.pop()",
        "    cond = stack.pop()",
        "    if cond != 0:",
        "        execute(true_blk, stack)",
        "    else:",
        "        execute(false_blk, stack)",
        "def op_get(stack):",
        "    top = stack.pop()",
        "    if len(stack) > 0 and stack[-1] == 'SENTINEL_TO':",
        "        stack.pop()",
        "        start = stack.pop()",
        "        lst = stack.pop()",
        "        stack.append(lst[start:top])",
        "    else:",
        "        lst = stack.pop()",
        "        stack.append(lst[top])",
        "def op_len(stack): stack.append(len(stack.pop()))",
        "def op_exp(stack): stack.append(math.exp(stack.pop()))",
        "def op_log(stack): stack.append(math.log(stack.pop()))",
        "def op_pow(stack): b = stack.pop(); a = stack.pop(); stack.append(a ** b)",
        "def op_sqrt(stack): stack.append(math.sqrt(stack.pop()))",
        "def op_abs(stack): stack.append(abs(stack.pop()))",
        "def op_max(stack): b = stack.pop(); a = stack.pop(); stack.append(max(a, b))",
        "def op_min(stack): b = stack.pop(); a = stack.pop(); stack.append(min(a, b))",
        "def op_fill(stack): v = stack.pop(); l = stack.pop(); stack.append([v] * l)",
        "def op_seed(stack): pass",
        "def op_rand(stack): import random; stack.append(random.random())",
        "def op_bitand(stack): b = stack.pop(); a = stack.pop(); stack.append(a & b)",
        "def op_bitor(stack): b = stack.pop(); a = stack.pop(); stack.append(a | b)",
        "def op_bitxor(stack): b = stack.pop(); a = stack.pop(); stack.append(a ^ b)",
        "def op_bitshl(stack): b = stack.pop(); a = stack.pop(); stack.append(a << b)",
        "def op_bitshr(stack): b = stack.pop(); a = stack.pop(); stack.append(a >> b)",
        "def op_bitnot(stack): a = stack.pop(); stack.append(~a)",
        ""
    ]
    
    # Append macro definitions
    py_lines.extend(macro_defs)
    py_lines.append("")
    
    # Append main runner function
    py_lines.append("def run(initial_stack=None):")
    py_lines.append("    if initial_stack is None:")
    py_lines.append("        stack = []")
    py_lines.append("    else:")
    py_lines.append("        stack = list(initial_stack)")
    if main_defs:
        py_lines.append(indent_code("\n".join(main_defs), 4))
    py_lines.append(indent_code(main_code, 4) if main_code else "    pass")
    py_lines.append("    return stack")
    
    return "\n".join(py_lines)

def run_scrooge(scrooge_code: str, initial_stack=None):
    py_code = transpile(scrooge_code)
    local_vars = {}
    exec(py_code, local_vars)
    return local_vars['run'](initial_stack)
