# Transpiled Scrooge Code
import sys
import math
import traceback

# Runtime Helper Functions
def execute(blk, stack):
    for item in blk:
        if callable(item):
            item(stack)
        else:
            stack.append(item)

def op_dup(stack):   stack.append(stack[-1])
def op_drop(stack):  stack.pop()
def op_swap(stack):  stack[-1], stack[-2] = stack[-2], stack[-1]
def op_rot(stack):   stack[-3], stack[-2], stack[-1] = stack[-2], stack[-1], stack[-3]
def op_over(stack):  stack.append(stack[-2])
def op_not(stack):   stack.append(~stack.pop())
def op_len(stack):   stack.append(len(stack.pop()))
def op_wrap(stack):  stack.append([stack.pop()])
def op_is_list(stack):    stack.append(int(isinstance(stack.pop(), list)))
def op_is_string(stack):  stack.append(int(isinstance(stack.pop(), str)))
def op_exp(stack):        stack.append(math.exp(stack.pop()))

def op_pick(stack):
    n = stack.pop()
    stack.append(stack[-1 - n])

def op_roll(stack):
    n = stack.pop()
    stack.append(stack.pop(-1 - n))

def op_cons(stack):
    lst = stack.pop()
    x = stack.pop()
    stack.append([x] + list(lst))

def op_bind(stack):
    env = stack.pop(); args = stack.pop(); params = stack.pop()
    new_env = list(env)
    for p, a in zip(params, args): new_env.insert(0, [p, a])
    stack.append(new_env)

def op_valid(stack):
    val = stack.pop(); idx = stack.pop(); grid = stack.pop()
    r, c = idx // 9, idx % 9
    for i in range(9):
        if grid[r * 9 + i] == val: stack.append(0); return
        if grid[i * 9 + c] == val: stack.append(0); return
    br, bc = (r // 3) * 3, (c // 3) * 3
    for dr in range(3):
        for dc in range(3):
            if grid[(br + dr) * 9 + (bc + dc)] == val: stack.append(0); return
    stack.append(1)

def op_slice(stack):
    end_idx = stack.pop(); start_idx = stack.pop(); lst = stack.pop()
    stack.append(lst[start_idx:end_idx])

def op_ifelse(stack):
    false_blk = stack.pop(); true_blk = stack.pop(); cond = stack.pop()
    if cond != 0:
        execute(true_blk, stack)
    else:
        execute(false_blk, stack)

def op_loop(stack):
    blk = stack.pop(); target = stack.pop()
    is_binding = len(blk) > 0 and callable(blk[0]) and getattr(blk[0], 'is_binding', False)
    if is_binding:
        if isinstance(target, list):
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                execute(blk, stack)
        else:
            for idx in range(int(target)):
                stack.append(idx)
                stack.append(0)
                execute(blk, stack)
    else:
        if isinstance(target, list):
            for x in target:
                stack.append(x)
                execute(blk, stack)
        else:
            for _ in range(int(target)):
                execute(blk, stack)

def op_fold(stack):
    blk = stack.pop(); init = stack.pop(); target = stack.pop()
    acc = init
    is_binding = len(blk) > 0 and callable(blk[0]) and getattr(blk[0], 'is_binding', False)
    for idx, x in enumerate(target):
        stack.append(acc)
        if is_binding:
            stack.append(idx)
        stack.append(x)
        execute(blk, stack)
        acc = stack.pop()
    stack.append(acc)

def op_apply(stack): execute(stack.pop(), stack)

def op_add(stack):
    b = stack.pop(); a = stack.pop()
    if isinstance(a, list) and isinstance(b, list): stack.append(a + b)
    elif isinstance(a, list):                       stack.append(a + [b])
    elif isinstance(b, list):                       stack.append([a] + b)
    else:                                           stack.append(a + b)
def op_sub(stack): b = stack.pop(); a = stack.pop(); stack.append(a - b)
def op_mul(stack):
    b = stack.pop(); a = stack.pop()
    if isinstance(b, list):
        res = []
        is_binding = len(b) > 0 and callable(b[0]) and getattr(b[0], 'is_binding', False)
        for idx, x in enumerate(a):
            if is_binding:
                stack.append(idx)
            stack.append(x)
            execute(b, stack)
            res.append(stack.pop())
        stack.append(res)
    else:
        stack.append(a * b)
def op_div(stack): b = stack.pop(); a = stack.pop(); stack.append(a / b)
def op_div_int(stack): b = stack.pop(); a = stack.pop(); stack.append(a // b)
def op_mod(stack): b = stack.pop(); a = stack.pop(); stack.append(a % b)
def op_xor(stack): b = stack.pop(); a = stack.pop(); stack.append(a ^ b)
def op_and(stack): b = stack.pop(); a = stack.pop(); stack.append(a & b)
def op_or(stack):  b = stack.pop(); a = stack.pop(); stack.append(a | b)

def op_eq(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a == b))
def op_gt(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a > b))
def op_lt(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a < b))
def op_ge(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a >= b))
def op_le(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a <= b))
def op_ne(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a != b))

def op_lshift(stack): b = stack.pop(); a = stack.pop(); stack.append(a << b)
def op_rshift(stack): b = stack.pop(); a = stack.pop(); stack.append(a >> b)

