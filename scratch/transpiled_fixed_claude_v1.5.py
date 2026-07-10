# Transpiled Scrooge Code
import sys
import math

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
        stack.append(lst[idx])
    else:
        stack.append(stack[-1 - idx])
def op_set(stack):
    v = stack.pop(); idx = stack.pop(); lst = stack.pop()
    new_lst = list(lst); new_lst[idx] = v; stack.append(new_lst)


def run(initial_stack=None):
    if initial_stack is None:
        stack = []
    else:
        stack = list(initial_stack)
    b0_1 = stack.pop()
    W0_1 = stack.pop()
    D_1 = stack.pop()
    def binding_2(stack):
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            v_5 = stack.pop()
            i_4 = stack.pop()
            execute([lambda stack, v_5=v_5: stack.append(v_5), lambda stack, x_2=x_2: stack.append(x_2), lambda stack, i_4=i_4: stack.append(i_4), op_get, op_mul], stack)
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
            v_7 = stack.pop()
            a_6 = stack.pop()
            execute([lambda stack, a_6=a_6: stack.append(a_6), lambda stack, v_7=v_7: stack.append(v_7), op_add], stack)
            acc = stack.pop()
        stack.append(acc)
    def binding_1(stack):
        x_2 = stack.pop()
        w_3 = stack.pop()
        def binding_2(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_5 = stack.pop()
                i_4 = stack.pop()
                execute([lambda stack, v_5=v_5: stack.append(v_5), lambda stack, x_2=x_2: stack.append(x_2), lambda stack, i_4=i_4: stack.append(i_4), op_get, op_mul], stack)
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
                v_7 = stack.pop()
                a_6 = stack.pop()
                execute([lambda stack, a_6=a_6: stack.append(a_6), lambda stack, v_7=v_7: stack.append(v_7), op_add], stack)
                acc = stack.pop()
            stack.append(acc)
        execute([lambda stack, w_3=w_3: stack.append(w_3), binding_2, binding_3], stack)
    binding_1.is_binding = True
    def binding_6(stack):
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            r_13 = stack.pop()
            i_12 = stack.pop()
            execute([lambda stack, r_13=r_13: stack.append(r_13), lambda stack, x_9=x_9: stack.append(x_9), binding_1, lambda stack, b_10=b_10: stack.append(b_10), lambda stack, i_12=i_12: stack.append(i_12), op_get, op_add], stack)
            res.append(stack.pop())
        stack.append(res)
    def binding_5(stack):
        x_9 = stack.pop()
        b_10 = stack.pop()
        W_11 = stack.pop()
        def binding_6(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                r_13 = stack.pop()
                i_12 = stack.pop()
                execute([lambda stack, r_13=r_13: stack.append(r_13), lambda stack, x_9=x_9: stack.append(x_9), binding_1, lambda stack, b_10=b_10: stack.append(b_10), lambda stack, i_12=i_12: stack.append(i_12), op_get, op_add], stack)
                res.append(stack.pop())
            stack.append(res)
        execute([lambda stack, W_11=W_11: stack.append(W_11), binding_6], stack)
    binding_5.is_binding = True
    def binding_9(stack):
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            v_17 = stack.pop()
            i_16 = stack.pop()
            execute([lambda stack, v_17=v_17: stack.append(v_17), op_exp], stack)
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
            v_19 = stack.pop()
            a_18 = stack.pop()
            execute([lambda stack, a_18=a_18: stack.append(a_18), lambda stack, v_19=v_19: stack.append(v_19), op_add], stack)
            acc = stack.pop()
        stack.append(acc)
    def binding_12(stack):
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            v_23 = stack.pop()
            i_22 = stack.pop()
            execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
            res.append(stack.pop())
        stack.append(res)
    def binding_11(stack):
        s_20 = stack.pop()
        e_21 = stack.pop()
        def binding_12(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_23 = stack.pop()
                i_22 = stack.pop()
                execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                res.append(stack.pop())
            stack.append(res)
        execute([lambda stack, e_21=e_21: stack.append(e_21), binding_12], stack)
    binding_11.is_binding = True
    def binding_8(stack):
        z_15 = stack.pop()
        def binding_9(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_17 = stack.pop()
                i_16 = stack.pop()
                execute([lambda stack, v_17=v_17: stack.append(v_17), op_exp], stack)
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
                v_19 = stack.pop()
                a_18 = stack.pop()
                execute([lambda stack, a_18=a_18: stack.append(a_18), lambda stack, v_19=v_19: stack.append(v_19), op_add], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_12(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_23 = stack.pop()
                i_22 = stack.pop()
                execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_11(stack):
            s_20 = stack.pop()
            e_21 = stack.pop()
            def binding_12(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_23 = stack.pop()
                    i_22 = stack.pop()
                    execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, e_21=e_21: stack.append(e_21), binding_12], stack)
        binding_11.is_binding = True
        execute([lambda stack, z_15=z_15: stack.append(z_15), binding_9, op_dup, binding_10, binding_11], stack)
    binding_8.is_binding = True
    def binding_15(stack):
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            v_28 = stack.pop()
            i_27 = stack.pop()
            execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
            res.append(stack.pop())
        stack.append(res)
    def binding_14(stack):
        y_25 = stack.pop()
        p_26 = stack.pop()
        def binding_15(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_28 = stack.pop()
                i_27 = stack.pop()
                execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        execute([lambda stack, p_26=p_26: stack.append(p_26), binding_15], stack)
    binding_14.is_binding = True
    def binding_19(stack):
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            w_38 = stack.pop()
            j_37 = stack.pop()
            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                w_38 = stack.pop()
                j_37 = stack.pop()
                execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            q_36 = stack.pop()
            i_35 = stack.pop()
            execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
            res.append(stack.pop())
        stack.append(res)
    def binding_20(stack):
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            v_40 = stack.pop()
            i_39 = stack.pop()
            execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
            res.append(stack.pop())
        stack.append(res)
    def binding_17(stack):
        r_30 = stack.pop()
        g_31 = stack.pop()
        x_32 = stack.pop()
        b_33 = stack.pop()
        W_34 = stack.pop()
        def binding_19(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                w_38 = stack.pop()
                j_37 = stack.pop()
                execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                q_36 = stack.pop()
                i_35 = stack.pop()
                execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_20(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_40 = stack.pop()
                i_39 = stack.pop()
                execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
    binding_17.is_binding = True
    def binding_25(stack):
        g_50 = stack.pop()
        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
    binding_25.is_binding = True
    def binding_24(stack):
        y_46 = stack.pop()
        x_47 = stack.pop()
        b_48 = stack.pop()
        W_49 = stack.pop()
        def binding_25(stack):
            g_50 = stack.pop()
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
        binding_25.is_binding = True
        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
    binding_24.is_binding = True
    def binding_23(stack):
        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
        init = stack.pop()
        target = stack.pop()
        acc = init
        def binding_25(stack):
            g_50 = stack.pop()
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
        binding_25.is_binding = True
        def binding_24(stack):
            y_46 = stack.pop()
            x_47 = stack.pop()
            b_48 = stack.pop()
            W_49 = stack.pop()
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
        binding_24.is_binding = True
        for idx, x in enumerate(target):
            stack.append(acc)
            stack.append(x)
            s_45 = stack.pop()
            A_44 = stack.pop()
            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
            acc = stack.pop()
        stack.append(acc)
    def binding_22(stack):
        execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
        init = stack.pop()
        target = stack.pop()
        acc = init
        def binding_25(stack):
            g_50 = stack.pop()
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
        binding_25.is_binding = True
        def binding_24(stack):
            y_46 = stack.pop()
            x_47 = stack.pop()
            b_48 = stack.pop()
            W_49 = stack.pop()
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
        binding_24.is_binding = True
        def binding_23(stack):
            execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                s_45 = stack.pop()
                A_44 = stack.pop()
                execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                acc = stack.pop()
            stack.append(acc)
        for idx, x in enumerate(target):
            stack.append(acc)
            stack.append(x)
            e_43 = stack.pop()
            M_42 = stack.pop()
            execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
            acc = stack.pop()
        stack.append(acc)
    def binding_26(stack):
        M_51 = stack.pop()
        execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
    binding_26.is_binding = True
    def binding_21(stack):
        step_41 = stack.pop()
        def binding_25(stack):
            g_50 = stack.pop()
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
        binding_25.is_binding = True
        def binding_24(stack):
            y_46 = stack.pop()
            x_47 = stack.pop()
            b_48 = stack.pop()
            W_49 = stack.pop()
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
        binding_24.is_binding = True
        def binding_23(stack):
            execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                s_45 = stack.pop()
                A_44 = stack.pop()
                execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_22(stack):
            execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                e_43 = stack.pop()
                M_42 = stack.pop()
                execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_26(stack):
            M_51 = stack.pop()
            execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
        binding_26.is_binding = True
        execute([[0, 0, 0], binding_22, binding_26], stack)
    binding_21.is_binding = True
    def binding_16(stack):
        grad_29 = stack.pop()
        def binding_19(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                w_38 = stack.pop()
                j_37 = stack.pop()
                execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                q_36 = stack.pop()
                i_35 = stack.pop()
                execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_20(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_40 = stack.pop()
                i_39 = stack.pop()
                execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_17(stack):
            r_30 = stack.pop()
            g_31 = stack.pop()
            x_32 = stack.pop()
            b_33 = stack.pop()
            W_34 = stack.pop()
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q_36 = stack.pop()
                    i_35 = stack.pop()
                    execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_40 = stack.pop()
                    i_39 = stack.pop()
                    execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
        binding_17.is_binding = True
        def binding_25(stack):
            g_50 = stack.pop()
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
        binding_25.is_binding = True
        def binding_24(stack):
            y_46 = stack.pop()
            x_47 = stack.pop()
            b_48 = stack.pop()
            W_49 = stack.pop()
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
        binding_24.is_binding = True
        def binding_23(stack):
            execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                s_45 = stack.pop()
                A_44 = stack.pop()
                execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_22(stack):
            execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                e_43 = stack.pop()
                M_42 = stack.pop()
                execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_26(stack):
            M_51 = stack.pop()
            execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
        binding_26.is_binding = True
        def binding_21(stack):
            step_41 = stack.pop()
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e_43 = stack.pop()
                    M_42 = stack.pop()
                    execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M_51 = stack.pop()
                execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
            binding_26.is_binding = True
            execute([[0, 0, 0], binding_22, binding_26], stack)
        binding_21.is_binding = True
        execute([[binding_17], binding_21], stack)
    binding_16.is_binding = True
    def binding_13(stack):
        smax_24 = stack.pop()
        def binding_15(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_28 = stack.pop()
                i_27 = stack.pop()
                execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_14(stack):
            y_25 = stack.pop()
            p_26 = stack.pop()
            def binding_15(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_28 = stack.pop()
                    i_27 = stack.pop()
                    execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, p_26=p_26: stack.append(p_26), binding_15], stack)
        binding_14.is_binding = True
        def binding_19(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                w_38 = stack.pop()
                j_37 = stack.pop()
                execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                q_36 = stack.pop()
                i_35 = stack.pop()
                execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_20(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_40 = stack.pop()
                i_39 = stack.pop()
                execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_17(stack):
            r_30 = stack.pop()
            g_31 = stack.pop()
            x_32 = stack.pop()
            b_33 = stack.pop()
            W_34 = stack.pop()
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q_36 = stack.pop()
                    i_35 = stack.pop()
                    execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_40 = stack.pop()
                    i_39 = stack.pop()
                    execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
        binding_17.is_binding = True
        def binding_25(stack):
            g_50 = stack.pop()
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
        binding_25.is_binding = True
        def binding_24(stack):
            y_46 = stack.pop()
            x_47 = stack.pop()
            b_48 = stack.pop()
            W_49 = stack.pop()
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
        binding_24.is_binding = True
        def binding_23(stack):
            execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                s_45 = stack.pop()
                A_44 = stack.pop()
                execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_22(stack):
            execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                e_43 = stack.pop()
                M_42 = stack.pop()
                execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_26(stack):
            M_51 = stack.pop()
            execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
        binding_26.is_binding = True
        def binding_21(stack):
            step_41 = stack.pop()
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e_43 = stack.pop()
                    M_42 = stack.pop()
                    execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M_51 = stack.pop()
                execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
            binding_26.is_binding = True
            execute([[0, 0, 0], binding_22, binding_26], stack)
        binding_21.is_binding = True
        def binding_16(stack):
            grad_29 = stack.pop()
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q_36 = stack.pop()
                    i_35 = stack.pop()
                    execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_40 = stack.pop()
                    i_39 = stack.pop()
                    execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_17(stack):
                r_30 = stack.pop()
                g_31 = stack.pop()
                x_32 = stack.pop()
                b_33 = stack.pop()
                W_34 = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q_36 = stack.pop()
                        i_35 = stack.pop()
                        execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_40 = stack.pop()
                        i_39 = stack.pop()
                        execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
            binding_17.is_binding = True
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e_43 = stack.pop()
                    M_42 = stack.pop()
                    execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M_51 = stack.pop()
                execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
            binding_26.is_binding = True
            def binding_21(stack):
                step_41 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e_43 = stack.pop()
                        M_42 = stack.pop()
                        execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M_51 = stack.pop()
                    execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
                binding_26.is_binding = True
                execute([[0, 0, 0], binding_22, binding_26], stack)
            binding_21.is_binding = True
            execute([[binding_17], binding_21], stack)
        binding_16.is_binding = True
        execute([[binding_14], binding_16], stack)
    binding_13.is_binding = True
    def binding_7(stack):
        fwd_14 = stack.pop()
        def binding_9(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_17 = stack.pop()
                i_16 = stack.pop()
                execute([lambda stack, v_17=v_17: stack.append(v_17), op_exp], stack)
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
                v_19 = stack.pop()
                a_18 = stack.pop()
                execute([lambda stack, a_18=a_18: stack.append(a_18), lambda stack, v_19=v_19: stack.append(v_19), op_add], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_12(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_23 = stack.pop()
                i_22 = stack.pop()
                execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_11(stack):
            s_20 = stack.pop()
            e_21 = stack.pop()
            def binding_12(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_23 = stack.pop()
                    i_22 = stack.pop()
                    execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, e_21=e_21: stack.append(e_21), binding_12], stack)
        binding_11.is_binding = True
        def binding_8(stack):
            z_15 = stack.pop()
            def binding_9(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_17 = stack.pop()
                    i_16 = stack.pop()
                    execute([lambda stack, v_17=v_17: stack.append(v_17), op_exp], stack)
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
                    v_19 = stack.pop()
                    a_18 = stack.pop()
                    execute([lambda stack, a_18=a_18: stack.append(a_18), lambda stack, v_19=v_19: stack.append(v_19), op_add], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_12(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_23 = stack.pop()
                    i_22 = stack.pop()
                    execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_11(stack):
                s_20 = stack.pop()
                e_21 = stack.pop()
                def binding_12(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_23 = stack.pop()
                        i_22 = stack.pop()
                        execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, e_21=e_21: stack.append(e_21), binding_12], stack)
            binding_11.is_binding = True
            execute([lambda stack, z_15=z_15: stack.append(z_15), binding_9, op_dup, binding_10, binding_11], stack)
        binding_8.is_binding = True
        def binding_15(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_28 = stack.pop()
                i_27 = stack.pop()
                execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_14(stack):
            y_25 = stack.pop()
            p_26 = stack.pop()
            def binding_15(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_28 = stack.pop()
                    i_27 = stack.pop()
                    execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, p_26=p_26: stack.append(p_26), binding_15], stack)
        binding_14.is_binding = True
        def binding_19(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                w_38 = stack.pop()
                j_37 = stack.pop()
                execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                q_36 = stack.pop()
                i_35 = stack.pop()
                execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_20(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_40 = stack.pop()
                i_39 = stack.pop()
                execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_17(stack):
            r_30 = stack.pop()
            g_31 = stack.pop()
            x_32 = stack.pop()
            b_33 = stack.pop()
            W_34 = stack.pop()
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q_36 = stack.pop()
                    i_35 = stack.pop()
                    execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_40 = stack.pop()
                    i_39 = stack.pop()
                    execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
        binding_17.is_binding = True
        def binding_25(stack):
            g_50 = stack.pop()
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
        binding_25.is_binding = True
        def binding_24(stack):
            y_46 = stack.pop()
            x_47 = stack.pop()
            b_48 = stack.pop()
            W_49 = stack.pop()
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
        binding_24.is_binding = True
        def binding_23(stack):
            execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                s_45 = stack.pop()
                A_44 = stack.pop()
                execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_22(stack):
            execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                e_43 = stack.pop()
                M_42 = stack.pop()
                execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_26(stack):
            M_51 = stack.pop()
            execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
        binding_26.is_binding = True
        def binding_21(stack):
            step_41 = stack.pop()
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e_43 = stack.pop()
                    M_42 = stack.pop()
                    execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M_51 = stack.pop()
                execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
            binding_26.is_binding = True
            execute([[0, 0, 0], binding_22, binding_26], stack)
        binding_21.is_binding = True
        def binding_16(stack):
            grad_29 = stack.pop()
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q_36 = stack.pop()
                    i_35 = stack.pop()
                    execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_40 = stack.pop()
                    i_39 = stack.pop()
                    execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_17(stack):
                r_30 = stack.pop()
                g_31 = stack.pop()
                x_32 = stack.pop()
                b_33 = stack.pop()
                W_34 = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q_36 = stack.pop()
                        i_35 = stack.pop()
                        execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_40 = stack.pop()
                        i_39 = stack.pop()
                        execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
            binding_17.is_binding = True
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e_43 = stack.pop()
                    M_42 = stack.pop()
                    execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M_51 = stack.pop()
                execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
            binding_26.is_binding = True
            def binding_21(stack):
                step_41 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e_43 = stack.pop()
                        M_42 = stack.pop()
                        execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M_51 = stack.pop()
                    execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
                binding_26.is_binding = True
                execute([[0, 0, 0], binding_22, binding_26], stack)
            binding_21.is_binding = True
            execute([[binding_17], binding_21], stack)
        binding_16.is_binding = True
        def binding_13(stack):
            smax_24 = stack.pop()
            def binding_15(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_28 = stack.pop()
                    i_27 = stack.pop()
                    execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_14(stack):
                y_25 = stack.pop()
                p_26 = stack.pop()
                def binding_15(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_28 = stack.pop()
                        i_27 = stack.pop()
                        execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, p_26=p_26: stack.append(p_26), binding_15], stack)
            binding_14.is_binding = True
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q_36 = stack.pop()
                    i_35 = stack.pop()
                    execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_40 = stack.pop()
                    i_39 = stack.pop()
                    execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_17(stack):
                r_30 = stack.pop()
                g_31 = stack.pop()
                x_32 = stack.pop()
                b_33 = stack.pop()
                W_34 = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q_36 = stack.pop()
                        i_35 = stack.pop()
                        execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_40 = stack.pop()
                        i_39 = stack.pop()
                        execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
            binding_17.is_binding = True
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e_43 = stack.pop()
                    M_42 = stack.pop()
                    execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M_51 = stack.pop()
                execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
            binding_26.is_binding = True
            def binding_21(stack):
                step_41 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e_43 = stack.pop()
                        M_42 = stack.pop()
                        execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M_51 = stack.pop()
                    execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
                binding_26.is_binding = True
                execute([[0, 0, 0], binding_22, binding_26], stack)
            binding_21.is_binding = True
            def binding_16(stack):
                grad_29 = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q_36 = stack.pop()
                        i_35 = stack.pop()
                        execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_40 = stack.pop()
                        i_39 = stack.pop()
                        execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_17(stack):
                    r_30 = stack.pop()
                    g_31 = stack.pop()
                    x_32 = stack.pop()
                    b_33 = stack.pop()
                    W_34 = stack.pop()
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                                w_38 = stack.pop()
                                j_37 = stack.pop()
                                execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            q_36 = stack.pop()
                            i_35 = stack.pop()
                            execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_20(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v_40 = stack.pop()
                            i_39 = stack.pop()
                            execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
                binding_17.is_binding = True
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e_43 = stack.pop()
                        M_42 = stack.pop()
                        execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M_51 = stack.pop()
                    execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
                binding_26.is_binding = True
                def binding_21(stack):
                    step_41 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_22(stack):
                        execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        def binding_23(stack):
                            execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            def binding_24(stack):
                                y_46 = stack.pop()
                                x_47 = stack.pop()
                                b_48 = stack.pop()
                                W_49 = stack.pop()
                                def binding_25(stack):
                                    g_50 = stack.pop()
                                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                            binding_24.is_binding = True
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                s_45 = stack.pop()
                                A_44 = stack.pop()
                                execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            e_43 = stack.pop()
                            M_42 = stack.pop()
                            execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_26(stack):
                        M_51 = stack.pop()
                        execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
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
        dot_8 = stack.pop()
        def binding_6(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                r_13 = stack.pop()
                i_12 = stack.pop()
                execute([lambda stack, r_13=r_13: stack.append(r_13), lambda stack, x_9=x_9: stack.append(x_9), binding_1, lambda stack, b_10=b_10: stack.append(b_10), lambda stack, i_12=i_12: stack.append(i_12), op_get, op_add], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_5(stack):
            x_9 = stack.pop()
            b_10 = stack.pop()
            W_11 = stack.pop()
            def binding_6(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    r_13 = stack.pop()
                    i_12 = stack.pop()
                    execute([lambda stack, r_13=r_13: stack.append(r_13), lambda stack, x_9=x_9: stack.append(x_9), binding_1, lambda stack, b_10=b_10: stack.append(b_10), lambda stack, i_12=i_12: stack.append(i_12), op_get, op_add], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, W_11=W_11: stack.append(W_11), binding_6], stack)
        binding_5.is_binding = True
        def binding_9(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_17 = stack.pop()
                i_16 = stack.pop()
                execute([lambda stack, v_17=v_17: stack.append(v_17), op_exp], stack)
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
                v_19 = stack.pop()
                a_18 = stack.pop()
                execute([lambda stack, a_18=a_18: stack.append(a_18), lambda stack, v_19=v_19: stack.append(v_19), op_add], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_12(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_23 = stack.pop()
                i_22 = stack.pop()
                execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_11(stack):
            s_20 = stack.pop()
            e_21 = stack.pop()
            def binding_12(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_23 = stack.pop()
                    i_22 = stack.pop()
                    execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, e_21=e_21: stack.append(e_21), binding_12], stack)
        binding_11.is_binding = True
        def binding_8(stack):
            z_15 = stack.pop()
            def binding_9(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_17 = stack.pop()
                    i_16 = stack.pop()
                    execute([lambda stack, v_17=v_17: stack.append(v_17), op_exp], stack)
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
                    v_19 = stack.pop()
                    a_18 = stack.pop()
                    execute([lambda stack, a_18=a_18: stack.append(a_18), lambda stack, v_19=v_19: stack.append(v_19), op_add], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_12(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_23 = stack.pop()
                    i_22 = stack.pop()
                    execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_11(stack):
                s_20 = stack.pop()
                e_21 = stack.pop()
                def binding_12(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_23 = stack.pop()
                        i_22 = stack.pop()
                        execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, e_21=e_21: stack.append(e_21), binding_12], stack)
            binding_11.is_binding = True
            execute([lambda stack, z_15=z_15: stack.append(z_15), binding_9, op_dup, binding_10, binding_11], stack)
        binding_8.is_binding = True
        def binding_15(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_28 = stack.pop()
                i_27 = stack.pop()
                execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_14(stack):
            y_25 = stack.pop()
            p_26 = stack.pop()
            def binding_15(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_28 = stack.pop()
                    i_27 = stack.pop()
                    execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, p_26=p_26: stack.append(p_26), binding_15], stack)
        binding_14.is_binding = True
        def binding_19(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                w_38 = stack.pop()
                j_37 = stack.pop()
                execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                q_36 = stack.pop()
                i_35 = stack.pop()
                execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_20(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_40 = stack.pop()
                i_39 = stack.pop()
                execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_17(stack):
            r_30 = stack.pop()
            g_31 = stack.pop()
            x_32 = stack.pop()
            b_33 = stack.pop()
            W_34 = stack.pop()
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q_36 = stack.pop()
                    i_35 = stack.pop()
                    execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_40 = stack.pop()
                    i_39 = stack.pop()
                    execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
        binding_17.is_binding = True
        def binding_25(stack):
            g_50 = stack.pop()
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
        binding_25.is_binding = True
        def binding_24(stack):
            y_46 = stack.pop()
            x_47 = stack.pop()
            b_48 = stack.pop()
            W_49 = stack.pop()
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
        binding_24.is_binding = True
        def binding_23(stack):
            execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                s_45 = stack.pop()
                A_44 = stack.pop()
                execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_22(stack):
            execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                e_43 = stack.pop()
                M_42 = stack.pop()
                execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                acc = stack.pop()
            stack.append(acc)
        def binding_26(stack):
            M_51 = stack.pop()
            execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
        binding_26.is_binding = True
        def binding_21(stack):
            step_41 = stack.pop()
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e_43 = stack.pop()
                    M_42 = stack.pop()
                    execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M_51 = stack.pop()
                execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
            binding_26.is_binding = True
            execute([[0, 0, 0], binding_22, binding_26], stack)
        binding_21.is_binding = True
        def binding_16(stack):
            grad_29 = stack.pop()
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q_36 = stack.pop()
                    i_35 = stack.pop()
                    execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_40 = stack.pop()
                    i_39 = stack.pop()
                    execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_17(stack):
                r_30 = stack.pop()
                g_31 = stack.pop()
                x_32 = stack.pop()
                b_33 = stack.pop()
                W_34 = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q_36 = stack.pop()
                        i_35 = stack.pop()
                        execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_40 = stack.pop()
                        i_39 = stack.pop()
                        execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
            binding_17.is_binding = True
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e_43 = stack.pop()
                    M_42 = stack.pop()
                    execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M_51 = stack.pop()
                execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
            binding_26.is_binding = True
            def binding_21(stack):
                step_41 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e_43 = stack.pop()
                        M_42 = stack.pop()
                        execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M_51 = stack.pop()
                    execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
                binding_26.is_binding = True
                execute([[0, 0, 0], binding_22, binding_26], stack)
            binding_21.is_binding = True
            execute([[binding_17], binding_21], stack)
        binding_16.is_binding = True
        def binding_13(stack):
            smax_24 = stack.pop()
            def binding_15(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_28 = stack.pop()
                    i_27 = stack.pop()
                    execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_14(stack):
                y_25 = stack.pop()
                p_26 = stack.pop()
                def binding_15(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_28 = stack.pop()
                        i_27 = stack.pop()
                        execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, p_26=p_26: stack.append(p_26), binding_15], stack)
            binding_14.is_binding = True
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q_36 = stack.pop()
                    i_35 = stack.pop()
                    execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_40 = stack.pop()
                    i_39 = stack.pop()
                    execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_17(stack):
                r_30 = stack.pop()
                g_31 = stack.pop()
                x_32 = stack.pop()
                b_33 = stack.pop()
                W_34 = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q_36 = stack.pop()
                        i_35 = stack.pop()
                        execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_40 = stack.pop()
                        i_39 = stack.pop()
                        execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
            binding_17.is_binding = True
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e_43 = stack.pop()
                    M_42 = stack.pop()
                    execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M_51 = stack.pop()
                execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
            binding_26.is_binding = True
            def binding_21(stack):
                step_41 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e_43 = stack.pop()
                        M_42 = stack.pop()
                        execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M_51 = stack.pop()
                    execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
                binding_26.is_binding = True
                execute([[0, 0, 0], binding_22, binding_26], stack)
            binding_21.is_binding = True
            def binding_16(stack):
                grad_29 = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q_36 = stack.pop()
                        i_35 = stack.pop()
                        execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_40 = stack.pop()
                        i_39 = stack.pop()
                        execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_17(stack):
                    r_30 = stack.pop()
                    g_31 = stack.pop()
                    x_32 = stack.pop()
                    b_33 = stack.pop()
                    W_34 = stack.pop()
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                                w_38 = stack.pop()
                                j_37 = stack.pop()
                                execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            q_36 = stack.pop()
                            i_35 = stack.pop()
                            execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_20(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v_40 = stack.pop()
                            i_39 = stack.pop()
                            execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
                binding_17.is_binding = True
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e_43 = stack.pop()
                        M_42 = stack.pop()
                        execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M_51 = stack.pop()
                    execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
                binding_26.is_binding = True
                def binding_21(stack):
                    step_41 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_22(stack):
                        execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        def binding_23(stack):
                            execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            def binding_24(stack):
                                y_46 = stack.pop()
                                x_47 = stack.pop()
                                b_48 = stack.pop()
                                W_49 = stack.pop()
                                def binding_25(stack):
                                    g_50 = stack.pop()
                                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                            binding_24.is_binding = True
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                s_45 = stack.pop()
                                A_44 = stack.pop()
                                execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            e_43 = stack.pop()
                            M_42 = stack.pop()
                            execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_26(stack):
                        M_51 = stack.pop()
                        execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
                    binding_26.is_binding = True
                    execute([[0, 0, 0], binding_22, binding_26], stack)
                binding_21.is_binding = True
                execute([[binding_17], binding_21], stack)
            binding_16.is_binding = True
            execute([[binding_14], binding_16], stack)
        binding_13.is_binding = True
        def binding_7(stack):
            fwd_14 = stack.pop()
            def binding_9(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_17 = stack.pop()
                    i_16 = stack.pop()
                    execute([lambda stack, v_17=v_17: stack.append(v_17), op_exp], stack)
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
                    v_19 = stack.pop()
                    a_18 = stack.pop()
                    execute([lambda stack, a_18=a_18: stack.append(a_18), lambda stack, v_19=v_19: stack.append(v_19), op_add], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_12(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_23 = stack.pop()
                    i_22 = stack.pop()
                    execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_11(stack):
                s_20 = stack.pop()
                e_21 = stack.pop()
                def binding_12(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_23 = stack.pop()
                        i_22 = stack.pop()
                        execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, e_21=e_21: stack.append(e_21), binding_12], stack)
            binding_11.is_binding = True
            def binding_8(stack):
                z_15 = stack.pop()
                def binding_9(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_17 = stack.pop()
                        i_16 = stack.pop()
                        execute([lambda stack, v_17=v_17: stack.append(v_17), op_exp], stack)
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
                        v_19 = stack.pop()
                        a_18 = stack.pop()
                        execute([lambda stack, a_18=a_18: stack.append(a_18), lambda stack, v_19=v_19: stack.append(v_19), op_add], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_12(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_23 = stack.pop()
                        i_22 = stack.pop()
                        execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_11(stack):
                    s_20 = stack.pop()
                    e_21 = stack.pop()
                    def binding_12(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v_23 = stack.pop()
                            i_22 = stack.pop()
                            execute([lambda stack, v_23=v_23: stack.append(v_23), lambda stack, s_20=s_20: stack.append(s_20), op_div], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    execute([lambda stack, e_21=e_21: stack.append(e_21), binding_12], stack)
                binding_11.is_binding = True
                execute([lambda stack, z_15=z_15: stack.append(z_15), binding_9, op_dup, binding_10, binding_11], stack)
            binding_8.is_binding = True
            def binding_15(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_28 = stack.pop()
                    i_27 = stack.pop()
                    execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_14(stack):
                y_25 = stack.pop()
                p_26 = stack.pop()
                def binding_15(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_28 = stack.pop()
                        i_27 = stack.pop()
                        execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, p_26=p_26: stack.append(p_26), binding_15], stack)
            binding_14.is_binding = True
            def binding_19(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    w_38 = stack.pop()
                    j_37 = stack.pop()
                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    q_36 = stack.pop()
                    i_35 = stack.pop()
                    execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_20(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_40 = stack.pop()
                    i_39 = stack.pop()
                    execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_17(stack):
                r_30 = stack.pop()
                g_31 = stack.pop()
                x_32 = stack.pop()
                b_33 = stack.pop()
                W_34 = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q_36 = stack.pop()
                        i_35 = stack.pop()
                        execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_40 = stack.pop()
                        i_39 = stack.pop()
                        execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
            binding_17.is_binding = True
            def binding_25(stack):
                g_50 = stack.pop()
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
            binding_25.is_binding = True
            def binding_24(stack):
                y_46 = stack.pop()
                x_47 = stack.pop()
                b_48 = stack.pop()
                W_49 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
            binding_24.is_binding = True
            def binding_23(stack):
                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    s_45 = stack.pop()
                    A_44 = stack.pop()
                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_22(stack):
                execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                init = stack.pop()
                target = stack.pop()
                acc = init
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                for idx, x in enumerate(target):
                    stack.append(acc)
                    stack.append(x)
                    e_43 = stack.pop()
                    M_42 = stack.pop()
                    execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                    acc = stack.pop()
                stack.append(acc)
            def binding_26(stack):
                M_51 = stack.pop()
                execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
            binding_26.is_binding = True
            def binding_21(stack):
                step_41 = stack.pop()
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e_43 = stack.pop()
                        M_42 = stack.pop()
                        execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M_51 = stack.pop()
                    execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
                binding_26.is_binding = True
                execute([[0, 0, 0], binding_22, binding_26], stack)
            binding_21.is_binding = True
            def binding_16(stack):
                grad_29 = stack.pop()
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q_36 = stack.pop()
                        i_35 = stack.pop()
                        execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_40 = stack.pop()
                        i_39 = stack.pop()
                        execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_17(stack):
                    r_30 = stack.pop()
                    g_31 = stack.pop()
                    x_32 = stack.pop()
                    b_33 = stack.pop()
                    W_34 = stack.pop()
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                                w_38 = stack.pop()
                                j_37 = stack.pop()
                                execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            q_36 = stack.pop()
                            i_35 = stack.pop()
                            execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_20(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v_40 = stack.pop()
                            i_39 = stack.pop()
                            execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
                binding_17.is_binding = True
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e_43 = stack.pop()
                        M_42 = stack.pop()
                        execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M_51 = stack.pop()
                    execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
                binding_26.is_binding = True
                def binding_21(stack):
                    step_41 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_22(stack):
                        execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        def binding_23(stack):
                            execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            def binding_24(stack):
                                y_46 = stack.pop()
                                x_47 = stack.pop()
                                b_48 = stack.pop()
                                W_49 = stack.pop()
                                def binding_25(stack):
                                    g_50 = stack.pop()
                                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                            binding_24.is_binding = True
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                s_45 = stack.pop()
                                A_44 = stack.pop()
                                execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            e_43 = stack.pop()
                            M_42 = stack.pop()
                            execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_26(stack):
                        M_51 = stack.pop()
                        execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
                    binding_26.is_binding = True
                    execute([[0, 0, 0], binding_22, binding_26], stack)
                binding_21.is_binding = True
                execute([[binding_17], binding_21], stack)
            binding_16.is_binding = True
            def binding_13(stack):
                smax_24 = stack.pop()
                def binding_15(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_28 = stack.pop()
                        i_27 = stack.pop()
                        execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_14(stack):
                    y_25 = stack.pop()
                    p_26 = stack.pop()
                    def binding_15(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v_28 = stack.pop()
                            i_27 = stack.pop()
                            execute([lambda stack, v_28=v_28: stack.append(v_28), lambda stack, y_25=y_25: stack.append(y_25), lambda stack, i_27=i_27: stack.append(i_27), op_get, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    execute([lambda stack, p_26=p_26: stack.append(p_26), binding_15], stack)
                binding_14.is_binding = True
                def binding_19(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        w_38 = stack.pop()
                        j_37 = stack.pop()
                        execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        q_36 = stack.pop()
                        i_35 = stack.pop()
                        execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_20(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        v_40 = stack.pop()
                        i_39 = stack.pop()
                        execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                        res.append(stack.pop())
                    stack.append(res)
                def binding_17(stack):
                    r_30 = stack.pop()
                    g_31 = stack.pop()
                    x_32 = stack.pop()
                    b_33 = stack.pop()
                    W_34 = stack.pop()
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                                w_38 = stack.pop()
                                j_37 = stack.pop()
                                execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            q_36 = stack.pop()
                            i_35 = stack.pop()
                            execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_20(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v_40 = stack.pop()
                            i_39 = stack.pop()
                            execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
                binding_17.is_binding = True
                def binding_25(stack):
                    g_50 = stack.pop()
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                binding_25.is_binding = True
                def binding_24(stack):
                    y_46 = stack.pop()
                    x_47 = stack.pop()
                    b_48 = stack.pop()
                    W_49 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                binding_24.is_binding = True
                def binding_23(stack):
                    execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        s_45 = stack.pop()
                        A_44 = stack.pop()
                        execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_22(stack):
                    execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                    init = stack.pop()
                    target = stack.pop()
                    acc = init
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    for idx, x in enumerate(target):
                        stack.append(acc)
                        stack.append(x)
                        e_43 = stack.pop()
                        M_42 = stack.pop()
                        execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                        acc = stack.pop()
                    stack.append(acc)
                def binding_26(stack):
                    M_51 = stack.pop()
                    execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
                binding_26.is_binding = True
                def binding_21(stack):
                    step_41 = stack.pop()
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_22(stack):
                        execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        def binding_23(stack):
                            execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            def binding_24(stack):
                                y_46 = stack.pop()
                                x_47 = stack.pop()
                                b_48 = stack.pop()
                                W_49 = stack.pop()
                                def binding_25(stack):
                                    g_50 = stack.pop()
                                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                            binding_24.is_binding = True
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                s_45 = stack.pop()
                                A_44 = stack.pop()
                                execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            e_43 = stack.pop()
                            M_42 = stack.pop()
                            execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_26(stack):
                        M_51 = stack.pop()
                        execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
                    binding_26.is_binding = True
                    execute([[0, 0, 0], binding_22, binding_26], stack)
                binding_21.is_binding = True
                def binding_16(stack):
                    grad_29 = stack.pop()
                    def binding_19(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            w_38 = stack.pop()
                            j_37 = stack.pop()
                            execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                                w_38 = stack.pop()
                                j_37 = stack.pop()
                                execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            q_36 = stack.pop()
                            i_35 = stack.pop()
                            execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_20(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v_40 = stack.pop()
                            i_39 = stack.pop()
                            execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_17(stack):
                        r_30 = stack.pop()
                        g_31 = stack.pop()
                        x_32 = stack.pop()
                        b_33 = stack.pop()
                        W_34 = stack.pop()
                        def binding_19(stack):
                            target = stack.pop()
                            res = []
                            for idx, x in enumerate(target):
                                stack.append(idx)
                                stack.append(x)
                                w_38 = stack.pop()
                                j_37 = stack.pop()
                                execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
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
                                    w_38 = stack.pop()
                                    j_37 = stack.pop()
                                    execute([lambda stack, w_38=w_38: stack.append(w_38), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_35=i_35: stack.append(i_35), op_get, op_mul, lambda stack, x_32=x_32: stack.append(x_32), lambda stack, j_37=j_37: stack.append(j_37), op_get, op_mul, op_sub], stack)
                                    res.append(stack.pop())
                                stack.append(res)
                            for idx, x in enumerate(target):
                                stack.append(idx)
                                stack.append(x)
                                q_36 = stack.pop()
                                i_35 = stack.pop()
                                execute([lambda stack, q_36=q_36: stack.append(q_36), binding_19], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        def binding_20(stack):
                            target = stack.pop()
                            res = []
                            for idx, x in enumerate(target):
                                stack.append(idx)
                                stack.append(x)
                                v_40 = stack.pop()
                                i_39 = stack.pop()
                                execute([lambda stack, v_40=v_40: stack.append(v_40), lambda stack, r_30=r_30: stack.append(r_30), lambda stack, g_31=g_31: stack.append(g_31), lambda stack, i_39=i_39: stack.append(i_39), op_get, op_mul, op_sub], stack)
                                res.append(stack.pop())
                            stack.append(res)
                        execute([lambda stack, W_34=W_34: stack.append(W_34), binding_18, lambda stack, b_33=b_33: stack.append(b_33), binding_20, [], op_cons, op_cons], stack)
                    binding_17.is_binding = True
                    def binding_25(stack):
                        g_50 = stack.pop()
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                    binding_25.is_binding = True
                    def binding_24(stack):
                        y_46 = stack.pop()
                        x_47 = stack.pop()
                        b_48 = stack.pop()
                        W_49 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                    binding_24.is_binding = True
                    def binding_23(stack):
                        execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            s_45 = stack.pop()
                            A_44 = stack.pop()
                            execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_22(stack):
                        execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                        init = stack.pop()
                        target = stack.pop()
                        acc = init
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        def binding_23(stack):
                            execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            def binding_24(stack):
                                y_46 = stack.pop()
                                x_47 = stack.pop()
                                b_48 = stack.pop()
                                W_49 = stack.pop()
                                def binding_25(stack):
                                    g_50 = stack.pop()
                                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                            binding_24.is_binding = True
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                s_45 = stack.pop()
                                A_44 = stack.pop()
                                execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        for idx, x in enumerate(target):
                            stack.append(acc)
                            stack.append(x)
                            e_43 = stack.pop()
                            M_42 = stack.pop()
                            execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                            acc = stack.pop()
                        stack.append(acc)
                    def binding_26(stack):
                        M_51 = stack.pop()
                        execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
                    binding_26.is_binding = True
                    def binding_21(stack):
                        step_41 = stack.pop()
                        def binding_25(stack):
                            g_50 = stack.pop()
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                        binding_25.is_binding = True
                        def binding_24(stack):
                            y_46 = stack.pop()
                            x_47 = stack.pop()
                            b_48 = stack.pop()
                            W_49 = stack.pop()
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                        binding_24.is_binding = True
                        def binding_23(stack):
                            execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            def binding_24(stack):
                                y_46 = stack.pop()
                                x_47 = stack.pop()
                                b_48 = stack.pop()
                                W_49 = stack.pop()
                                def binding_25(stack):
                                    g_50 = stack.pop()
                                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                            binding_24.is_binding = True
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                s_45 = stack.pop()
                                A_44 = stack.pop()
                                execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        def binding_22(stack):
                            execute([lambda stack, W0_1=W0_1: stack.append(W0_1), lambda stack, b0_1=b0_1: stack.append(b0_1), [], op_cons, op_cons], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_25(stack):
                                g_50 = stack.pop()
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                            binding_25.is_binding = True
                            def binding_24(stack):
                                y_46 = stack.pop()
                                x_47 = stack.pop()
                                b_48 = stack.pop()
                                W_49 = stack.pop()
                                def binding_25(stack):
                                    g_50 = stack.pop()
                                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                            binding_24.is_binding = True
                            def binding_23(stack):
                                execute([lambda stack, M_42=M_42: stack.append(M_42)], stack)
                                init = stack.pop()
                                target = stack.pop()
                                acc = init
                                def binding_25(stack):
                                    g_50 = stack.pop()
                                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                                binding_25.is_binding = True
                                def binding_24(stack):
                                    y_46 = stack.pop()
                                    x_47 = stack.pop()
                                    b_48 = stack.pop()
                                    W_49 = stack.pop()
                                    def binding_25(stack):
                                        g_50 = stack.pop()
                                        execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), lambda stack, g_50=g_50: stack.append(g_50), 0.01, binding_17], stack)
                                    binding_25.is_binding = True
                                    execute([lambda stack, W_49=W_49: stack.append(W_49), lambda stack, b_48=b_48: stack.append(b_48), lambda stack, x_47=x_47: stack.append(x_47), binding_5, binding_8, lambda stack, y_46=y_46: stack.append(y_46), binding_14, binding_25], stack)
                                binding_24.is_binding = True
                                for idx, x in enumerate(target):
                                    stack.append(acc)
                                    stack.append(x)
                                    s_45 = stack.pop()
                                    A_44 = stack.pop()
                                    execute([lambda stack, A_44=A_44: stack.append(A_44), 0, op_get, lambda stack, A_44=A_44: stack.append(A_44), 1, op_get, lambda stack, s_45=s_45: stack.append(s_45), 0, op_get, lambda stack, s_45=s_45: stack.append(s_45), 1, op_get, binding_24], stack)
                                    acc = stack.pop()
                                stack.append(acc)
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                e_43 = stack.pop()
                                M_42 = stack.pop()
                                execute([lambda stack, D_1=D_1: stack.append(D_1), binding_23], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        def binding_26(stack):
                            M_51 = stack.pop()
                            execute([lambda stack, M_51=M_51: stack.append(M_51), 0, op_get, lambda stack, M_51=M_51: stack.append(M_51), 1, op_get], stack)
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