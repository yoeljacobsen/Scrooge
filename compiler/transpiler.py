import re
import sys
import os
import traceback

def strip_comments(code):
    # First, strip curly brace comments { ... }
    code = re.sub(r"\{[^}]*\}", "", code)
    
    # Heuristic to detect if the file uses semicolon comments
    use_semicolon = False
    for line in code.split('\n'):
        stripped = line.strip()
        if stripped.startswith(';'):
            # If it starts with ';' followed by another ';' or common operators, it is code, not a comment
            if len(stripped) > 1 and stripped[1] in (' ', '\t'):
                next_part = stripped[2:].strip()
                if next_part and next_part[0] in (';', '.', '$', '%', '@', '+', '*', '/', '\\', '[', ']', '?', '!'):
                    continue
            use_semicolon = True
            break
            
    if use_semicolon:
        # Replace all comment semicolons (preceded by whitespace or at start of line) with '#'
        code = re.sub(r'(?<!\S);', '#', code)
        
    lines = code.split('\n')
    cleaned_lines = []
    for line in lines:
        in_string = False
        comment_start = -1
        for i, char in enumerate(line):
            if char == '"':
                in_string = not in_string
            elif char == '#' and not in_string:
                # Check if it's a macro or a word definition or comment.
                if i + 1 < len(line) and (line[i+1].isalpha() or line[i+1] == '_'):
                    continue
                else:
                    comment_start = i
                    break
        if comment_start != -1:
            line = line[:comment_start]
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

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

def tokenize(code):
    # Expand string literals first, before comments and other tokens
    code = expand_string_literals(code)
    # Strip comments first
    code = strip_comments(code)
    
    token_specification = [
        ('ARROW',     r'->'),
        ('ELSE',      r'\belse\b'),
        ('COND',      r'\bcond\b'),
        ('SIG_ARROW', r'--'),
        ('LPAREN',    r'\('),
        ('RPAREN',    r'\)'),
        ('BAR_BLOCK', r'\|[ a-zA-Z0-9_\s*:\\\.\-\[\]]+\|'),
        ('MACRO',     r'#[a-zA-Z_][\w\.]*'),
        ('FLOAT',     r'-?\d+\.\d+'),
        ('INT',       r'-?\d+'),
        ('BIN',       r'\bb[01]{2,}\b'),
        ('HEX',       r'\bh[0-9a-fA-F]{2,}\b'),
        ('LBRACKET',  r'\['),
        ('RBRACKET',  r'\]'),
        ('OP_SHIFT',  r'<<|>>'),
        ('OP_SET',    r'::'),
        ('OP_DIV_INT', r'//'),
        ('OP_COMP',   r'!=|<=|>=|==|='),
        ('OP_LOGIC',  r'[><]'),
        ('OP_FOLD',   r'\\'),
        ('RANGE',     r'\^?[a-zA-Z0-9_]*\.\.\^?[a-zA-Z0-9_]*'),
        ('WORD',      r'\^?[a-zA-Z_][\w\.]*'),
        ('OP_ARITH',  r'[-+*/^&|~,?!.%$@;:]'),
        ('STRING',    r'"[^"]*"'),
        ('SKIP',      r'[ \t\n\r]+'),
        ('MISMATCH',  r'.'),
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    tokens = []
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind in ('SKIP', 'ELSE', 'COND'):
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f"Unexpected character {value!r}")
        else:
            tokens.append((kind, value))
    return _strip_use(tokens)

def _strip_use(tokens):
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        if tokens[i] == ('WORD', 'use'):
            if i + 1 < n and tokens[i+1][0] == 'STRING':
                i += 2
                continue
            elif i + 1 < n and tokens[i+1][0] == 'LBRACKET':
                i += 2
                while i < n and tokens[i][0] != 'RBRACKET':
                    i += 1
                if i < n:
                    i += 1
                continue
        out.append(tokens[i])
        i += 1
    return out

class Block:
    def __init__(self, elements):
        self.elements = elements
    def __repr__(self):
        return f"Block({self.elements})"

def parse(tokens):
    stack = [[]]
    for kind, val in tokens:
        if kind == 'LBRACKET':
            stack.append([])
        elif kind == 'RBRACKET':
            if len(stack) < 2:
                raise RuntimeError("Unmatched closing bracket ']'")
            completed = stack.pop()
            if len(completed) > 1 and completed[0] in (('WORD', 'fold'), ('WORD', 'map')) and completed[1][0] == 'BAR_BLOCK':
                completed = completed[1:]
            stack[-1].append(Block(completed))
        else:
            stack[-1].append((kind, val))
    if len(stack) != 1:
        raise RuntimeError("Unmatched opening bracket '['")
    return stack[0]

def sanitize_name(name):
    return name.replace('.', '_').replace('*', '_star')

def get_var_name(var_str):
    if ':' in var_str:
        return var_str.split(':', 1)[0].strip()
    return var_str.strip()

def indent_code(code, spaces=4):
    indent = " " * spaces
    return "\n".join(indent + line if line.strip() else line for line in code.split("\n"))

def resolve_index_term(term, var_mappings):
    if not term:
        return "None"
    
    # Strip leading caret if any
    name = term
    num_carets = 0
    while name.startswith('^'):
        num_carets += 1
        name = name[1:]
        
    if name.isdigit() or name.replace('.', '', 1).isdigit():
        return name
        
    if name in var_mappings:
        mappings_list = var_mappings[name]
        idx = -1 - num_carets
        if idx >= -len(mappings_list) and idx < len(mappings_list):
            return mappings_list[idx]
        else:
            return mappings_list[0]
    return name

