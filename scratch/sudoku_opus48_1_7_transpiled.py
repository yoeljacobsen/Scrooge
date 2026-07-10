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
    def binding_2(stack):
        g_1 = stack.pop()
        def binding_3(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                c_3 = stack.pop()
                k_2 = stack.pop()
                execute([lambda stack, c_3=c_3: stack.append(c_3), 0, op_eq, [lambda stack, k_2=k_2: stack.append(k_2)], [-1], op_ifelse], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_4(stack):
            execute([-1], stack)
            init = stack.pop()
            target = stack.pop()
            acc = init
            for idx, x in enumerate(target):
                stack.append(acc)
                stack.append(x)
                e_5 = stack.pop()
                a_4 = stack.pop()
                execute([lambda stack, a_4=a_4: stack.append(a_4), -1, op_eq, lambda stack, e_5=e_5: stack.append(e_5), -1, op_ne, op_and, [lambda stack, e_5=e_5: stack.append(e_5)], [lambda stack, a_4=a_4: stack.append(a_4)], op_ifelse], stack)
                acc = stack.pop()
            stack.append(acc)
        execute([lambda stack, g_1=g_1: stack.append(g_1), binding_3, binding_4], stack)
    binding_2.is_binding = True
    binding_1 = binding_2
    def binding_5(stack):
        find_empty_6 = stack.pop()
        def binding_7(stack):
            v_7 = stack.pop()
            idx_8 = stack.pop()
            g_9 = stack.pop()
            def binding_8(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    c_11 = stack.pop()
                    k_10 = stack.pop()
                    execute([lambda stack, k_10=k_10: stack.append(k_10), lambda stack, idx_8=idx_8: stack.append(idx_8), op_eq, [lambda stack, v_7=v_7: stack.append(v_7)], [lambda stack, c_11=c_11: stack.append(c_11)], op_ifelse], stack)
                    res.append(stack.pop())
                stack.append(res)
            execute([lambda stack, g_9=g_9: stack.append(g_9), binding_8], stack)
        binding_7.is_binding = True
        binding_6 = binding_7
        def binding_9(stack):
            place_12 = stack.pop()
            def binding_11(stack):
                v_13 = stack.pop()
                idx_14 = stack.pop()
                g_15 = stack.pop()
                execute([lambda stack, g_15=g_15: stack.append(g_15), lambda stack, idx_14=idx_14: stack.append(idx_14), lambda stack, v_13=v_13: stack.append(v_13), op_valid], stack)
            binding_11.is_binding = True
            binding_10 = binding_11
            def binding_12(stack):
                ok_16 = stack.pop()
                def binding_13(stack):
                    steps_17 = stack.pop()
                    g_18 = stack.pop()
                    def binding_14(stack):
                        def binding_15(stack):
                            pos_19 = stack.pop()
                            def binding_16(stack):
                                execute([0, lambda stack, g_18=g_18: stack.append(g_18), lambda stack, steps_17=steps_17: stack.append(steps_17), [], op_cons, op_cons, op_cons], stack)
                                init = stack.pop()
                                target = stack.pop()
                                acc = init
                                def binding_17(stack):
                                    st_22 = stack.pop()
                                    def binding_18(stack):
                                        rs_23 = stack.pop()
                                        rg_24 = stack.pop()
                                        rf_25 = stack.pop()
                                        execute([lambda stack, rf_25=rf_25: stack.append(rf_25), 1, op_eq, [1, lambda stack, rg_24=rg_24: stack.append(rg_24), lambda stack, rs_23=rs_23: stack.append(rs_23), [], op_cons, op_cons, op_cons], [0, lambda stack, g_18=g_18: stack.append(g_18), lambda stack, rs_23=rs_23: stack.append(rs_23), [], op_cons, op_cons, op_cons], op_ifelse], stack)
                                    binding_18.is_binding = True
                                    execute([lambda stack, g_18=g_18: stack.append(g_18), lambda stack, pos_19=pos_19: stack.append(pos_19), lambda stack, v_21=v_21: stack.append(v_21), binding_10, [lambda stack, g_18=g_18: stack.append(g_18), lambda stack, pos_19=pos_19: stack.append(pos_19), lambda stack, v_21=v_21: stack.append(v_21), binding_6, lambda stack, st_22=st_22: stack.append(st_22), binding_14, binding_18], [0, lambda stack, g_18=g_18: stack.append(g_18), lambda stack, st_22=st_22: stack.append(st_22), [], op_cons, op_cons, op_cons], op_ifelse], stack)
                                binding_17.is_binding = True
                                for idx, x in enumerate(target):
                                    stack.append(acc)
                                    stack.append(x)
                                    v_21 = stack.pop()
                                    f_20 = stack.pop()
                                    execute([[lambda stack, f_20=f_20: stack.append(f_20), 0, op_get], 1, op_eq, [lambda stack, f_20=f_20: stack.append(f_20)], [[lambda stack, f_20=f_20: stack.append(f_20), 2, op_get], 1, op_add, binding_17], op_ifelse], stack)
                                    acc = stack.pop()
                                stack.append(acc)
                            def binding_19(stack):
                                res_26 = stack.pop()
                                execute([lambda stack, res_26=res_26: stack.append(res_26), 0, op_get, lambda stack, res_26=res_26: stack.append(res_26), 1, op_get, lambda stack, res_26=res_26: stack.append(res_26), 2, op_get], stack)
                            binding_19.is_binding = True
                            execute([lambda stack, pos_19=pos_19: stack.append(pos_19), -1, op_eq, [1, lambda stack, g_18=g_18: stack.append(g_18), lambda stack, steps_17=steps_17: stack.append(steps_17)], [[1, 2, 3, 4, 5, 6, 7, 8, 9], binding_16, binding_19], op_ifelse], stack)
                        binding_15.is_binding = True
                        execute([lambda stack, g_18=g_18: stack.append(g_18), binding_1, binding_15], stack)
                    def binding_20(stack):
                        solve_27 = stack.pop()
                        def binding_21(stack):
                            steps_28 = stack.pop()
                            grid_29 = stack.pop()
                            f_30 = stack.pop()
                            execute([lambda stack, grid_29=grid_29: stack.append(grid_29), lambda stack, steps_28=steps_28: stack.append(steps_28)], stack)
                        binding_21.is_binding = True
                        execute([[5, 3, 0, 0, 7, 0, 0, 0, 0, 6, 0, 0, 1, 9, 5, 0, 0, 0, 0, 9, 8, 0, 0, 0, 0, 6, 0, 8, 0, 0, 0, 6, 0, 0, 0, 3, 4, 0, 0, 8, 0, 3, 0, 0, 1, 7, 0, 0, 0, 2, 0, 0, 0, 6, 0, 6, 0, 0, 0, 0, 2, 8, 0, 0, 0, 0, 4, 1, 9, 0, 0, 5, 0, 0, 0, 0, 8, 0, 0, 7, 9], 0, binding_14, binding_21], stack)
                    binding_20.is_binding = True
                    execute([[binding_14], binding_20], stack)
                binding_13.is_binding = True
                execute([[binding_13]], stack)
            binding_12.is_binding = True
            execute([[binding_10], binding_12], stack)
        binding_9.is_binding = True
        execute([[binding_6], binding_9], stack)
    binding_5.is_binding = True

    execute([[binding_1], binding_5], stack)
    return stack