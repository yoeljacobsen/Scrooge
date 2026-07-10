import re
import math
import random

def run_scrooge(code: str) -> list:
    # 1. Preprocessing & Tokenization
    # Remove inline comments { ... }
    code = re.sub(r'\{[^{}]*\}', ' ', code)
    
    # Normalize structural syntax to tokens
    code = code.replace('#', ' # ')
    raw_tokens = code.split()
    tokens = []
    for tok in raw_tokens:
        if tok.startswith('[map|'):
            tokens.append('[map|')
            if len(tok) > 5:
                tokens.append(tok[5:])
        elif tok.startswith('[fold|'):
            tokens.append('[fold|')
            if len(tok) > 6:
                tokens.append(tok[6:])
        elif tok.startswith('[') and len(tok) > 1:
            tokens.append('[')
            tokens.append(tok[1:])
        elif tok.endswith(']') and len(tok) > 1:
            tokens.append(tok[:-1])
            tokens.append(']')
        elif tok.endswith('|') and len(tok) > 1:
            tokens.append(tok[:-1])
            tokens.append('|')
        elif tok.startswith('|') and len(tok) > 1:
            tokens.append('|')
            tokens.append(tok[1:])
        else:
            tokens.append(tok)
    
    # 2. Program Structure & Macro Registration (Pass 1)
    macros = {}
    main_body = []
    
    i = 0
    while i < len(tokens):
        if tokens[i] == '#':
            # Macro definition: #name ( inputs -- outputs ) body end
            name = tokens[i+1]
            i += 2
            # Skip signature
            if tokens[i] == '(':
                while tokens[i] != ')':
                    i += 1
                i += 1
            body = []
            while tokens[i] != 'end':
                body.append(tokens[i])
                i += 1
            macros[name] = body
            i += 1
        else:
            main_body.append(tokens[i])
            i += 1

    # 3. Execution Environment State
    stack = []
    env_seed = 0

    def parse_literal(token):
        if token == 'nil':
            return []
        # Float (scientific notation without dots, e.g., 314e-2)
        if re.match(r'^-?\d+e-?\d+$', token):
            return float(token)
        # Int
        if re.match(r'^-?\d+$', token):
            return int(token)
        return None

    def execute(body, scopes=[{}]):
        nonlocal env_seed, stack
        pc = 0
        while pc < len(body):
            token = body[pc]
            
            # Shape Gate Resolution (Ignored or validated statically)
            if token == '|':
                pc += 1
                while pc < len(body) and body[pc] != '|':
                    pc += 1
                pc += 1
                continue

            # Literal Evaluation
            lit = parse_literal(token)
            if lit is not None:
                stack.append(lit)
                pc += 1
                continue

            # Scope Binding Lookup
            val = None
            for scope in reversed(scopes):
                if token in scope:
                    val = scope[token]
                    break
            if val is not None:
                if isinstance(val, list) and any(isinstance(x, str) for x in val): # Closure
                    execute(val, scopes)
                else:
                    stack.append(val)
                pc += 1
                continue

            # Macro Invocation
            if token in macros:
                execute(macros[token], [{}])
                pc += 1
                continue

            # Block Construction / Closures
            if token == '[':
                block_tokens = []
                pc += 1
                depth = 1
                while pc < len(body):
                    if body[pc] == '[': depth += 1
                    elif body[pc] == ']': depth -= 1
                    if depth == 0: break
                    block_tokens.append(body[pc])
                    pc += 1
                
                # Check if block is an immutable Data Array or Deferred Closure
                is_data = True
                parsed_block = []
                for t in block_tokens:
                    p = parse_literal(t)
                    if p is None:
                        is_data = False
                        break
                    parsed_block.append(p)
                
                stack.append(parsed_block if is_data else block_tokens)
                pc += 1
                continue

            # Compile-Time Binding (-> [ vars ] [ body ])
            if token == '->':
                pc += 1 # skip '->'
                assert body[pc] == '['
                pc += 1
                vars_list = []
                while body[pc] != ']':
                    vars_list.append(body[pc])
                    pc += 1
                pc += 2 # skip ']' and open '[' of body
                
                body_tokens = []
                depth = 1
                while depth > 0:
                    if body[pc] == '[': depth += 1
                    elif body[pc] == ']': depth -= 1
                    if depth == 0: break
                    body_tokens.append(body[pc])
                    pc += 1
                
                # Bind variables from stack (reversed)
                new_scope = {}
                for var in reversed(vars_list):
                    new_scope[var] = stack.pop()
                
                # Execute body with inherited scope context
                execute(body_tokens, scopes + [new_scope])
                pc += 1
                continue

            # Context Map Iterator [map| idx val ctx | body ]
            if token == '[map|':
                idx_name = body[pc+1]
                val_name = body[pc+2]
                ctx_name = body[pc+3]
                pc += 5 # skip '[map| idx val ctx |'
                
                body_tokens = []
                depth = 1
                while depth > 0:
                    if body[pc] == '[': depth += 1
                    elif body[pc] == ']': depth -= 1
                    if depth == 0: break
                    body_tokens.append(body[pc])
                    pc += 1
                
                arr = stack.pop()
                ctx = stack.pop() if ctx_name != '_' else None
                
                new_arr = []
                for idx, val in enumerate(arr):
                    iter_scope = {idx_name: idx, val_name: val}
                    if ctx_name != '_': iter_scope[ctx_name] = ctx
                    sub_stack = []
                    orig_stack = stack
                    stack = sub_stack
                    execute(body_tokens, scopes + [iter_scope])
                    stack = orig_stack
                    new_arr.append(sub_stack[-1])
                stack.append(new_arr)
                pc += 1
                continue

            # Context Fold Iterator [fold| idx acc val ctx | body from init ]
            if token == '[fold|':
                idx_name = body[pc+1]
                acc_name = body[pc+2]
                val_name = body[pc+3]
                ctx_name = body[pc+4]
                pc += 6 # skip '[fold| idx acc val ctx |'
                
                body_tokens = []
                depth = 1
                while True:
                    if body[pc] == '[': depth += 1
                    elif body[pc] == ']': depth -= 1
                    if depth == 1 and body[pc] == 'from':
                        break
                    body_tokens.append(body[pc])
                    pc += 1
                pc += 1 # skip 'from'
                
                init_tokens = []
                while depth > 0:
                    if body[pc] == '[': depth += 1
                    elif body[pc] == ']': depth -= 1
                    if depth == 0: break
                    init_tokens.append(body[pc])
                    pc += 1
                
                arr = stack.pop()
                ctx = stack.pop() if ctx_name != '_' else None
                
                # Compute init value
                execute(init_tokens, scopes)
                acc = stack.pop()
                
                for idx, val in enumerate(arr):
                    iter_scope = {idx_name: idx, acc_name: acc, val_name: val}
                    if ctx_name != '_': iter_scope[ctx_name] = ctx
                    sub_stack = []
                    orig_stack = stack
                    stack = sub_stack
                    execute(body_tokens, scopes + [iter_scope])
                    stack = orig_stack
                    acc = sub_stack[-1]
                stack.append(acc)
                pc += 1
                continue

            # Conditionals
            if token == 'cond':
                pc += 1 # skip 'cond'
                assert body[pc] == '['
                pc += 1
                true_body = []
                depth = 1
                while depth > 0:
                    if body[pc] == '[': depth += 1
                    elif body[pc] == ']': depth -= 1
                    if depth == 0: break
                    true_body.append(body[pc])
                    pc += 1
                pc += 2 # skip ']' and 'else'
                assert body[pc] == '['
                pc += 1
                false_body = []
                depth = 1
                while depth > 0:
                    if body[pc] == '[': depth += 1
                    elif body[pc] == ']': depth -= 1
                    if depth == 0: break
                    false_body.append(body[pc])
                    pc += 1
                pc += 2 # skip ']' and '?'
                
                flag = stack.pop()
                if flag != 0:
                    execute(true_body, scopes)
                else:
                    execute(false_body, scopes)
                continue

            # Primitive Functional Implementation
            if token == '.':
                stack.append(stack[-1])
            elif token == '%':
                stack.pop()
            elif token == '$':
                stack[-1], stack[-2] = stack[-2], stack[-1]
            elif token == '@':
                z = stack.pop()
                y = stack.pop()
                x = stack.pop()
                stack.extend([y, z, x])
            elif token == ';':
                stack.append(stack[-2])
            elif token == 'roll':
                n = stack.pop()
                stack.append(stack.pop(-1 - n))
            elif token == 'pk':
                offset = stack.pop()
                stack.append(stack[-1 - offset])
            elif token == 'cons':
                lst = stack.pop()
                x = stack.pop()
                stack.append([x] + lst)
            elif token == ':':
                idx = stack.pop()
                blk = stack.pop()
                stack.append(blk[idx])
            elif token == 'to':
                end = stack.pop()
                start = stack.pop()
                blk = stack.pop()
                stack.append(blk[start:end])
            elif token == 'select':
                flag = stack.pop()
                f_val = stack.pop()
                t_val = stack.pop()
                stack.append(t_val if flag != 0 else f_val)
            
            # Math & Logic (Automatic Float Promotion / Signed Integer Wrapping)
            elif token in ('+', '-', '*', '/', '\\'):
                b = stack.pop()
                a = stack.pop()
                if isinstance(a, float) or isinstance(b, float):
                    if token == '+': stack.append(float(a + b))
                    elif token == '-': stack.append(float(a - b))
                    elif token == '*': stack.append(float(a * b))
                    elif token == '/': stack.append(float(a / b))
                else:
                    if token == '+': res = a + b
                    elif token == '-': res = a - b
                    elif token == '*': res = a * b
                    elif token == '/': res = int(a / b)
                    elif token == '\\': res = a % b
                    # 64-bit Signed Wrap-Around Guarantee
                    stack.append((res + 2**63) % 2**64 - 2**63)
            elif token in ('and', 'or', 'not', '=', '!=', '>', '<'):
                if token == 'not':
                    stack.append(1 if stack.pop() == 0 else 0)
                else:
                    b = stack.pop()
                    a = stack.pop()
                    if token == 'and': stack.append(1 if (a != 0 and b != 0) else 0)
                    elif token == 'or': stack.append(1 if (a != 0 or b != 0) else 0)
                    elif token == '=': stack.append(1 if a == b else 0)
                    elif token == '!=': stack.append(1 if a != b else 0)
                    elif token == '>': stack.append(1 if a > b else 0)
                    elif token == '<': stack.append(1 if a < b else 0)

            # Core Library Builtins
            elif token == 'exp':
                val = stack.pop()
                try: stack.append(min(1e9, math.exp(val)))
                except OverflowError: stack.append(1e9)
            elif token == 'log':
                val = stack.pop()
                stack.append(-1e9 if val <= 0 else math.log(val))
            elif token == 'pow':
                b = stack.pop()
                a = stack.pop()
                stack.append(pow(a, b))
            elif token == 'sqrt':
                stack.append(math.sqrt(stack.pop()))
            elif token == 'abs':
                stack.append(abs(stack.pop()))
            elif token == 'max':
                stack.append(max(stack.pop(), stack.pop()))
            elif token == 'min':
                stack.append(min(stack.pop(), stack.pop()))
            elif token == 'fill':
                val = stack.pop()
                length = stack.pop()
                stack.append([val] * length)
            elif token == 'len':
                stack.append(len(stack.pop()))
            elif token == 'seed':
                env_seed = stack.pop()
                random.seed(env_seed)
            elif token == 'rand':
                stack.append(random.random())
            elif token == 'bitand': stack.append(stack.pop() & stack.pop())
            elif token == 'bitor':  stack.append(stack.pop() | stack.pop())
            elif token == 'bitxor': stack.append(stack.pop() ^ stack.pop())
            elif token == 'bitnot': stack.append(~stack.pop())
            elif token == 'bitshl':
                shift = stack.pop()
                stack.append(stack.pop() << shift)
            elif token == 'bitshr':
                shift = stack.pop()
                stack.append(stack.pop() >> shift)
            
            pc += 1

    execute(main_body)
    return stack