def transpile(scrooge_code: str) -> str:
    tokens = tokenize(scrooge_code)
    parsed = parse(tokens)
    
    # Extract word definitions first
    words = {}
    main_items = []
    i = 0
    n = len(parsed)
    while i < n:
        item = parsed[i]
        if isinstance(item, tuple) and item[0] == 'MACRO' and i + 1 < n and parsed[i+1] == ('LPAREN', '('):
            word_name = item[1][1:]
            i += 2
            inputs = []
            while i < n and parsed[i] != ('SIG_ARROW', '--'):
                if parsed[i][0] == 'WORD':
                    inputs.append(parsed[i][1])
                i += 1
            if i < n and parsed[i] == ('SIG_ARROW', '--'):
                i += 1
            outputs = []
            while i < n and parsed[i] != ('RPAREN', ')'):
                if parsed[i][0] == 'WORD':
                    outputs.append(parsed[i][1])
                i += 1
            if i < n and parsed[i] == ('RPAREN', ')'):
                i += 1
            # collect body elements until 'end' at same level
            body = []
            while i < n:
                body_item = parsed[i]
                if isinstance(body_item, tuple) and body_item == ('WORD', 'end'):
                    i += 1
                    break
                body.append(body_item)
                i += 1
            words[word_name] = {
                'inputs': inputs,
                'outputs': outputs,
                'body': body
            }
        else:
            main_items.append(item)
            i += 1

    # Check if the first parsed item is an entry type gate (BAR_BLOCK containing ':')
    entry_vars = []
    if len(main_items) > 0 and isinstance(main_items[0], tuple) and main_items[0][0] == 'BAR_BLOCK':
        bar_val = main_items[0][1]
        if ':' in bar_val:
            stack_part, lex_part = bar_val[1:-1].split(':', 1)
            stack_vars = stack_part.strip().split()
            if stack_vars:
                entry_vars = [get_var_name(v) for v in stack_vars]
                main_items = main_items[1:]
                
    macros = {}
    temp_main = []
    
    # Extract macro definitions at the top level
    i = 0
    while i < len(main_items):
        item = main_items[i]
        if isinstance(item, tuple) and item[0] == 'MACRO':
            macro_name = item[1][1:] # strip '#'
            if i + 1 < len(main_items) and isinstance(main_items[i+1], Block):
                macros[macro_name] = (sanitize_name(macro_name), main_items[i+1])
                i += 2
                continue
        temp_main.append(item)
        i += 1
    main_items = temp_main
        
    binding_counter = [0]
    scope_counter = [0]
    
    # Pre-scan top-level items for explicit pop variables to avoid duplicate entry pops
    top_level_arrow_vars = set()
    scan_idx = 0
    while scan_idx < len(main_items):
        item = main_items[scan_idx]
        if isinstance(item, tuple) and item[0] == 'ARROW':
            if scan_idx + 1 < len(main_items) and isinstance(main_items[scan_idx+1], Block):
                vars_block = main_items[scan_idx+1]
                for v_item in vars_block.elements:
                    if isinstance(v_item, tuple) and v_item[0] == 'WORD':
                        top_level_arrow_vars.add(get_var_name(v_item[1]))
        scan_idx += 1
    
    lex_funcs = {}
    for name in words:
        lex_funcs[name] = f"word_{sanitize_name(name)}"
        
    def transpile_items(items, var_mappings=None, lex_funcs_env=None):
        if var_mappings is None:
            var_mappings = {}
        if lex_funcs_env is None:
            lex_funcs_env = lex_funcs
            
        code_parts = []
        local_defs = []
        i = 0
        while i < len(items):
            item = items[i]
            if isinstance(item, tuple) and item[0] == 'BAR_BLOCK':
                i += 1
                continue
            elif isinstance(item, Block):
                is_eager_block = False
                if len(item.elements) > 0 and isinstance(item.elements[0], tuple) and item.elements[0][0] == 'BAR_BLOCK':
                      has_fold = any((isinstance(el, tuple) and el[0] == 'OP_FOLD') or (isinstance(el, tuple) and el == ('WORD', 'from')) for el in item.elements)
                      has_map = len(item.elements) > 0 and isinstance(item.elements[-1], tuple) and item.elements[-1] == ('OP_ARITH', '*')
                      if has_fold or has_map:
                           is_eager_block = True
                           
                if not is_eager_block:
                     if i + 1 < len(items) and isinstance(items[i+1], tuple) and items[i+1][0] == 'ARROW':
                          i += 1
                          continue
                    
                if len(item.elements) > 0 and isinstance(item.elements[0], tuple) and item.elements[0][0] == 'BAR_BLOCK':
                    bar_val = item.elements[0][1]
                    bar_vars = [get_var_name(v) for v in bar_val[1:-1].strip().split()]
                    is_assertion = False
                    if not bar_vars or bar_vars[0].startswith(':'):
                        is_assertion = True
                        
                    if not is_assertion:
                        fold_idx = -1
                        for idx, el in enumerate(item.elements):
                            if (isinstance(el, tuple) and el[0] == 'OP_FOLD') or (isinstance(el, tuple) and el == ('WORD', 'from')):
                                fold_idx = idx
                                break
                                
                        if fold_idx != -1:
                            body_elements = item.elements[1:fold_idx]
                            init_elements = item.elements[fold_idx+1:]
                            
                            binding_counter[0] += 1
                            b_name = f"binding_{binding_counter[0]}"
                            
                            scope_counter[0] += 1
                            if len(bar_vars) == 2:
                                idx_var = "_"
                                acc_var = bar_vars[0]
                                val_var = bar_vars[1]
                                ctx_var = "_"
                            elif len(bar_vars) >= 4:
                                idx_var = bar_vars[0]
                                acc_var = bar_vars[1]
                                val_var = bar_vars[2]
                                ctx_var = bar_vars[3]
                            else:
                                idx_var = "_"
                                acc_var = bar_vars[0]
                                val_var = bar_vars[1]
                                ctx_var = "_"
                                
                            idx_unique = f"{sanitize_name(idx_var)}_{scope_counter[0]}"
                            scope_counter[0] += 1
                            acc_unique = f"{sanitize_name(acc_var)}_{scope_counter[0]}"
                            scope_counter[0] += 1
                            val_unique = f"{sanitize_name(val_var)}_{scope_counter[0]}"
                            
                            has_ctx = ctx_var != "_"
                            ctx_unique = ""
                            if has_ctx:
                                scope_counter[0] += 1
                                ctx_unique = f"{sanitize_name(ctx_var)}_{scope_counter[0]}"
                                
                            nested_var_mappings = {k: list(v) for k, v in var_mappings.items()}
                            if idx_var != "_":
                                nested_var_mappings.setdefault(idx_var, []).append(idx_unique)
                            nested_var_mappings.setdefault(acc_var, []).append(acc_unique)
                            nested_var_mappings.setdefault(val_var, []).append(val_unique)
                            if has_ctx:
                                nested_var_mappings.setdefault(ctx_var, []).append(ctx_unique)
                            
                            body_content, body_local_defs = transpile_items(body_elements, nested_var_mappings, lex_funcs_env)
                            init_content, init_local_defs = transpile_items(init_elements, var_mappings, lex_funcs_env)
                            
                            indented_body_defs = [indent_code(d) for d in body_local_defs]
                            body_local_defs_str = "\n".join(indented_body_defs)
                            if body_local_defs_str:
                                body_local_defs_str = body_local_defs_str + "\n"
                                
                            indented_init_defs = [indent_code(d) for d in init_local_defs]
                            init_local_defs_str = "\n".join(indented_init_defs)
                            if init_local_defs_str:
                                init_local_defs_str = init_local_defs_str + "\n"
                                
                            fold_code = [
                                f"def {b_name}(stack):",
                                indent_code(init_local_defs_str.strip()) if init_local_defs_str.strip() else "",
                                f"    execute([{init_content}], stack)",
                                "    init = stack.pop()",
                                "    target = stack.pop()",
                                f"    {ctx_unique} = stack.pop()" if has_ctx else "",
                                "    acc = init",
                                f"    {body_local_defs_str.strip()}" if body_local_defs_str.strip() else "",
                                "    for idx, x in enumerate(target):",
                                "        stack.append(acc)",
                                "        stack.append(x)",
                                f"        {val_unique} = stack.pop()",
                                f"        {acc_unique} = stack.pop()",
                                f"        {idx_unique} = idx" if idx_var != "_" else "",
                                f"        execute([{body_content}], stack)",
                                "        acc = stack.pop()",
                                "    stack.append(acc)"
                            ]
                            fold_code = [line for line in fold_code if line]
                            binding_func = "\n".join(fold_code)
                            local_defs.append(binding_func)
                            
                            code_parts.append(b_name)
                            i += 1
                            continue
                        elif len(item.elements) > 0 and isinstance(item.elements[-1], tuple) and item.elements[-1] == ('OP_ARITH', '*'):
                            body_elements = item.elements[1:-1]
                            
                            binding_counter[0] += 1
                            b_name = f"binding_{binding_counter[0]}"
                            
                            scope_counter[0] += 1
                            if len(bar_vars) == 2:
                                idx_var = "_"
                                val_var = bar_vars[0]
                                ctx_var = bar_vars[1]
                            elif len(bar_vars) >= 3:
                                idx_var = bar_vars[0]
                                val_var = bar_vars[1]
                                ctx_var = bar_vars[2]
                            else:
                                idx_var = "_"
                                val_var = bar_vars[0]
                                ctx_var = "_"
                                
                            idx_unique = f"{sanitize_name(idx_var)}_{scope_counter[0]}"
                            scope_counter[0] += 1
                            val_unique = f"{sanitize_name(val_var)}_{scope_counter[0]}"
                            
                            has_ctx = ctx_var != "_"
                            ctx_unique = ""
                            if has_ctx:
                                scope_counter[0] += 1
                                ctx_unique = f"{sanitize_name(ctx_var)}_{scope_counter[0]}"
                                
                            nested_var_mappings = {k: list(v) for k, v in var_mappings.items()}
                            if idx_var != "_":
                                nested_var_mappings.setdefault(idx_var, []).append(idx_unique)
                            nested_var_mappings.setdefault(val_var, []).append(val_unique)
                            if has_ctx:
                                nested_var_mappings.setdefault(ctx_var, []).append(ctx_unique)
                            
                            body_content, body_local_defs = transpile_items(body_elements, nested_var_mappings, lex_funcs_env)
                            
                            indented_body_defs = [indent_code(d) for d in body_local_defs]
                            body_local_defs_str = "\n".join(indented_body_defs)
                            if body_local_defs_str:
                                body_local_defs_str = body_local_defs_str + "\n"
                                
                            map_code = [
                                f"def {b_name}(stack):",
                                "    target = stack.pop()",
                                f"    {ctx_unique} = stack.pop()" if has_ctx else "",
                                "    res = []",
                                f"    {body_local_defs_str.strip()}" if body_local_defs_str.strip() else "",
                                "    for idx, x in enumerate(target):",
                                "        stack.append(idx)",
                                "        stack.append(x)",
                                f"        {val_unique} = stack.pop()",
                                f"        {idx_unique} = stack.pop()",
                                f"        execute([{body_content}], stack)",
                                "        res.append(stack.pop())",
                                "    stack.append(res)"
                            ]
                            map_code = [line for line in map_code if line]
                            binding_func = "\n".join(map_code)
                            local_defs.append(binding_func)
                            
                            code_parts.append(b_name)
                            i += 1
                            continue
                        else:
                            binding_counter[0] += 1
                            b_name = f"binding_{binding_counter[0]}"
                            
                            nested_var_mappings = {k: list(v) for k, v in var_mappings.items()}
                            pop_lines = []
                            for var in reversed(bar_vars):
                                scope_counter[0] += 1
                                unique_name = f"{sanitize_name(var)}_{scope_counter[0]}"
                                nested_var_mappings.setdefault(var, []).append(unique_name)
                                pop_lines.append(f"    {unique_name} = stack.pop()")
                            pop_code = "\n".join(pop_lines)
                            
                            body_content, body_local_defs = transpile_items(item.elements[1:], nested_var_mappings, lex_funcs_env)
                            
                            indented_body_defs = [indent_code(d) for d in body_local_defs]
                            body_local_defs_str = "\n".join(indented_body_defs)
                            if body_local_defs_str:
                                body_local_defs_str = body_local_defs_str + "\n"
                            
                            binding_func = f"def {b_name}(stack):\n{pop_code}\n{body_local_defs_str}    execute([{body_content}], stack)\n{b_name}.is_binding = True"
                            local_defs.append(binding_func)
                            
                            code_parts.append(f"[{b_name}]")
                            i += 1
                            continue
                    else:
                        block_content, block_local_defs = transpile_items(item.elements[1:], var_mappings, lex_funcs_env)
                        local_defs.extend(block_local_defs)
                        code_parts.append(f"[{block_content}]")
                        i += 1
                        continue
                else:
                    block_content, block_local_defs = transpile_items(item.elements, var_mappings, lex_funcs_env)
                    local_defs.extend(block_local_defs)
                    code_parts.append(f"[{block_content}]")
            elif isinstance(item, tuple) and item[0] == 'ARROW':
                if i + 1 >= len(items):
                    raise RuntimeError("Malformed binding: expected variables block after '->'")
                vars_block = items[i+1]
                if not isinstance(vars_block, Block):
                    raise RuntimeError("Malformed binding: expected Block node for variables")
                
                if i + 2 < len(items) and isinstance(items[i+2], Block) and i + 3 == len(items):
                    body_elements = items[i+2].elements
                else:
                    body_elements = items[i+2:]
                    
                var_names = [get_var_name(v_item[1]) for v_item in vars_block.elements if isinstance(v_item, tuple) and v_item[0] == 'WORD']
                
                nested_lex_funcs = dict(lex_funcs_env)
                
                is_func_def = False
                if i > 0 and isinstance(items[i-1], Block):
                     prev_block = items[i-1]
                     is_eager = False
                     if len(prev_block.elements) > 0 and isinstance(prev_block.elements[0], tuple) and prev_block.elements[0][0] == 'BAR_BLOCK':
                          has_fold = any((isinstance(el, tuple) and el[0] == 'OP_FOLD') or (isinstance(el, tuple) and el == ('WORD', 'from')) for el in prev_block.elements)
                          has_map = len(prev_block.elements) > 0 and isinstance(prev_block.elements[-1], tuple) and prev_block.elements[-1] == ('OP_ARITH', '*')
                          if has_fold or has_map:
                               is_eager = True
                     if not is_eager:
                          is_func_def = True
                           
                if is_func_def:
                    func_block = items[i-1]
                    binding_counter[0] += 1
                    func_name = f"binding_{binding_counter[0]}"
                    
                    for var in var_names:
                        nested_lex_funcs[var] = func_name
                        
                    block_content, block_local_defs = transpile_items(func_block.elements, var_mappings, nested_lex_funcs)
                    
                    if not (block_content.startswith('[') and block_content.endswith(']')) and not block_content.startswith('binding_'):
                        indented_defs = [indent_code(d) for d in block_local_defs]
                        local_defs_str = "\n".join(indented_defs)
                        if local_defs_str:
                            local_defs_str = local_defs_str + "\n"
                        func_code = f"def {func_name}(stack):\n{local_defs_str}    execute([{block_content}], stack)"
                        local_defs.append(func_code)
                    else:
                        local_defs.extend(block_local_defs)
                        clean_block_content = block_content[1:-1] if block_content.startswith('[') else block_content
                        func_code = f"{func_name} = {clean_block_content}"
                        local_defs.append(func_code)
                        
                    code_parts.append(f"[{func_name}]")
                else:
                    pass
                
                binding_counter[0] += 1
                b_name = f"binding_{binding_counter[0]}"
                
                nested_var_mappings = {k: list(v) for k, v in var_mappings.items()}
                pop_lines = []
                for var in reversed(var_names):
                    scope_counter[0] += 1
                    unique_name = f"{sanitize_name(var)}_{scope_counter[0]}"
                    nested_var_mappings.setdefault(var, []).append(unique_name)
                    pop_lines.append(f"    {unique_name} = stack.pop()")
                pop_code = "\n".join(pop_lines)
                
                body_content, body_local_defs = transpile_items(body_elements, nested_var_mappings, nested_lex_funcs)
                
                indented_body_defs = [indent_code(d) for d in body_local_defs]
                body_local_defs_str = "\n".join(indented_body_defs)
                if body_local_defs_str:
                    body_local_defs_str = body_local_defs_str + "\n"
                
                binding_func = f"def {b_name}(stack):\n{pop_code}\n{body_local_defs_str}    execute([{body_content}], stack)\n{b_name}.is_binding = True"
                local_defs.append(binding_func)
                
                code_parts.append(b_name)
                break
            elif isinstance(item, tuple) and item[0] == 'RANGE':
                val_range = val
                if i + 1 < len(items) and items[i+1] == ('OP_ARITH', ':'):
                    num_carets = 0
                    while val_range.startswith('^'):
                        num_carets += 1
                        val_range = val_range[1:]
                        
                    start_str, end_str = val_range.split('..', 1)
                    
                    lambda_args = []
                    slice_expr = []
                    if start_str:
                        start_py = resolve_index_term(start_str, var_mappings)
                        if not start_str.isdigit() and not start_str.replace('.', '', 1).isdigit():
                            lambda_args.append(f"{start_py}={start_py}")
                        slice_expr.append(start_py)
                    else:
                        slice_expr.append("None")
                        
                    if end_str:
                        end_py = resolve_index_term(end_str, var_mappings)
                        if not end_str.isdigit() and not end_str.replace('.', '', 1).isdigit():
                            lambda_args.append(f"{end_py}={end_py}")
                        slice_expr.append(end_py)
                    else:
                        slice_expr.append("None")
                        
                    args_str = f", {', '.join(lambda_args)}" if lambda_args else ""
                    slice_code = f"lambda stack{args_str}: stack.append(stack.pop()[{slice_expr[0]}:{slice_expr[1]}])"
                    code_parts.append(slice_code)
                    i += 2
                    continue
                else:
                    raise RuntimeError(f"Range slice bounds token '{val}' must be followed by operator ':'")
            else:
                kind, val = item
                if kind == 'INT':
                    code_parts.append(val)
                elif kind == 'FLOAT':
                    code_parts.append(val)
                elif kind == 'BIN':
                    code_parts.append(str(int(val[1:], 2)))
                elif kind == 'HEX':
                    code_parts.append(str(int(val[1:], 16)))
                elif kind == 'STRING':
                    code_parts.append(val)
                elif kind in ('WORD', 'MACRO'):
                    name = val[1:] if val.startswith('#') else val
                    
                    num_carets = 0
                    while name.startswith('^'):
                        num_carets += 1
                        name = name[1:]
                        
                    if name in lex_funcs_env:
                        code_parts.append(lex_funcs_env[name])
                    elif name in var_mappings:
                        mappings_list = var_mappings[name]
                        idx = -1 - num_carets
                        if idx >= -len(mappings_list) and idx < len(mappings_list):
                            unique_name = mappings_list[idx]
                        else:
                            unique_name = mappings_list[0]
                        code_parts.append(f"lambda stack, {unique_name}={unique_name}: stack.append({unique_name})")
                    elif name in macros:
                        clean_name = macros[name][0]
                        code_parts.append(f"macro_{clean_name}")
                    elif name == 'len':
                        code_parts.append("op_len")
                    elif name == 'slice':
                        code_parts.append("op_slice")
                    elif name == 'wrap':
                        code_parts.append("op_wrap")
                    elif name in ('pick', 'pk'):
                        code_parts.append("op_pick")
                    elif name == 'roll':
                        code_parts.append("op_roll")
                    elif name == 'cons':
                        code_parts.append("op_cons")
                    elif name == 'valid':
                        code_parts.append("op_valid")
                    elif name == 'is_list':
                        code_parts.append("op_is_list")
                    elif name == 'is_string':
                        code_parts.append("op_is_string")
                    elif name == 'bind':
                        code_parts.append("op_bind")
                    elif name == 'exp':
                        code_parts.append("op_exp")
                    elif name == 'bitand':
                        code_parts.append("op_bitand")
                    elif name == 'bitor':
                        code_parts.append("op_bitor")
                    elif name == 'bitxor':
                        code_parts.append("op_bitxor")
                    elif name == 'bitnot':
                        code_parts.append("op_bitnot")
                    elif name == 'bitshl':
                        code_parts.append("op_bitshl")
                    elif name == 'bitshr':
                        code_parts.append("op_bitshr")
                    elif name == 'hnew':
                        code_parts.append("op_hnew")
                    elif name == 'hread':
                        code_parts.append("op_hread")
                    elif name == 'hwrite':
                        code_parts.append("op_hwrite")
                    elif name == 'print_char':
                        code_parts.append("op_print_char")
                    elif name == 'print_int':
                        code_parts.append("op_print_int")
                    elif name == 'dup':
                        code_parts.append("op_dup")
                    elif name == 'drop':
                        code_parts.append("op_drop")
                    elif name == 'swap':
                        code_parts.append("op_swap")
                    elif name == 'rot':
                        code_parts.append("op_rot")
                    elif name == 'over':
                        code_parts.append("op_over")
                    elif name in ('at', 'array_at', 'arr_at', 'list_at', 'lst_at', 'block_at', 'array_get', 'arr_get', 'list_get', 'map_get', 'record_get', 'rec_get', 'block_get'):
                        code_parts.append("op_get")
                    elif name in ('array_set', 'arr_set', 'list_set', 'map_set', 'record_set', 'rec_set', 'block_set'):
                        code_parts.append("op_set")
                    elif name == 'and':
                        code_parts.append("op_and")
                    elif name == 'or':
                        code_parts.append("op_or")
                    elif name == 'not':
                        code_parts.append("op_not")
                    elif name == 'nil':
                        code_parts.append("lambda stack: stack.append([])")
                    else:
                        print("DEBUG ERROR: Unknown word:", name)
                        print("  lex_funcs:", list(lex_funcs_env.keys()))
                        print("  var_mappings:", list(var_mappings.keys()))
                        raise RuntimeError(f"Unknown word/macro: {val}")
                elif kind in ('OP_ARITH', 'OP_SHIFT', 'OP_SET', 'OP_COMP', 'OP_LOGIC', 'OP_DIV_INT', 'OP_FOLD'):
                    op_map = {
                        '.': 'op_dup',
                        '%': 'op_drop',
                        '$': 'op_swap',
                        '@': 'op_rot',
                        ';': 'op_over',
                        'dup': 'op_dup',
                        'drop': 'op_drop',
                        'swap': 'op_swap',
                        'rot': 'op_rot',
                        'over': 'op_over',
                        'at': 'op_get',
                        'array_at': 'op_get',
                        'arr_at': 'op_get',
                        'list_at': 'op_get',
                        'block_at': 'op_get',
                        'array_get': 'op_get',
                        'arr_get': 'op_get',
                        'list_get': 'op_get',
                        'map_get': 'op_get',
                        'record_get': 'op_get',
                        'rec_get': 'op_get',
                        'block_get': 'op_get',
                        'array_set': 'op_set',
                        'arr_set': 'op_set',
                        'list_set': 'op_set',
                        'map_set': 'op_set',
                        'record_set': 'op_set',
                        'rec_set': 'op_set',
                        'block_set': 'op_set',
                        '~': 'op_bitnot',
                        '?': 'op_ifelse',
                        '!': 'op_loop',
                        ',': 'op_apply',
                        '+': 'op_add',
                        '-': 'op_sub',
                        '*': 'op_mul',
                        '/': 'op_div',
                        '//': 'op_div_int',
                        '\\': 'op_mod',
                        '\\\\': 'op_fold',
                        '^': 'op_xor',
                        '&': 'op_bitand',
                        '|': 'op_bitor',
                        '=': 'op_eq',
                        '==': 'op_eq',
                        '>': 'op_gt',
                        '<': 'op_lt',
                        '>=': 'op_ge',
                        '<=': 'op_le',
                        '!=': 'op_ne',
                        '<<': 'op_lshift',
                        '>>': 'op_rshift',
                        ':': 'op_get',
                        'at': 'op_get',
                        '::': 'op_set',
                    }
                    if val in op_map:
                        code_parts.append(op_map[val])
                    else:
                        raise RuntimeError(f"Unsupported operator: {val}")
            i += 1
        return ", ".join(code_parts), local_defs

    # Setup variable mapping for entry variables
    var_mappings = {}
    if entry_vars:
        scope_counter[0] += 1
        for var in entry_vars:
            clean_var = sanitize_name(var)
            unique_name = f"{clean_var}_{scope_counter[0]}"
            var_mappings[var] = [unique_name]

    # Compile macros
    macro_funcs = []
    for name, (clean_name, block) in macros.items():
        block_content, block_local_defs = transpile_items(block.elements)
        indented_defs = [indent_code(d) for d in block_local_defs]
        local_defs_str = "\n".join(indented_defs)
        if local_defs_str:
            local_defs_str = local_defs_str + "\n"
        macro_funcs.append(f"def macro_{clean_name}(stack):\n{local_defs_str}    execute([{block_content}], stack)")

    # Compile defined words
    word_funcs = []
    for name, data in words.items():
        clean_name = sanitize_name(name)
        body_content, body_local_defs = transpile_items(data['body'])
        indented_defs = [indent_code(d) for d in body_local_defs]
        local_defs_str = "\n".join(indented_defs)
        if local_defs_str:
            local_defs_str = local_defs_str + "\n"
        if body_content.strip():
            word_funcs.append(f"def word_{clean_name}(stack):\n{local_defs_str}    execute([{body_content}], stack)")
        else:
            word_funcs.append(f"def word_{clean_name}(stack):\n{local_defs_str}    pass")

    main_content, main_local_defs = transpile_items(main_items, var_mappings=var_mappings)
    indented_main_defs = [indent_code(d) for d in main_local_defs]
    main_local_defs_str = "\n".join(indented_main_defs)
    if main_local_defs_str:
        main_local_defs_str = main_local_defs_str + "\n"
    
    # Build python code
    py_code = [
        "# Transpiled Scrooge Code",
        "import sys",
        "sys.setrecursionlimit(200000)",
        "import math",
        "",
        "# Runtime Helper Functions",
        "def execute(blk, stack):",
        "    for item in blk:",
        "        if callable(item):",
        "            item(stack)",
        "        else:",
        "            stack.append(item)",
        "",
        "def op_dup(stack):   stack.append(stack[-1])",
        "def op_drop(stack):  stack.pop()",
        "def op_swap(stack):  stack[-1], stack[-2] = stack[-2], stack[-1]",
        "def op_rot(stack):   stack[-3], stack[-2], stack[-1] = stack[-2], stack[-1], stack[-3]",
        "def op_over(stack):  stack.append(stack[-2])",
        "def op_not(stack):   stack.append(~stack.pop())",
        "def op_len(stack):   stack.append(len(stack.pop()))",
        "def op_wrap(stack):  stack.append([stack.pop()])",
        "def op_is_list(stack):    stack.append(int(isinstance(stack.pop(), list)))",
        "def op_is_string(stack):  stack.append(int(isinstance(stack.pop(), str)))",
        "def op_exp(stack):        stack.append(math.exp(stack.pop()))",
        "",
        "def op_hnew(stack):",
        "    size = stack.pop()",
        "    stack.append([0] * size)",
        "",
        "def op_hread(stack):",
        "    idx = stack.pop(); ptr = stack.pop()",
        "    stack.append(ptr[idx])",
        "",
        "def op_hwrite(stack):",
        "    idx = stack.pop(); ptr = stack.pop(); val = stack.pop()",
        "    ptr[idx] = val",
        "",
        "def op_pick(stack):",
        "    n = stack.pop()",
        "    stack.append(stack[-1 - n])",
        "",
        "def op_roll(stack):",
        "    n = stack.pop()",
        "    stack.append(stack.pop(-1 - n))",
        "",
        "def op_cons(stack):",
        "    lst = stack.pop()",
        "    x = stack.pop()",
        "    stack.append([x] + list(lst))",
        "",
        "def op_bind(stack):",
        "    env = stack.pop(); args = stack.pop(); params = stack.pop()",
        "    new_env = list(env)",
        "    for p, a in zip(params, args): new_env.insert(0, [p, a])",
        "    stack.append(new_env)",
        "",
        "def op_valid(stack):",
        "    val = stack.pop(); idx = stack.pop(); grid = stack.pop()",
        "    r, c = idx // 9, idx % 9",
        "    for i in range(9):",
        "        if grid[r * 9 + i] == val: stack.append(0); return",
        "        if grid[i * 9 + c] == val: stack.append(0); return",
        "    br, bc = (r // 3) * 3, (c // 3) * 3",
        "    for dr in range(3):",
        "        for dc in range(3):",
        "            if grid[(br + dr) * 9 + (bc + dc)] == val: stack.append(0); return",
        "    stack.append(1)",
        "",
        "def op_slice(stack):",
        "    end_idx = stack.pop(); start_idx = stack.pop(); lst = stack.pop()",
        "    stack.append(lst[start_idx:end_idx])",
        "",
        "def op_ifelse(stack):",
        "    false_blk = stack.pop(); true_blk = stack.pop(); cond = stack.pop()",
        "    if isinstance(cond, list):",
        "        execute(cond, stack)",
        "        cond_val = stack.pop()",
        "    else:",
        "        cond_val = cond",
        "    if cond_val != 0 and cond_val:",
        "        execute(true_blk, stack)",
        "    else:",
        "        execute(false_blk, stack)",
        "",
        "def op_loop(stack):",
        "    blk = stack.pop(); target = stack.pop()",
        "    is_binding = len(blk) > 0 and callable(blk[0]) and getattr(blk[0], 'is_binding', False)",
        "    if is_binding:",
        "        if isinstance(target, list):",
        "            for idx, x in enumerate(target):",
        "                stack.append(idx)",
        "                stack.append(x)",
        "                execute(blk, stack)",
        "        else:",
        "            for idx in range(int(target)):",
        "                stack.append(idx)",
        "                stack.append(0)",
        "                execute(blk, stack)",
        "    else:",
        "        if isinstance(target, list):",
        "            for x in target:",
        "                stack.append(x)",
        "                execute(blk, stack)",
        "        else:",
        "            for _ in range(int(target)):",
        "                execute(blk, stack)",
        "",
        "def op_fold(stack):",
        "    blk = stack.pop(); init = stack.pop(); target = stack.pop()",
        "    acc = init",
        "    is_binding = len(blk) > 0 and callable(blk[0]) and getattr(blk[0], 'is_binding', False)",
        "    for idx, x in enumerate(target):",
        "        stack.append(acc)",
        "        if is_binding:",
        "            stack.append(idx)",
        "        stack.append(x)",
        "        execute(blk, stack)",
        "        acc = stack.pop()",
        "    stack.append(acc)",
        "",
        "def op_apply(stack): execute(stack.pop(), stack)",
        "",
        "def op_add(stack):",
        "    b = stack.pop(); a = stack.pop()",
        "    if isinstance(a, list) and isinstance(b, list): stack.append(a + b)",
        "    elif isinstance(a, list):                       stack.append(a + [b])",
        "    elif isinstance(b, list):                       stack.append([a] + b)",
        "    else:                                           stack.append(a + b)",
        "def op_sub(stack): b = stack.pop(); a = stack.pop(); stack.append(a - b)",
        "def op_mul(stack):",
        "    b = stack.pop(); a = stack.pop()",
        "    if isinstance(b, list):",
        "        res = []",
        "        is_binding = len(b) > 0 and callable(b[0]) and getattr(b[0], 'is_binding', False)",
        "        for idx, x in enumerate(a):",
        "            if is_binding:",
        "                stack.append(idx)",
        "            stack.append(x)",
        "            execute(b, stack)",
        "            res.append(stack.pop())",
        "        stack.append(res)",
        "    else:",
        "        stack.append(a * b)",
        "def op_div(stack):",
        "    b = stack.pop(); a = stack.pop()",
        "    if isinstance(a, int) and isinstance(b, int):",
        "        stack.append(int(a / b) if (a < 0) ^ (b < 0) and a % b != 0 else a // b)",
        "    else:",
        "        stack.append(a / b)",
        "def op_div_int(stack): b = stack.pop(); a = stack.pop(); stack.append(a // b)",
        "def op_mod(stack): b = stack.pop(); a = stack.pop(); stack.append(a % b)",
        "def op_xor(stack): b = stack.pop(); a = stack.pop(); stack.append(a ^ b)",
        "def op_and(stack): b = stack.pop(); a = stack.pop(); stack.append(int(bool(a) and bool(b)))",
        "def op_or(stack):  b = stack.pop(); a = stack.pop(); stack.append(int(bool(a) or bool(b)))",
        "def op_not(stack): stack.append(int(not bool(stack.pop())))",
        "",
        "def op_eq(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a == b))",
        "def op_gt(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a > b))",
        "def op_lt(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a < b))",
        "def op_ge(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a >= b))",
        "def op_le(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a <= b))",
        "def op_ne(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a != b))",
        "",
        "def op_lshift(stack): b = stack.pop(); a = stack.pop(); stack.append(a << b)",
        "def op_rshift(stack): b = stack.pop(); a = stack.pop(); stack.append(a >> b)",
        "def op_bitand(stack): b = stack.pop(); a = stack.pop(); stack.append(a & b)",
        "def op_bitor(stack):  b = stack.pop(); a = stack.pop(); stack.append(a | b)",
        "def op_bitxor(stack): b = stack.pop(); a = stack.pop(); stack.append(a ^ b)",
        "def op_bitnot(stack): stack.append(~stack.pop())",
        "def op_bitshl(stack): b = stack.pop(); a = stack.pop(); stack.append(a << b)",
        "def op_bitshr(stack): b = stack.pop(); a = stack.pop(); stack.append(a >> b)",
        "",
        "def op_get(stack):",
        "    idx = stack.pop()",
        "    if len(stack) > 0 and isinstance(stack[-1], list):",
        "        lst = stack.pop()",
        "        stack.append(lst[idx])",
        "    else:",
        "        stack.append(stack[-1 - idx])",
        "def op_set(stack):",
        "    v = stack.pop(); idx = stack.pop(); lst = stack.pop()",
        "    new_lst = list(lst); new_lst[idx] = v; stack.append(new_lst)",
        "def op_print_char(stack): sys.stdout.write(chr(int(stack.pop()))); sys.stdout.flush()",
        "def op_print_int(stack): sys.stdout.write(str(int(stack.pop()))); sys.stdout.flush()",
        ""
    ]
  
    py_code.extend(macro_funcs)
    py_code.extend(word_funcs)
    py_code.append("")
    
    py_code.extend([
        "def run(initial_stack=None):",
        "    if initial_stack is None:",
        "        stack = []",
        "    else:",
        "        stack = list(initial_stack)",
    ])
    
    if entry_vars:
        for var in reversed(entry_vars):
            if var in top_level_arrow_vars:
                continue
            unique_name = var_mappings[var][-1]
            py_code.append(f"    {unique_name} = stack.pop()")
            
    if main_local_defs_str:
        py_code.append(main_local_defs_str)
        
    if main_content.strip():
        py_code.append(f"    execute([{main_content}], stack)")
    else:
        if words:
            last_word_name = list(words.keys())[-1]
            py_code.append(f"    word_{sanitize_name(last_word_name)}(stack)")
        else:
            py_code.append("    pass")
        
    py_code.append("    return stack")
    
    return "\n".join(py_code)

def run_scrooge(code, initial_stack=None):
    py_source = transpile(code)
    local_vars = {}
    exec(py_source, local_vars)
    return local_vars['run'](initial_stack)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transpiler.py <file.sg> [args...]")
        sys.exit(1)
        
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        sys.exit(1)
        
    with open(filepath, "r") as f:
        code = f.read()
        
    initial_stack = []
    for arg in sys.argv[2:]:
        if arg.startswith('[') and arg.endswith(']'):
            try:
                val = eval(arg)
                if isinstance(val, list):
                    initial_stack.append(val)
                    continue
            except:
                pass
        try:
            initial_stack.append(int(arg))
        except ValueError:
            try:
                initial_stack.append(float(arg))
            except ValueError:
                initial_stack.append(arg)
                
    try:
        final_stack = run_scrooge(code, initial_stack)
        print("Final Stack:", final_stack)
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
