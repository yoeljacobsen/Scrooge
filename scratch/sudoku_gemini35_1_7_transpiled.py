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
        target = stack.pop()
        res = []
        for idx, x in enumerate(target):
            stack.append(idx)
            stack.append(x)
            val_2 = stack.pop()
            idx_1 = stack.pop()
            execute([lambda stack, val_2=val_2: stack.append(val_2), 0, op_eq, [lambda stack, idx_1=idx_1: stack.append(idx_1)], [99], op_ifelse], stack)
            res.append(stack.pop())
        stack.append(res)
    def binding_3(stack):
        execute([99], stack)
        init = stack.pop()
        target = stack.pop()
        acc = init
        for idx, x in enumerate(target):
            stack.append(acc)
            stack.append(x)
            v_4 = stack.pop()
            acc_3 = stack.pop()
            execute([lambda stack, v_4=v_4: stack.append(v_4), lambda stack, acc_3=acc_3: stack.append(acc_3), op_lt, [lambda stack, v_4=v_4: stack.append(v_4)], [lambda stack, acc_3=acc_3: stack.append(acc_3)], op_ifelse], stack)
            acc = stack.pop()
        stack.append(acc)
    binding_1 = binding_2, binding_3
    def binding_4(stack):
        find_empty_5 = stack.pop()
        def binding_6(stack):
            v_6 = stack.pop()
            i_7 = stack.pop()
            g_8 = stack.pop()
            execute([lambda stack, g_8=g_8: stack.append(g_8), lambda stack, i_7=i_7: stack.append(i_7), lambda stack, v_6=v_6: stack.append(v_6), op_valid], stack)
        binding_6.is_binding = True
        binding_5 = binding_6
        def binding_7(stack):
            check_valid_9 = stack.pop()
            def binding_9(stack):
                v_10 = stack.pop()
                i_11 = stack.pop()
                g_12 = stack.pop()
                def binding_10(stack):
                    target = stack.pop()
                    res = []
                    for idx, x in enumerate(target):
                        stack.append(idx)
                        stack.append(x)
                        val_14 = stack.pop()
                        idx_13 = stack.pop()
                        execute([lambda stack, idx_13=idx_13: stack.append(idx_13), lambda stack, i_11=i_11: stack.append(i_11), op_eq, [lambda stack, v_10=v_10: stack.append(v_10)], [lambda stack, val_14=val_14: stack.append(val_14)], op_ifelse], stack)
                        res.append(stack.pop())
                    stack.append(res)
                execute([lambda stack, g_12=g_12: stack.append(g_12), binding_10], stack)
            binding_9.is_binding = True
            binding_8 = binding_9
            def binding_11(stack):
                update_grid_15 = stack.pop()
                def binding_13(stack):
                    steps_16 = stack.pop()
                    grid_17 = stack.pop()
                    def binding_14(stack):
                        empty_idx_18 = stack.pop()
                        def binding_15(stack):
                            execute([0, lambda stack, steps_16=steps_16: stack.append(steps_16), lambda stack, grid_17=grid_17: stack.append(grid_17), [], op_cons, op_cons, op_cons], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_16(stack):
                                flag_21 = stack.pop()
                                def binding_17(stack):
                                    s_22 = stack.pop()
                                    def binding_18(stack):
                                        g_23 = stack.pop()
                                        def binding_19(stack):
                                            s_next_24 = stack.pop()
                                            def binding_20(stack):
                                                r_f_25 = stack.pop()
                                                r_s_26 = stack.pop()
                                                r_g_27 = stack.pop()
                                                execute([lambda stack, r_f_25=r_f_25: stack.append(r_f_25), [1, lambda stack, r_s_26=r_s_26: stack.append(r_s_26), lambda stack, r_g_27=r_g_27: stack.append(r_g_27), [], op_cons, op_cons, op_cons], [0, lambda stack, r_s_26=r_s_26: stack.append(r_s_26), lambda stack, g_23=g_23: stack.append(g_23), [], op_cons, op_cons, op_cons], op_ifelse], stack)
                                            binding_20.is_binding = True
                                            execute([lambda stack, g_23=g_23: stack.append(g_23), lambda stack, empty_idx_18=empty_idx_18: stack.append(empty_idx_18), lambda stack, v_20=v_20: stack.append(v_20), binding_5, [lambda stack, g_23=g_23: stack.append(g_23), lambda stack, empty_idx_18=empty_idx_18: stack.append(empty_idx_18), lambda stack, v_20=v_20: stack.append(v_20), binding_8, lambda stack, s_next_24=s_next_24: stack.append(s_next_24), binding_12, binding_20], [0, lambda stack, s_next_24=s_next_24: stack.append(s_next_24), lambda stack, g_23=g_23: stack.append(g_23), [], op_cons, op_cons, op_cons], op_ifelse], stack)
                                        binding_19.is_binding = True
                                        execute([lambda stack, flag_21=flag_21: stack.append(flag_21), [lambda stack, acc_19=acc_19: stack.append(acc_19)], [lambda stack, s_22=s_22: stack.append(s_22), 1, op_add, binding_19], op_ifelse], stack)
                                    binding_18.is_binding = True
                                    execute([lambda stack, acc_19=acc_19: stack.append(acc_19), 2, op_get, binding_18], stack)
                                binding_17.is_binding = True
                                execute([lambda stack, acc_19=acc_19: stack.append(acc_19), 1, op_get, binding_17], stack)
                            binding_16.is_binding = True
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                v_20 = stack.pop()
                                acc_19 = stack.pop()
                                execute([lambda stack, acc_19=acc_19: stack.append(acc_19), 0, op_get, binding_16], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        def binding_21(stack):
                            final_acc_28 = stack.pop()
                            execute([lambda stack, final_acc_28=final_acc_28: stack.append(final_acc_28), 2, op_get, lambda stack, final_acc_28=final_acc_28: stack.append(final_acc_28), 1, op_get, lambda stack, final_acc_28=final_acc_28: stack.append(final_acc_28), 0, op_get], stack)
                        binding_21.is_binding = True
                        execute([lambda stack, empty_idx_18=empty_idx_18: stack.append(empty_idx_18), 99, op_eq, [lambda stack, grid_17=grid_17: stack.append(grid_17), lambda stack, steps_16=steps_16: stack.append(steps_16), 1], [[1, 2, 3, 4, 5, 6, 7, 8, 9], binding_15, binding_21], op_ifelse], stack)
                    binding_14.is_binding = True
                    execute([lambda stack, grid_17=grid_17: stack.append(grid_17), binding_1, op_apply, binding_14], stack)
                binding_13.is_binding = True
                binding_12 = binding_13
                def binding_22(stack):
                    solve_29 = stack.pop()
                    execute([0, binding_12], stack)
                binding_22.is_binding = True
                execute([[binding_12], binding_22], stack)
            binding_11.is_binding = True
            execute([[binding_8], binding_11], stack)
        binding_7.is_binding = True
        execute([[binding_5], binding_7], stack)
    binding_4.is_binding = True

    execute([[binding_1], binding_4], stack)
    return stack