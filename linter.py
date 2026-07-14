import sys
import os
import re

def strip_comments(code):
    lines = code.split("\n")
    cleaned_lines = []
    for line in lines:
        # Strip comments inside curly braces { ... }
        line = re.sub(r"\{[^}]*\}", "", line)
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def tokenize(code):
    code = strip_comments(code)
    token_specification = [
        ("ARROW",     r"->"),
        ("ELSE",      r"\belse\b"),
        ("SIG_ARROW", r"--"),
        ("LPAREN",    r"\("),
        ("RPAREN",    r"\)"),
        ("BAR_BLOCK", r"\|[ a-zA-Z0-9_\s*:\\\.\-\[\]]+\|"),
        ("MACRO",     r"#[a-zA-Z_][\w\.]*"),
        ("FLOAT",     r"-?\d+\.\d+"),
        ("INT",       r"-?\d+"),
        ("BIN",       r"\bb[01]{2,}\b"),
        ("HEX",       r"\bh[0-9a-fA-F]{2,}\b"),
        ("LBRACKET",  r"\["),
        ("RBRACKET",  r"\]"),
        ("OP_SHIFT",  r"<<|>>"),
        ("OP_SET",    r"::"),
        ("OP_DIV_INT", r"//"),
        ("OP_COMP",   r"!=|<=|>=|==|="),
        ("OP_LOGIC",  r"[><]"),
        ("OP_FOLD",   r"\\"),
        ("RANGE",     r"\^?[a-zA-Z0-9_]*\.\.\^?[a-zA-Z0-9_]*"),
        ("WORD",      r"\^?[a-zA-Z_][\w\.]*"),
        ("OP_ARITH",  r"[-+*/^&|~,?!.%$@;:]"),
        ("STRING",    r"\"[^\"]*\""),
        ("SKIP",      r"[ \t\n\r]+"),
        ("MISMATCH",  r"."),
    ]
    tok_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_specification)
    tokens = []
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind in ("SKIP", "ELSE"):
            continue
        tokens.append((kind, value))
    return tokens

class Block:
    def __init__(self, elements):
        self.elements = elements
    def __repr__(self):
        return f"Block({self.elements})"

def parse_tokens(tokens):
    stack = [[]]
    for kind, val in tokens:
        if kind == "LBRACKET":
            stack.append([])
        elif kind == "RBRACKET":
            if len(stack) < 2:
                raise RuntimeError("Unmatched closing bracket ']'")
            completed = stack.pop()
            stack[-1].append(Block(completed))
        else:
            stack[-1].append((kind, val))
    if len(stack) != 1:
        raise RuntimeError("Unmatched opening bracket '['")
    return stack[0]

def extract_words(parsed_items):
    words = {}
    i = 0
    n = len(parsed_items)
    main_body = []
    while i < n:
        item = parsed_items[i]
        if isinstance(item, tuple) and item[0] == "MACRO":
            word_name = item[1][1:]
            i += 1
            if i >= n or parsed_items[i] != ("LPAREN", "("):
                raise RuntimeError(f"Expected '(' after word definition name '{word_name}'")
            i += 1
            inputs = []
            while i < n and parsed_items[i] != ("SIG_ARROW", "--"):
                if parsed_items[i][0] != "WORD":
                    raise RuntimeError(f"Expected type name in inputs signature of '{word_name}', got {parsed_items[i]}")
                inputs.append(parsed_items[i][1])
                i += 1
            if i >= n or parsed_items[i] != ("SIG_ARROW", "--"):
                raise RuntimeError(f"Expected '--' in signature of '{word_name}'")
            i += 1
            outputs = []
            while i < n and parsed_items[i] != ("RPAREN", ")"):
                if parsed_items[i][0] != "WORD":
                    raise RuntimeError(f"Expected type name in outputs signature of '{word_name}'")
                outputs.append(parsed_items[i][1])
                i += 1
            if i >= n or parsed_items[i] != ("RPAREN", ")"):
                raise RuntimeError(f"Expected ')' in signature of '{word_name}'")
            i += 1
            body = []
            while i < n:
                body_item = parsed_items[i]
                if isinstance(body_item, tuple) and body_item == ("WORD", "end"):
                    i += 1
                    break
                body.append(body_item)
                i += 1
            else:
                raise RuntimeError(f"Expected 'end' for word definition '{word_name}'")
            words[word_name] = {
                "inputs": [x.capitalize() for x in inputs],
                "outputs": [x.capitalize() for x in outputs],
                "body": body
            }
        else:
            main_body.append(item)
            i += 1
    return words, main_body