def op_get(stack):
    idx = stack.pop()
    if len(stack) > 0 and isinstance(stack[-1], list):
        lst = stack.pop()
        try:
            stack.append(lst[idx])
        except Exception as e:
            print('DEBUG op_get (list indexing) failed!')
            print('lst len:', len(lst), 'idx:', idx)
            print('lst:', lst)
            traceback.print_stack()
            raise e
    else:
        try:
            stack.append(stack[-1 - idx])
        except Exception as e:
            print('DEBUG op_get (stack retrieval) failed!')
            print('stack len:', len(stack), 'idx:', idx)
            print('stack:', stack)
            traceback.print_stack()
            raise e
def op_set(stack):
    v = stack.pop(); idx = stack.pop(); lst = stack.pop()
    new_lst = list(lst); new_lst[idx] = v; stack.append(new_lst)


def run(initial_stack=None):
    if initial_stack is None:
        stack = []
    else:
        stack = list(initial_stack)
    b0 = stack.pop()
    W0 = stack.pop()
    D = stack.pop()
    def binding_2(stack):
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            v = stack.pop()
            i = stack.pop()
            execute([lambda stack, v=v: stack.append(v), lambda stack, x=x: stack.append(x), lambda stack, i=i: stack.append(i), op_get, op_mul], stack)
            res.append(stack.pop())
        stack.append(res)
    def binding_3(stack):
        execute([0.0], stack)
        init = stack.pop()
        target = stack.pop()
        acc = init
        for idx, x in enumerate(target):
            stack.append(acc)
            stack.append(x)
            v = stack.pop()
            a = stack.pop()
            execute([lambda stack, a=a: stack.append(a), lambda stack, v=v: stack.append(v), op_add], stack)
            acc = stack.pop()
        stack.append(acc)
    def binding_1(stack):
        x = stack.pop()
        w = stack.pop()
        def binding_2(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, v=v: stack.append(v), lambda stack, x=x: stack.append(x), lambda stack, i=i: stack.append(i), op_get, op_mul], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_3(stack):
            execute([0.0], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                v = stack.pop()
                a = stack.pop()
                execute([lambda stack, a=a: stack.append(a), lambda stack, v=v: stack.append(v), op_add], stack)
                acc = stack.pop()
            stack.append(acc)
        execute([lambda stack, w=w: stack.append(w), binding_2, binding_3], stack)
    binding_1.is_binding = True
    def binding_6(stack):
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            r = stack.pop()
            i = stack.pop()
            execute([lambda stack, r=r: stack.append(r), lambda stack, x=x: stack.append(x), binding_1, lambda stack, b=b: stack.append(b), lambda stack, i=i: stack.append(i), op_get, op_add], stack)
            res.append(stack.pop())
        stack.append(res)
    def binding_5(stack):
        x = stack.pop()
        b = stack.pop()
        W = stack.pop()
        def binding_6(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                r = stack.pop()
                i = stack.pop()
                execute([lambda stack, r=r: stack.append(r), lambda stack, x=x: stack.append(x), binding_1, lambda stack, b=b: stack.append(b), lambda stack, i=i: stack.append(i), op_get, op_add], stack)
                res.append(stack.pop())
            stack.append(res)
        execute([lambda stack, W=W: stack.append(W), binding_6], stack)
    binding_5.is_binding = True
    def binding_9(stack):
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            v = stack.pop()
            i = stack.pop()
            execute([lambda stack, v=v: stack.append(v), op_exp], stack)
            res.append(stack.pop())
        stack.append(res)
    def binding_10(stack):
        execute([0.0], stack)
        init = stack.pop()
        target = stack.pop()
        acc = init
        for idx, x in enumerate(target):
            stack.append(acc)
            stack.append(x)
            v = stack.pop()
            a = stack.pop()
            execute([lambda stack, a=a: stack.append(a), lambda stack, v=v: stack.append(v), op_add], stack)
            acc = stack.pop()
        stack.append(acc)
    def binding_12(stack):
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            v = stack.pop()
            i = stack.pop()
            execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
            res.append(stack.pop())
        stack.append(res)
    def binding_11(stack):
        s = stack.pop()
        e = stack.pop()
        def binding_12(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                res.append(stack.pop())
            stack.append(res)
        execute([lambda stack, e=e: stack.append(e), binding_12], stack)
    binding_11.is_binding = True
    def binding_8(stack):
        z = stack.pop()
        def binding_9(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, v=v: stack.append(v), op_exp], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_10(stack):
            execute([0.0], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                v = stack.pop()
                a = stack.pop()
                execute([lambda stack, a=a: stack.append(a), lambda stack, v=v: stack.append(v), op_add], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_12(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_11(stack):
            s = stack.pop()
            e = stack.pop()
            def binding_12(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, e=e: stack.append(e), binding_12], stack)
        binding_11.is_binding = True
        execute([lambda stack, z=z: stack.append(z), binding_9, op_dup, binding_10, binding_11], stack)
    binding_8.is_binding = True
    def binding_15(stack):
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            v = stack.pop()
            i = stack.pop()
            execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
            res.append(stack.pop())
        stack.append(res)
    def binding_14(stack):
        y = stack.pop()
        p = stack.pop()
        def binding_15(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                res.append(stack.pop())
            stack.append(res)
        execute([lambda stack, p=p: stack.append(p), binding_15], stack)
    binding_14.is_binding = True
    def binding_19(stack):
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            w = stack.pop()
            j = stack.pop()
            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
            res.append(stack.pop())
        stack.append(res)
    def binding_18(stack):
        target = stack.pop()
        res = []
        def binding_19(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                w = stack.pop()
                j = stack.pop()
                execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            q = stack.pop()
            i = stack.pop()
            execute([lambda stack, q=q: stack.append(q), binding_19], stack)
            res.append(stack.pop())
        stack.append(res)
    def binding_20(stack):
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            v = stack.pop()
            i = stack.pop()
            execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
            res.append(stack.pop())
        stack.append(res)
    def binding_17(stack):
        r = stack.pop()
        g = stack.pop()
        x = stack.pop()
        b = stack.pop()
        W = stack.pop()
        def binding_19(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                w = stack.pop()
                j = stack.pop()
                execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_18(stack):
            target = stack.pop()
            res = []
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                q = stack.pop()
                i = stack.pop()
                execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_20(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
    binding_17.is_binding = True
    def binding_25(stack):
        g = stack.pop()
        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
    binding_25.is_binding = True
    def binding_24(stack):
        y = stack.pop()
        x = stack.pop()
        b = stack.pop()
        W = stack.pop()
        def binding_25(stack):
            g = stack.pop()
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
        binding_25.is_binding = True
        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
    binding_24.is_binding = True
    def binding_23(stack):
        execute([lambda stack, M=M: stack.append(M)], stack)
        init = stack.pop()
        target = stack.pop()
        acc = init
        def binding_25(stack):
            g = stack.pop()
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
        binding_25.is_binding = True
        def binding_24(stack):
            y = stack.pop()
            x = stack.pop()
            b = stack.pop()
            W = stack.pop()
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
        binding_24.is_binding = True
        for idx, x in enumerate(target):
            stack.append(acc)
            stack.append(x)
            s = stack.pop()
            A = stack.pop()
            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
            acc = stack.pop()
        stack.append(acc)
    def binding_22(stack):
        execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
        init = stack.pop()
        target = stack.pop()
        acc = init
        def binding_25(stack):
            g = stack.pop()
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
        binding_25.is_binding = True
        def binding_24(stack):
            y = stack.pop()
            x = stack.pop()
            b = stack.pop()
            W = stack.pop()
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
        binding_24.is_binding = True
        def binding_23(stack):
            execute([lambda stack, M=M: stack.append(M)], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                s = stack.pop()
                A = stack.pop()
                execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                acc = stack.pop()
            stack.append(acc)
        for idx, x in enumerate(target):
            stack.append(acc)
            stack.append(x)
            e = stack.pop()
            M = stack.pop()
            execute([lambda stack, D=D: stack.append(D), binding_23], stack)
            acc = stack.pop()
        stack.append(acc)
    def binding_26(stack):
        M = stack.pop()
        execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
    binding_26.is_binding = True
    def binding_21(stack):
        step = stack.pop()
        def binding_25(stack):
            g = stack.pop()
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
        binding_25.is_binding = True
        def binding_24(stack):
            y = stack.pop()
            x = stack.pop()
            b = stack.pop()
            W = stack.pop()
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
        binding_24.is_binding = True
        def binding_23(stack):
            execute([lambda stack, M=M: stack.append(M)], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                s = stack.pop()
                A = stack.pop()
                execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_22(stack):
            execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                e = stack.pop()
                M = stack.pop()
                execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_26(stack):
            M = stack.pop()
            execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
        binding_26.is_binding = True
        execute([[0, 0, 0], binding_22, binding_26], stack)
    binding_21.is_binding = True
    def binding_16(stack):
        grad = stack.pop()
        def binding_19(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                w = stack.pop()
                j = stack.pop()
                execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_18(stack):
            target = stack.pop()
            res = []
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                q = stack.pop()
                i = stack.pop()
                execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_20(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_17(stack):
            r = stack.pop()
            g = stack.pop()
            x = stack.pop()
            b = stack.pop()
            W = stack.pop()
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_18(stack):
                target = stack.pop()
                res = []
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
        binding_17.is_binding = True
        def binding_25(stack):
            g = stack.pop()
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
        binding_25.is_binding = True
        def binding_24(stack):
            y = stack.pop()
            x = stack.pop()
            b = stack.pop()
            W = stack.pop()
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
        binding_24.is_binding = True
        def binding_23(stack):
            execute([lambda stack, M=M: stack.append(M)], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                s = stack.pop()
                A = stack.pop()
                execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_22(stack):
            execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                e = stack.pop()
                M = stack.pop()
                execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_26(stack):
            M = stack.pop()
            execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
        binding_26.is_binding = True
        def binding_21(stack):
            step = stack.pop()
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e = stack.pop()
                    M = stack.pop()
                    execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M = stack.pop()
                execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
            binding_26.is_binding = True
            execute([[0, 0, 0], binding_22, binding_26], stack)
        binding_21.is_binding = True
        execute([[binding_17], binding_21], stack)
    binding_16.is_binding = True
    def binding_13(stack):
        smax = stack.pop()
        def binding_15(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_14(stack):
            y = stack.pop()
            p = stack.pop()
            def binding_15(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, p=p: stack.append(p), binding_15], stack)
        binding_14.is_binding = True
        def binding_19(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                w = stack.pop()
                j = stack.pop()
                execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_18(stack):
            target = stack.pop()
            res = []
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                q = stack.pop()
                i = stack.pop()
                execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_20(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_17(stack):
            r = stack.pop()
            g = stack.pop()
            x = stack.pop()
            b = stack.pop()
            W = stack.pop()
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_18(stack):
                target = stack.pop()
                res = []
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
        binding_17.is_binding = True
        def binding_25(stack):
            g = stack.pop()
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
        binding_25.is_binding = True
        def binding_24(stack):
            y = stack.pop()
            x = stack.pop()
            b = stack.pop()
            W = stack.pop()
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
        binding_24.is_binding = True
        def binding_23(stack):
            execute([lambda stack, M=M: stack.append(M)], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                s = stack.pop()
                A = stack.pop()
                execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_22(stack):
            execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                e = stack.pop()
                M = stack.pop()
                execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_26(stack):
            M = stack.pop()
            execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
        binding_26.is_binding = True
        def binding_21(stack):
            step = stack.pop()
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e = stack.pop()
                    M = stack.pop()
                    execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M = stack.pop()
                execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
            binding_26.is_binding = True
            execute([[0, 0, 0], binding_22, binding_26], stack)
        binding_21.is_binding = True
        def binding_16(stack):
            grad = stack.pop()
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_18(stack):
                target = stack.pop()
                res = []
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_17(stack):
                r = stack.pop()
                g = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_18(stack):
                    target = stack.pop()
                    res = []
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
            binding_17.is_binding = True
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e = stack.pop()
                    M = stack.pop()
                    execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M = stack.pop()
                execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
            binding_26.is_binding = True
            def binding_21(stack):
                step = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e = stack.pop()
                        M = stack.pop()
                        execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M = stack.pop()
                    execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                binding_26.is_binding = True
                execute([[0, 0, 0], binding_22, binding_26], stack)
            binding_21.is_binding = True
            execute([[binding_17], binding_21], stack)
        binding_16.is_binding = True
        execute([[binding_14], binding_16], stack)
    binding_13.is_binding = True
    def binding_7(stack):
        fwd = stack.pop()
        def binding_9(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, v=v: stack.append(v), op_exp], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_10(stack):
            execute([0.0], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                v = stack.pop()
                a = stack.pop()
                execute([lambda stack, a=a: stack.append(a), lambda stack, v=v: stack.append(v), op_add], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_12(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_11(stack):
            s = stack.pop()
            e = stack.pop()
            def binding_12(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, e=e: stack.append(e), binding_12], stack)
        binding_11.is_binding = True
        def binding_8(stack):
            z = stack.pop()
            def binding_9(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), op_exp], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_10(stack):
                execute([0.0], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    v = stack.pop()
                    a = stack.pop()
                    execute([lambda stack, a=a: stack.append(a), lambda stack, v=v: stack.append(v), op_add], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_12(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_11(stack):
                s = stack.pop()
                e = stack.pop()
                def binding_12(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, e=e: stack.append(e), binding_12], stack)
            binding_11.is_binding = True
            execute([lambda stack, z=z: stack.append(z), binding_9, op_dup, binding_10, binding_11], stack)
        binding_8.is_binding = True
        def binding_15(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_14(stack):
            y = stack.pop()
            p = stack.pop()
            def binding_15(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, p=p: stack.append(p), binding_15], stack)
        binding_14.is_binding = True
        def binding_19(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                w = stack.pop()
                j = stack.pop()
                execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_18(stack):
            target = stack.pop()
            res = []
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                q = stack.pop()
                i = stack.pop()
                execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_20(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_17(stack):
            r = stack.pop()
            g = stack.pop()
            x = stack.pop()
            b = stack.pop()
            W = stack.pop()
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_18(stack):
                target = stack.pop()
                res = []
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
        binding_17.is_binding = True
        def binding_25(stack):
            g = stack.pop()
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
        binding_25.is_binding = True
        def binding_24(stack):
            y = stack.pop()
            x = stack.pop()
            b = stack.pop()
            W = stack.pop()
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
        binding_24.is_binding = True
        def binding_23(stack):
            execute([lambda stack, M=M: stack.append(M)], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                s = stack.pop()
                A = stack.pop()
                execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_22(stack):
            execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                e = stack.pop()
                M = stack.pop()
                execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_26(stack):
            M = stack.pop()
            execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
        binding_26.is_binding = True
        def binding_21(stack):
            step = stack.pop()
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e = stack.pop()
                    M = stack.pop()
                    execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M = stack.pop()
                execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
            binding_26.is_binding = True
            execute([[0, 0, 0], binding_22, binding_26], stack)
        binding_21.is_binding = True
        def binding_16(stack):
            grad = stack.pop()
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_18(stack):
                target = stack.pop()
                res = []
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_17(stack):
                r = stack.pop()
                g = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_18(stack):
                    target = stack.pop()
                    res = []
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
            binding_17.is_binding = True
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e = stack.pop()
                    M = stack.pop()
                    execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M = stack.pop()
                execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
            binding_26.is_binding = True
            def binding_21(stack):
                step = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e = stack.pop()
                        M = stack.pop()
                        execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M = stack.pop()
                    execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                binding_26.is_binding = True
                execute([[0, 0, 0], binding_22, binding_26], stack)
            binding_21.is_binding = True
            execute([[binding_17], binding_21], stack)
        binding_16.is_binding = True
        def binding_13(stack):
            smax = stack.pop()
            def binding_15(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_14(stack):
                y = stack.pop()
                p = stack.pop()
                def binding_15(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, p=p: stack.append(p), binding_15], stack)
            binding_14.is_binding = True
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_18(stack):
                target = stack.pop()
                res = []
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_17(stack):
                r = stack.pop()
                g = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_18(stack):
                    target = stack.pop()
                    res = []
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
            binding_17.is_binding = True
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e = stack.pop()
                    M = stack.pop()
                    execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M = stack.pop()
                execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
            binding_26.is_binding = True
            def binding_21(stack):
                step = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e = stack.pop()
                        M = stack.pop()
                        execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M = stack.pop()
                    execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                binding_26.is_binding = True
                execute([[0, 0, 0], binding_22, binding_26], stack)
            binding_21.is_binding = True
            def binding_16(stack):
                grad = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_18(stack):
                    target = stack.pop()
                    res = []
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_17(stack):
                    r = stack.pop()
                    g = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_18(stack):
                        target = stack.pop()
                        res = []
                        def binding_19(stack):
                            target = stack.pop()
                            res = []
                            for idx, x in enumerate(target):
                                stack.append(idx)
                                stack.append(x)
                                w = stack.pop()
                                j = stack.pop()
                                execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            q = stack.pop()
                            i = stack.pop()
                            execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_20(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v = stack.pop()
                            i = stack.pop()
                            execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
                binding_17.is_binding = True
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e = stack.pop()
                        M = stack.pop()
                        execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M = stack.pop()
                    execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                binding_26.is_binding = True
                def binding_21(stack):
                    step = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_22(stack):
                        execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        def binding_23(stack):
                            execute([lambda stack, M=M: stack.append(M)], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            def binding_24(stack):
                                y = stack.pop()
                                x = stack.pop()
                                b = stack.pop()
                                W = stack.pop()
                                def binding_25(stack):
                                    g = stack.pop()
                                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                            binding_24.is_binding = True
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                s = stack.pop()
                                A = stack.pop()
                                execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            e = stack.pop()
                            M = stack.pop()
                            execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_26(stack):
                        M = stack.pop()
                        execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                    binding_26.is_binding = True
                    execute([[0, 0, 0], binding_22, binding_26], stack)
                binding_21.is_binding = True
                execute([[binding_17], binding_21], stack)
            binding_16.is_binding = True
            execute([[binding_14], binding_16], stack)
        binding_13.is_binding = True
        execute([[binding_8], binding_13], stack)
    binding_7.is_binding = True
    def binding_4(stack):
        dot = stack.pop()
        def binding_6(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                r = stack.pop()
                i = stack.pop()
                execute([lambda stack, r=r: stack.append(r), lambda stack, x=x: stack.append(x), binding_1, lambda stack, b=b: stack.append(b), lambda stack, i=i: stack.append(i), op_get, op_add], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_5(stack):
            x = stack.pop()
            b = stack.pop()
            W = stack.pop()
            def binding_6(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    r = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, r=r: stack.append(r), lambda stack, x=x: stack.append(x), binding_1, lambda stack, b=b: stack.append(b), lambda stack, i=i: stack.append(i), op_get, op_add], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, W=W: stack.append(W), binding_6], stack)
        binding_5.is_binding = True
        def binding_9(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, v=v: stack.append(v), op_exp], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_10(stack):
            execute([0.0], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                v = stack.pop()
                a = stack.pop()
                execute([lambda stack, a=a: stack.append(a), lambda stack, v=v: stack.append(v), op_add], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_12(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_11(stack):
            s = stack.pop()
            e = stack.pop()
            def binding_12(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, e=e: stack.append(e), binding_12], stack)
        binding_11.is_binding = True
        def binding_8(stack):
            z = stack.pop()
            def binding_9(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), op_exp], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_10(stack):
                execute([0.0], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    v = stack.pop()
                    a = stack.pop()
                    execute([lambda stack, a=a: stack.append(a), lambda stack, v=v: stack.append(v), op_add], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_12(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_11(stack):
                s = stack.pop()
                e = stack.pop()
                def binding_12(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, e=e: stack.append(e), binding_12], stack)
            binding_11.is_binding = True
            execute([lambda stack, z=z: stack.append(z), binding_9, op_dup, binding_10, binding_11], stack)
        binding_8.is_binding = True
        def binding_15(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_14(stack):
            y = stack.pop()
            p = stack.pop()
            def binding_15(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, p=p: stack.append(p), binding_15], stack)
        binding_14.is_binding = True
        def binding_19(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                w = stack.pop()
                j = stack.pop()
                execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_18(stack):
            target = stack.pop()
            res = []
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                q = stack.pop()
                i = stack.pop()
                execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_20(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v = stack.pop()
                i = stack.pop()
                execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_17(stack):
            r = stack.pop()
            g = stack.pop()
            x = stack.pop()
            b = stack.pop()
            W = stack.pop()
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_18(stack):
                target = stack.pop()
                res = []
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
        binding_17.is_binding = True
        def binding_25(stack):
            g = stack.pop()
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
        binding_25.is_binding = True
        def binding_24(stack):
            y = stack.pop()
            x = stack.pop()
            b = stack.pop()
            W = stack.pop()
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
        binding_24.is_binding = True
        def binding_23(stack):
            execute([lambda stack, M=M: stack.append(M)], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                s = stack.pop()
                A = stack.pop()
                execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_22(stack):
            execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                e = stack.pop()
                M = stack.pop()
                execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_26(stack):
            M = stack.pop()
            execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
        binding_26.is_binding = True
        def binding_21(stack):
            step = stack.pop()
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e = stack.pop()
                    M = stack.pop()
                    execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M = stack.pop()
                execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
            binding_26.is_binding = True
            execute([[0, 0, 0], binding_22, binding_26], stack)
        binding_21.is_binding = True
        def binding_16(stack):
            grad = stack.pop()
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_18(stack):
                target = stack.pop()
                res = []
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_17(stack):
                r = stack.pop()
                g = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_18(stack):
                    target = stack.pop()
                    res = []
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
            binding_17.is_binding = True
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e = stack.pop()
                    M = stack.pop()
                    execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M = stack.pop()
                execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
            binding_26.is_binding = True
            def binding_21(stack):
                step = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e = stack.pop()
                        M = stack.pop()
                        execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M = stack.pop()
                    execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                binding_26.is_binding = True
                execute([[0, 0, 0], binding_22, binding_26], stack)
            binding_21.is_binding = True
            execute([[binding_17], binding_21], stack)
        binding_16.is_binding = True
        def binding_13(stack):
            smax = stack.pop()
            def binding_15(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_14(stack):
                y = stack.pop()
                p = stack.pop()
                def binding_15(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, p=p: stack.append(p), binding_15], stack)
            binding_14.is_binding = True
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_18(stack):
                target = stack.pop()
                res = []
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_17(stack):
                r = stack.pop()
                g = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_18(stack):
                    target = stack.pop()
                    res = []
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
            binding_17.is_binding = True
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e = stack.pop()
                    M = stack.pop()
                    execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M = stack.pop()
                execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
            binding_26.is_binding = True
            def binding_21(stack):
                step = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e = stack.pop()
                        M = stack.pop()
                        execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M = stack.pop()
                    execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                binding_26.is_binding = True
                execute([[0, 0, 0], binding_22, binding_26], stack)
            binding_21.is_binding = True
            def binding_16(stack):
                grad = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_18(stack):
                    target = stack.pop()
                    res = []
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_17(stack):
                    r = stack.pop()
                    g = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_18(stack):
                        target = stack.pop()
                        res = []
                        def binding_19(stack):
                            target = stack.pop()
                            res = []
                            for idx, x in enumerate(target):
                                stack.append(idx)
                                stack.append(x)
                                w = stack.pop()
                                j = stack.pop()
                                execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            q = stack.pop()
                            i = stack.pop()
                            execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_20(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v = stack.pop()
                            i = stack.pop()
                            execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
                binding_17.is_binding = True
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e = stack.pop()
                        M = stack.pop()
                        execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M = stack.pop()
                    execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                binding_26.is_binding = True
                def binding_21(stack):
                    step = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_22(stack):
                        execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        def binding_23(stack):
                            execute([lambda stack, M=M: stack.append(M)], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            def binding_24(stack):
                                y = stack.pop()
                                x = stack.pop()
                                b = stack.pop()
                                W = stack.pop()
                                def binding_25(stack):
                                    g = stack.pop()
                                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                            binding_24.is_binding = True
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                s = stack.pop()
                                A = stack.pop()
                                execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            e = stack.pop()
                            M = stack.pop()
                            execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_26(stack):
                        M = stack.pop()
                        execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                    binding_26.is_binding = True
                    execute([[0, 0, 0], binding_22, binding_26], stack)
                binding_21.is_binding = True
                execute([[binding_17], binding_21], stack)
            binding_16.is_binding = True
            execute([[binding_14], binding_16], stack)
        binding_13.is_binding = True
        def binding_7(stack):
            fwd = stack.pop()
            def binding_9(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), op_exp], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_10(stack):
                execute([0.0], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    v = stack.pop()
                    a = stack.pop()
                    execute([lambda stack, a=a: stack.append(a), lambda stack, v=v: stack.append(v), op_add], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_12(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_11(stack):
                s = stack.pop()
                e = stack.pop()
                def binding_12(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, e=e: stack.append(e), binding_12], stack)
            binding_11.is_binding = True
            def binding_8(stack):
                z = stack.pop()
                def binding_9(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), op_exp], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_10(stack):
                    execute([0.0], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        v = stack.pop()
                        a = stack.pop()
                        execute([lambda stack, a=a: stack.append(a), lambda stack, v=v: stack.append(v), op_add], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_12(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_11(stack):
                    s = stack.pop()
                    e = stack.pop()
                    def binding_12(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v = stack.pop()
                            i = stack.pop()
                            execute([lambda stack, v=v: stack.append(v), lambda stack, s=s: stack.append(s), op_div], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    execute([lambda stack, e=e: stack.append(e), binding_12], stack)
                binding_11.is_binding = True
                execute([lambda stack, z=z: stack.append(z), binding_9, op_dup, binding_10, binding_11], stack)
            binding_8.is_binding = True
            def binding_15(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_14(stack):
                y = stack.pop()
                p = stack.pop()
                def binding_15(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, p=p: stack.append(p), binding_15], stack)
            binding_14.is_binding = True
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w = stack.pop()
                    j = stack.pop()
                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_18(stack):
                target = stack.pop()
                res = []
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v = stack.pop()
                    i = stack.pop()
                    execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_17(stack):
                r = stack.pop()
                g = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_18(stack):
                    target = stack.pop()
                    res = []
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
            binding_17.is_binding = True
            def binding_25(stack):
                g = stack.pop()
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y = stack.pop()
                x = stack.pop()
                b = stack.pop()
                W = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M=M: stack.append(M)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s = stack.pop()
                    A = stack.pop()
                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e = stack.pop()
                    M = stack.pop()
                    execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M = stack.pop()
                execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
            binding_26.is_binding = True
            def binding_21(stack):
                step = stack.pop()
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e = stack.pop()
                        M = stack.pop()
                        execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M = stack.pop()
                    execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                binding_26.is_binding = True
                execute([[0, 0, 0], binding_22, binding_26], stack)
            binding_21.is_binding = True
            def binding_16(stack):
                grad = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_18(stack):
                    target = stack.pop()
                    res = []
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_17(stack):
                    r = stack.pop()
                    g = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_18(stack):
                        target = stack.pop()
                        res = []
                        def binding_19(stack):
                            target = stack.pop()
                            res = []
                            for idx, x in enumerate(target):
                                stack.append(idx)
                                stack.append(x)
                                w = stack.pop()
                                j = stack.pop()
                                execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            q = stack.pop()
                            i = stack.pop()
                            execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_20(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v = stack.pop()
                            i = stack.pop()
                            execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
                binding_17.is_binding = True
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e = stack.pop()
                        M = stack.pop()
                        execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M = stack.pop()
                    execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                binding_26.is_binding = True
                def binding_21(stack):
                    step = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_22(stack):
                        execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        def binding_23(stack):
                            execute([lambda stack, M=M: stack.append(M)], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            def binding_24(stack):
                                y = stack.pop()
                                x = stack.pop()
                                b = stack.pop()
                                W = stack.pop()
                                def binding_25(stack):
                                    g = stack.pop()
                                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                            binding_24.is_binding = True
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                s = stack.pop()
                                A = stack.pop()
                                execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            e = stack.pop()
                            M = stack.pop()
                            execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_26(stack):
                        M = stack.pop()
                        execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                    binding_26.is_binding = True
                    execute([[0, 0, 0], binding_22, binding_26], stack)
                binding_21.is_binding = True
                execute([[binding_17], binding_21], stack)
            binding_16.is_binding = True
            def binding_13(stack):
                smax = stack.pop()
                def binding_15(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_14(stack):
                    y = stack.pop()
                    p = stack.pop()
                    def binding_15(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v = stack.pop()
                            i = stack.pop()
                            execute([lambda stack, i=i: stack.append(i), lambda stack, y=y: stack.append(y), op_eq, [lambda stack, v=v: stack.append(v), 1.0, op_sub], [lambda stack, v=v: stack.append(v)], op_ifelse], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    execute([lambda stack, p=p: stack.append(p), binding_15], stack)
                binding_14.is_binding = True
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w = stack.pop()
                        j = stack.pop()
                        execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_18(stack):
                    target = stack.pop()
                    res = []
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v = stack.pop()
                        i = stack.pop()
                        execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_17(stack):
                    r = stack.pop()
                    g = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_18(stack):
                        target = stack.pop()
                        res = []
                        def binding_19(stack):
                            target = stack.pop()
                            res = []
                            for idx, x in enumerate(target):
                                stack.append(idx)
                                stack.append(x)
                                w = stack.pop()
                                j = stack.pop()
                                execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            q = stack.pop()
                            i = stack.pop()
                            execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_20(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v = stack.pop()
                            i = stack.pop()
                            execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
                binding_17.is_binding = True
                def binding_25(stack):
                    g = stack.pop()
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y = stack.pop()
                    x = stack.pop()
                    b = stack.pop()
                    W = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M=M: stack.append(M)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s = stack.pop()
                        A = stack.pop()
                        execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e = stack.pop()
                        M = stack.pop()
                        execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M = stack.pop()
                    execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                binding_26.is_binding = True
                def binding_21(stack):
                    step = stack.pop()
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_22(stack):
                        execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        def binding_23(stack):
                            execute([lambda stack, M=M: stack.append(M)], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            def binding_24(stack):
                                y = stack.pop()
                                x = stack.pop()
                                b = stack.pop()
                                W = stack.pop()
                                def binding_25(stack):
                                    g = stack.pop()
                                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                            binding_24.is_binding = True
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                s = stack.pop()
                                A = stack.pop()
                                execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            e = stack.pop()
                            M = stack.pop()
                            execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_26(stack):
                        M = stack.pop()
                        execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                    binding_26.is_binding = True
                    execute([[0, 0, 0], binding_22, binding_26], stack)
                binding_21.is_binding = True
                def binding_16(stack):
                    grad = stack.pop()
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w = stack.pop()
                            j = stack.pop()
                            execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_18(stack):
                        target = stack.pop()
                        res = []
                        def binding_19(stack):
                            target = stack.pop()
                            res = []
                            for idx, x in enumerate(target):
                                stack.append(idx)
                                stack.append(x)
                                w = stack.pop()
                                j = stack.pop()
                                execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            q = stack.pop()
                            i = stack.pop()
                            execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_20(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v = stack.pop()
                            i = stack.pop()
                            execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_17(stack):
                        r = stack.pop()
                        g = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_19(stack):
                            target = stack.pop()
                            res = []
                            for idx, x in enumerate(target):
                                stack.append(idx)
                                stack.append(x)
                                w = stack.pop()
                                j = stack.pop()
                                execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        def binding_18(stack):
                            target = stack.pop()
                            res = []
                            def binding_19(stack):
                                target = stack.pop()
                                res = []
                                for idx, x in enumerate(target):
                                    stack.append(idx)
                                    stack.append(x)
                                    w = stack.pop()
                                    j = stack.pop()
                                    execute([lambda stack, w=w: stack.append(w), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, lambda stack, x=x: stack.append(x), lambda stack, j=j: stack.append(j), op_get, op_mul, op_sub], stack)
                                    res.append(stack.pop())
                                stack.append(res)
                            for idx, x in enumerate(target):
                                stack.append(idx)
                                stack.append(x)
                                q = stack.pop()
                                i = stack.pop()
                                execute([lambda stack, q=q: stack.append(q), binding_19], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        def binding_20(stack):
                            target = stack.pop()
                            res = []
                            for idx, x in enumerate(target):
                                stack.append(idx)
                                stack.append(x)
                                v = stack.pop()
                                i = stack.pop()
                                execute([lambda stack, v=v: stack.append(v), lambda stack, r=r: stack.append(r), lambda stack, g=g: stack.append(g), lambda stack, i=i: stack.append(i), op_get, op_mul, op_sub], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        execute([lambda stack, W=W: stack.append(W), binding_18, lambda stack, b=b: stack.append(b), binding_20, [], op_cons, op_cons], stack)
                    binding_17.is_binding = True
                    def binding_25(stack):
                        g = stack.pop()
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y = stack.pop()
                        x = stack.pop()
                        b = stack.pop()
                        W = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M=M: stack.append(M)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s = stack.pop()
                            A = stack.pop()
                            execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_22(stack):
                        execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        def binding_23(stack):
                            execute([lambda stack, M=M: stack.append(M)], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            def binding_24(stack):
                                y = stack.pop()
                                x = stack.pop()
                                b = stack.pop()
                                W = stack.pop()
                                def binding_25(stack):
                                    g = stack.pop()
                                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                            binding_24.is_binding = True
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                s = stack.pop()
                                A = stack.pop()
                                execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            e = stack.pop()
                            M = stack.pop()
                            execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_26(stack):
                        M = stack.pop()
                        execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                    binding_26.is_binding = True
                    def binding_21(stack):
                        step = stack.pop()
                        def binding_25(stack):
                            g = stack.pop()
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y = stack.pop()
                            x = stack.pop()
                            b = stack.pop()
                            W = stack.pop()
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        def binding_23(stack):
                            execute([lambda stack, M=M: stack.append(M)], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            def binding_24(stack):
                                y = stack.pop()
                                x = stack.pop()
                                b = stack.pop()
                                W = stack.pop()
                                def binding_25(stack):
                                    g = stack.pop()
                                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                            binding_24.is_binding = True
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                s = stack.pop()
                                A = stack.pop()
                                execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        def binding_22(stack):
                            execute([lambda stack, W0=W0: stack.append(W0), lambda stack, b0=b0: stack.append(b0), [], op_cons, op_cons], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_25(stack):
                                g = stack.pop()
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            def binding_24(stack):
                                y = stack.pop()
                                x = stack.pop()
                                b = stack.pop()
                                W = stack.pop()
                                def binding_25(stack):
                                    g = stack.pop()
                                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                            binding_24.is_binding = True
                            def binding_23(stack):
                                execute([lambda stack, M=M: stack.append(M)], stack)
                                init = stack.pop()
                                target = stack.pop()
                                acc = init
                                def binding_25(stack):
                                    g = stack.pop()
                                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                def binding_24(stack):
                                    y = stack.pop()
                                    x = stack.pop()
                                    b = stack.pop()
                                    W = stack.pop()
                                    def binding_25(stack):
                                        g = stack.pop()
                                        execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), lambda stack, g=g: stack.append(g), 0.01, binding_17], stack)
                                    binding_25.is_binding = True
                                    execute([lambda stack, W=W: stack.append(W), lambda stack, b=b: stack.append(b), lambda stack, x=x: stack.append(x), binding_5, binding_8, lambda stack, y=y: stack.append(y), binding_14, binding_25], stack)
                                binding_24.is_binding = True
                                for idx, x in enumerate(target):
                                    stack.append(acc)
                                    stack.append(x)
                                    s = stack.pop()
                                    A = stack.pop()
                                    execute([lambda stack, A=A: stack.append(A), 0, op_get, lambda stack, A=A: stack.append(A), 1, op_get, lambda stack, s=s: stack.append(s), 0, op_get, lambda stack, s=s: stack.append(s), 1, op_get, binding_24], stack)
                                    acc = stack.pop()
                                stack.append(acc)
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                e = stack.pop()
                                M = stack.pop()
                                execute([lambda stack, D=D: stack.append(D), binding_23], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        def binding_26(stack):
                            M = stack.pop()
                            execute([lambda stack, M=M: stack.append(M), 0, op_get, lambda stack, M=M: stack.append(M), 1, op_get], stack)
                        binding_26.is_binding = True
                        execute([[0, 0, 0], binding_22, binding_26], stack)
                    binding_21.is_binding = True
                    execute([[binding_17], binding_21], stack)
                binding_16.is_binding = True
                execute([[binding_14], binding_16], stack)
            binding_13.is_binding = True
            execute([[binding_8], binding_13], stack)
        binding_7.is_binding = True
        execute([[binding_5], binding_7], stack)
    binding_4.is_binding = True

    execute([[binding_1], binding_4], stack)
    return stack