# Type checking categories
primitives = {
    "+", "-", "*", "/", "\\", "and", "or", "not", "=", "!=", ">", "<", "<=", ">=",
    ".", "%", "$", "@", ";", "roll", "pk", "pick", "hnew", "hread", "hwrite",
    "cons", "pair", ":", "to", "select", "nil", "len", "slice", "wrap",
    "is_list", "is_string", "exp", "log", "pow", "sqrt", "abs", "max", "min", "fill", "seed", "rand",
    "bitand", "bitor", "bitxor", "bitshl", "bitshr", "bitnot",
    "print_char", "print_int",
    "?", "!", ","
}

def is_type_compatible(t1, t2):
    if t1 == "Unknown" or t2 == "Unknown":
        return True
    return t1 == t2

def verify_word(name, data, word_definitions):
    inputs = data["inputs"]
    outputs = data["outputs"]
    body = data["body"]
    
    # Track 1 & 2: Arity and Coarse Type Checker
    # Start stack with input types
    stack = list(inputs)
    
    # Verify the body elements recursively
    scope = {}
    
    try:
        final_stack = verify_block(body, stack, scope, word_definitions)
    except Exception as e:
        print(f"Verification error in word '{name}': {e}", file=sys.stderr)
        raise
        
    # Check arity and types of final stack vs outputs signature
    if len(final_stack) != len(outputs):
        raise RuntimeError(f"Arity check failed in '{name}': body produces stack of size {len(final_stack)} (types: {final_stack}), but signature expects {len(outputs)} (types: {outputs})")
        
    for i, (f_t, o_t) in enumerate(zip(final_stack, outputs)):
        if not is_type_compatible(f_t, o_t):
            raise RuntimeError(f"Type check failed in '{name}' at output index {i}: body produces {f_t}, signature expects {o_t}")

def verify_block(elements, initial_stack, scope, word_definitions):
    stack = list(initial_stack)
    # Consecutive arrow frames can add variables to the active scope
    active_scope = dict(scope)
    
    i = 0
    n = len(elements)
    while i < n:
        item = elements[i]
        
        if isinstance(item, Block):
            # A block literal: check if it is a fold or map or parameter binding block
            is_map_or_fold = False
            first_elem = item.elements[0] if item.elements else None
            
            # Check for Vector fold/map syntax
            if isinstance(first_elem, tuple) and first_elem[0] == "BAR_BLOCK":
                bar_val = first_elem[1]
                bar_vars = [v.strip() for v in bar_val[1:-1].strip().split() if v.strip()]
                
                # Check for fold or map operators inside block
                has_fold = any(isinstance(el, tuple) and el[0] == "OP_FOLD" for el in item.elements)
                has_map = len(item.elements) > 0 and isinstance(item.elements[-1], tuple) and item.elements[-1] == ("OP_ARITH", "*")
                
                if has_fold:
                    # Fold block type check
                    # Syntax: [| acc val | body \ init ]
                    fold_idx = -1
                    for idx, el in enumerate(item.elements):
                        if isinstance(el, tuple) and el[0] == "OP_FOLD":
                            fold_idx = idx
                            break
                    body_elems = item.elements[1:fold_idx]
                    init_elems = item.elements[fold_idx+1:]
                    
                    # Evaluate init on current stack
                    init_stack = verify_block(init_elems, stack, active_scope, word_definitions)
                    if not init_stack:
                        raise RuntimeError("Fold 'init' expression returned empty stack")
                    init_type = init_stack[-1]
                    # pop init result from stack
                    stack = init_stack[:-1]
                    
                    # Target array is popped from stack
                    if not stack:
                        raise RuntimeError("Fold missing target array operand on stack")
                    target_type = stack.pop()
                    if target_type != "Block" and target_type != "Unknown":
                        raise RuntimeError(f"Fold expects Block target, got {target_type}")
                        
                    # Bind variables and typecheck body
                    nested_scope = dict(active_scope)
                    nested_scope[bar_vars[0]] = init_type
                    nested_scope[bar_vars[1]] = "Unknown" # element is Unknown
                    
                    body_start_stack = [] # Body executes with acc and val on stack
                    body_final_stack = verify_block(body_elems, body_start_stack, nested_scope, word_definitions)
                    if not body_final_stack:
                        raise RuntimeError("Fold body returned empty stack")
                    final_acc_type = body_final_stack[-1]
                    if not is_type_compatible(final_acc_type, init_type):
                        raise RuntimeError(f"Fold body output accumulator type {final_acc_type} does not match init type {init_type}")
                        
                    # Fold pushes the final accumulator onto stack
                    stack.append(init_type)
                    is_map_or_fold = True
                    
                elif has_map:
                    # Map block type check
                    # Syntax: [| idx val | body * ]
                    body_elems = item.elements[1:-1]
                    
                    if not stack:
                        raise RuntimeError("Map missing target array operand on stack")
                    target_type = stack.pop()
                    if target_type != "Block" and target_type != "Unknown":
                        raise RuntimeError(f"Map expects Block target, got {target_type}")
                        
                    nested_scope = dict(active_scope)
                    nested_scope[bar_vars[0]] = "Scalar" # idx
                    nested_scope[bar_vars[1]] = "Unknown" # val
                    
                    body_final_stack = verify_block(body_elems, [], nested_scope, word_definitions)
                    # Map pushes a new Block onto stack
                    stack.append("Block")
                    is_map_or_fold = True
            
            if not is_map_or_fold:
                # Normal block literal: pushes Block type to stack
                stack.append("Block")
                
        elif isinstance(item, tuple) and item[0] == "ARROW":
            # Bind variables: -> [ vars ]
            if i + 1 >= n or not isinstance(elements[i+1], Block):
                raise RuntimeError("Expected Block node after '->'")
            vars_block = elements[i+1]
            var_names = [v[1] for v in vars_block.elements if isinstance(v, tuple) and v[0] == "WORD"]
            
            for var in reversed(var_names):
                if not stack:
                    raise RuntimeError(f"Stack underflow during '->' binding of '{var}'")
                val_type = stack.pop()
                active_scope[var] = val_type
                
            i += 1 # Skip the vars block
            
        else:
            kind, val = item
            
            # Count carets for variable scope resolution
            name = val
            num_carets = 0
            while name.startswith("^"):
                num_carets += 1
                name = name[1:]
                
            if kind == "INT" or kind == "FLOAT" or kind == "HEX" or kind == "BIN":
                stack.append("Scalar")
                
            elif kind == "STRING":
                stack.append("Block") # Strings are represented as Blocks
                
            elif kind in ("WORD", "MACRO", "OP_ARITH", "OP_COMP", "OP_SHIFT", "OP_SET", "OP_DIV_INT", "OP_FOLD", "OP_LOGIC"):
                if name in active_scope:
                    stack.append(active_scope[name])
                    
                elif name in word_definitions:
                    # Call to defined word
                    sig = word_definitions[name]
                    # pop inputs
                    for inp in reversed(sig["inputs"]):
                        if not stack:
                            raise RuntimeError(f"Stack underflow calling '{name}'")
                        popped = stack.pop()
                        if not is_type_compatible(popped, inp):
                            raise RuntimeError(f"Type mismatch calling '{name}': got {popped}, expected {inp}")
                    # push outputs
                    for out in sig["outputs"]:
                        stack.append(out)
                        
                elif name in primitives:
                    # Primitive operations
                    if name in ("+", "-", "*", "/", "\\", "and", "or", "bitand", "bitor", "bitxor", "bitshl", "bitshr", "pow", "max", "min"):
                        if len(stack) < 2:
                            raise RuntimeError(f"Stack underflow for primitive operator '{name}'")
                        t2 = stack.pop()
                        t1 = stack.pop()
                        if name in ("+", "-", "*", "/", "\\"):
                            if t1 == "Block" or t2 == "Block":
                                stack.append("Block")
                            else:
                                stack.append("Scalar")
                        else:
                            stack.append("Scalar")
                            
                    elif name in ("=", "!=", ">", "<", "<=", ">="):
                        if len(stack) < 2:
                            raise RuntimeError(f"Stack underflow for primitive '{name}'")
                        stack.pop()
                        stack.pop()
                        stack.append("Scalar")
                        
                    elif name in (".", "dup"):
                        if not stack:
                            raise RuntimeError(f"Stack underflow for dup '.'")
                        stack.append(stack[-1])
                        
                    elif name in ("%", "drop"):
                        if not stack:
                            raise RuntimeError(f"Stack underflow for drop '%'")
                        stack.pop()
                        
                    elif name in ("$", "swap"):
                        if len(stack) < 2:
                            raise RuntimeError(f"Stack underflow for swap '$'")
                        stack[-1], stack[-2] = stack[-2], stack[-1]
                        
                    elif name in ("@", "rot"):
                        if len(stack) < 3:
                            raise RuntimeError(f"Stack underflow for rot '@'")
                        stack[-3], stack[-2], stack[-1] = stack[-2], stack[-1], stack[-3]
                        
                    elif name in (";", "over"):
                        if len(stack) < 2:
                            raise RuntimeError(f"Stack underflow for over ';'")
                        stack.append(stack[-2])
                        
                    elif name in ("not", "~", "bitnot", "abs", "sqrt", "exp", "log"):
                        if not stack:
                            raise RuntimeError(f"Stack underflow for operator '{name}'")
                        t = stack.pop()
                        if name == "exp" or name == "log" or name == "sqrt":
                            stack.append("Scalar")
                        else:
                            stack.append(t)
                            
                    elif name in ("pick", "pk"):
                        if not stack:
                            raise RuntimeError(f"Stack underflow for pick/pk")
                        offset_t = stack.pop()
                        if not is_type_compatible(offset_t, "Scalar"):
                            raise RuntimeError("Offset for pick/pk must be Scalar")
                        stack.append("Unknown")
                        
                    elif name == "roll":
                        if not stack:
                            raise RuntimeError(f"Stack underflow for roll")
                        offset_t = stack.pop()
                        if not is_type_compatible(offset_t, "Scalar"):
                            raise RuntimeError("Offset for roll must be Scalar")
                        pass
                        
                    elif name == "hnew":
                        if not stack:
                            raise RuntimeError(f"Stack underflow for hnew")
                        size_t = stack.pop()
                        if not is_type_compatible(size_t, "Scalar"):
                            raise RuntimeError("hnew expects Scalar size")
                        stack.append("Ptr")
                        
                    elif name == "hread":
                        if len(stack) < 2:
                            raise RuntimeError(f"Stack underflow for hread")
                        idx_t = stack.pop()
                        ptr_t = stack.pop()
                        if not is_type_compatible(ptr_t, "Ptr"):
                            raise RuntimeError(f"hread expects Ptr, got {ptr_t}")
                        if not is_type_compatible(idx_t, "Scalar"):
                            raise RuntimeError(f"hread expects Scalar index, got {idx_t}")
                        stack.append("Unknown")
                        
                    elif name == "hwrite":
                        if len(stack) < 3:
                            raise RuntimeError(f"Stack underflow for hwrite")
                        idx_t = stack.pop()
                        ptr_t = stack.pop()
                        val_t = stack.pop()
                        if not is_type_compatible(ptr_t, "Ptr"):
                            raise RuntimeError(f"hwrite expects Ptr, got {ptr_t}")
                        if not is_type_compatible(idx_t, "Scalar"):
                            raise RuntimeError(f"hwrite expects Scalar index, got {idx_t}")
                            
                    elif name in ("print_char", "print_int"):
                        if not stack:
                            raise RuntimeError(f"Stack underflow for primitive '{name}'")
                        t = stack.pop()
                        if not is_type_compatible(t, "Scalar"):
                            raise RuntimeError(f"{name} expects Scalar, got {t}")
                            
                    elif name == "cons":
                        if len(stack) < 2:
                            raise RuntimeError(f"Stack underflow for cons")
                        lst_t = stack.pop()
                        val_t = stack.pop()
                        if lst_t != "Block" and lst_t != "Unknown":
                            raise RuntimeError(f"cons expects Block, got {lst_t}")
                        stack.append("Block")
                        
                    elif name == "pair":
                        if len(stack) < 2:
                            raise RuntimeError(f"Stack underflow for pair")
                        stack.pop()
                        stack.pop()
                        stack.append("Block")
                        
                    elif name == ":":
                        if len(stack) < 2:
                            raise RuntimeError(f"Stack underflow for retrieval operator ':'")
                        idx_t = stack.pop()
                        lst_t = stack.pop()
                        if not is_type_compatible(idx_t, "Scalar"):
                            raise RuntimeError(f"retrieval expects Scalar index, got {idx_t}")
                        if lst_t != "Block" and lst_t != "Ptr" and lst_t != "Unknown":
                            raise RuntimeError(f"retrieval expects Block or Ptr, got {lst_t}")
                        stack.append("Unknown")
                        
                    elif name == "to":
                        if len(stack) < 3:
                            raise RuntimeError(f"Stack underflow for slice operator 'to'")
                        end_t = stack.pop()
                        start_t = stack.pop()
                        lst_t = stack.pop()
                        if not is_type_compatible(start_t, "Scalar") or not is_type_compatible(end_t, "Scalar"):
                            raise RuntimeError("slice bounds must be Scalar")
                        if lst_t != "Block" and lst_t != "Unknown":
                            raise RuntimeError("slice expects Block")
                        stack.append("Block")
                        
                    elif name == "len":
                        if not stack:
                            raise RuntimeError("Stack underflow for len")
                        lst_t = stack.pop()
                        if lst_t != "Block" and lst_t != "Unknown":
                            raise RuntimeError(f"len expects Block, got {lst_t}")
                        stack.append("Scalar")
                        
                    elif name in ("is_list", "is_string"):
                        if not stack:
                            raise RuntimeError(f"Stack underflow for {name}")
                        stack.pop()
                        stack.append("Scalar")
                        
                    elif name == "nil":
                        stack.append("Block")
                        
                    elif name == "?":
                        if len(stack) < 3:
                            raise RuntimeError("Stack underflow for conditional operator '?'")
                        false_b_t = stack.pop()
                        true_b_t = stack.pop()
                        cond_t = stack.pop()
                        if not is_type_compatible(cond_t, "Scalar"):
                            raise RuntimeError(f"Conditional guard must be Scalar, got {cond_t}")
                        if i >= 2 and isinstance(elements[i-1], Block) and isinstance(elements[i-2], Block):
                            s_true = verify_block(elements[i-2].elements, stack, active_scope, word_definitions)
                            s_false = verify_block(elements[i-1].elements, stack, active_scope, word_definitions)
                            if len(s_true) != len(s_false):
                                raise RuntimeError(f"Conditional branch stack sizes mismatch: true branch returns stack of size {len(s_true)}, false branch returns {len(s_false)}")
                            for idx, (t1, t2) in enumerate(zip(s_true, s_false)):
                                if not is_type_compatible(t1, t2):
                                    raise RuntimeError(f"Conditional branch type mismatch at stack position {idx}: true has {t1}, false has {t2}")
                            stack = [t1 if t1 == t2 else "Unknown" for t1, t2 in zip(s_true, s_false)]
                        else:
                            stack.append("Unknown")
                            
                    elif name == "!":
                        if len(stack) < 2:
                            raise RuntimeError("Stack underflow for loop operator '!'")
                        blk_t = stack.pop()
                        target_t = stack.pop()
                        if i >= 1 and isinstance(elements[i-1], Block):
                            verify_block(elements[i-1].elements, stack, active_scope, word_definitions)
                        pass
                        
                    else:
                        raise RuntimeError(f"Unsupported primitive: {name}")
                else:
                    raise RuntimeError(f"Unbound identifier/word: {val}")
        i += 1
    return stack

def lint_file(filepath):
    print(f"Linting file: {filepath}")
    if not os.path.exists(filepath):
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        return False
        
    with open(filepath, "r") as f:
        code = f.read()
        
    try:
        tokens = tokenize(code)
        parsed = parse_tokens(tokens)
        word_definitions, main_body = extract_words(parsed)
        
        print(f"Parsed {len(word_definitions)} word definitions.")
        
        for name, data in word_definitions.items():
            verify_word(name, data, word_definitions)
            
        if main_body:
            print("Verifying main execution body...")
            verify_block(main_body, [], {}, word_definitions)
            
        print("LINTER SUCCESS: All checks passed!")
        return True
    except Exception as e:
        print(f"LINTER FAILURE: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python linter.py <file.sg>")
        sys.exit(1)
    success = lint_file(sys.argv[1])
    sys.exit(0 if success else 1)
