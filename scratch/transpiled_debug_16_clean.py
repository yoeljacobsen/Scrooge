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
    mnist_labels_1 = stack.pop()
    mnist_images_1 = stack.pop()
    def binding_1(stack):
        LR_2 = stack.pop()
        def binding_2(stack):
            target = stack.pop()
            res = []
            for idx, x in enumerate(target):
                stack.append(idx)
                stack.append(x)
                v_4 = stack.pop()
                j_3 = stack.pop()
                execute([0.0], stack)
                res.append(stack.pop())
            stack.append(res)
        def binding_3(stack):
            Z_5 = stack.pop()
            def binding_4(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_7 = stack.pop()
                    k_6 = stack.pop()
                    execute([0.0], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_5(stack):
                target = stack.pop()
                res = []
                for idx, x in enumerate(target):
                    stack.append(idx)
                    stack.append(x)
                    v_9 = stack.pop()
                    k_8 = stack.pop()
                    execute([lambda stack, Z_5=Z_5: stack.append(Z_5)], stack)
                    res.append(stack.pop())
                stack.append(res)
            def binding_6(stack):
                W0_10 = stack.pop()
                B0_11 = stack.pop()
                def binding_7(stack):
                    M0_12 = stack.pop()
                    def binding_8(stack):
                        target = stack.pop()
                        res = []
                        for idx, x in enumerate(target):
                            stack.append(idx)
                            stack.append(x)
                            v_14 = stack.pop()
                            n_13 = stack.pop()
                            execute([lambda stack, n_13=n_13: stack.append(n_13)], stack)
                            res.append(stack.pop())
                        stack.append(res)
                    def binding_9(stack):
                        IDX_15 = stack.pop()
                        def binding_10(stack):
                            execute([lambda stack, M0_12=M0_12: stack.append(M0_12)], stack)
                            init = stack.pop()
                            target = stack.pop()
                            acc = init
                            def binding_11(stack):
                                execute([lambda stack, model_16=model_16: stack.append(model_16)], stack)
                                init = stack.pop()
                                target = stack.pop()
                                acc = init
                                def binding_12(stack):
                                    B_20 = stack.pop()
                                    W_21 = stack.pop()
                                    Y_22 = stack.pop()
                                    X_23 = stack.pop()
                                    def binding_13(stack):
                                        target = stack.pop()
                                        res = []
                                        def binding_14(stack):
                                            target = stack.pop()
                                            res = []
                                            for idx, x in enumerate(target):
                                                stack.append(idx)
                                                stack.append(x)
                                                wj_27 = stack.pop()
                                                j_26 = stack.pop()
                                                execute([lambda stack, X_23=X_23: stack.append(X_23), lambda stack, j_26=j_26: stack.append(j_26), op_get, lambda stack, wj_27=wj_27: stack.append(wj_27), op_mul], stack)
                                                res.append(stack.pop())
                                            stack.append(res)
                                        def binding_15(stack):
                                            execute([0.0], stack)
                                            init = stack.pop()
                                            target = stack.pop()
                                            acc = init
                                            for idx, x in enumerate(target):
                                                stack.append(acc)
                                                stack.append(x)
                                                p_29 = stack.pop()
                                                a_28 = stack.pop()
                                                execute([lambda stack, a_28=a_28: stack.append(a_28), lambda stack, p_29=p_29: stack.append(p_29), op_add], stack)
                                                acc = stack.pop()
                                            stack.append(acc)
                                        for idx, x in enumerate(target):
                                            stack.append(idx)
                                            stack.append(x)
                                            w_25 = stack.pop()
                                            i_24 = stack.pop()
                                            execute([lambda stack, w_25=w_25: stack.append(w_25), binding_14, binding_15, lambda stack, B_20=B_20: stack.append(B_20), lambda stack, i_24=i_24: stack.append(i_24), op_get, op_add, op_exp], stack)
                                            res.append(stack.pop())
                                        stack.append(res)
                                    def binding_16(stack):
                                        E_30 = stack.pop()
                                        def binding_17(stack):
                                            execute([0.0], stack)
                                            init = stack.pop()
                                            target = stack.pop()
                                            acc = init
                                            for idx, x in enumerate(target):
                                                stack.append(acc)
                                                stack.append(x)
                                                q_32 = stack.pop()
                                                a_31 = stack.pop()
                                                execute([lambda stack, a_31=a_31: stack.append(a_31), lambda stack, q_32=q_32: stack.append(q_32), op_add], stack)
                                                acc = stack.pop()
                                            stack.append(acc)
                                        def binding_18(stack):
                                            S_33 = stack.pop()
                                            def binding_19(stack):
                                                target = stack.pop()
                                                res = []
                                                for idx, x in enumerate(target):
                                                    stack.append(idx)
                                                    stack.append(x)
                                                    q_35 = stack.pop()
                                                    k_34 = stack.pop()
                                                    execute([lambda stack, q_35=q_35: stack.append(q_35), lambda stack, S_33=S_33: stack.append(S_33), op_div], stack)
                                                    res.append(stack.pop())
                                                stack.append(res)
                                            def binding_20(stack):
                                                target = stack.pop()
                                                res = []
                                                for idx, x in enumerate(target):
                                                    stack.append(idx)
                                                    stack.append(x)
                                                    pk_37 = stack.pop()
                                                    k_36 = stack.pop()
                                                    execute([lambda stack, pk_37=pk_37: stack.append(pk_37), lambda stack, Y_22=Y_22: stack.append(Y_22), lambda stack, k_36=k_36: stack.append(k_36), op_get, op_sub], stack)
                                                    res.append(stack.pop())
                                                stack.append(res)
                                            def binding_21(stack):
                                                G_38 = stack.pop()
                                                def binding_22(stack):
                                                    target = stack.pop()
                                                    res = []
                                                    def binding_23(stack):
                                                        gi_41 = stack.pop()
                                                        def binding_24(stack):
                                                            target = stack.pop()
                                                            res = []
                                                            for idx, x in enumerate(target):
                                                                stack.append(idx)
                                                                stack.append(x)
                                                                wj_43 = stack.pop()
                                                                j_42 = stack.pop()
                                                                execute([lambda stack, wj_43=wj_43: stack.append(wj_43), lambda stack, gi_41=gi_41: stack.append(gi_41), lambda stack, X_23=X_23: stack.append(X_23), lambda stack, j_42=j_42: stack.append(j_42), op_get, op_mul, lambda stack, LR_2=LR_2: stack.append(LR_2), op_mul, op_sub], stack)
                                                                res.append(stack.pop())
                                                            stack.append(res)
                                                        execute([lambda stack, w_40=w_40: stack.append(w_40), binding_24], stack)
                                                    binding_23.is_binding = True
                                                    for idx, x in enumerate(target):
                                                        stack.append(idx)
                                                        stack.append(x)
                                                        w_40 = stack.pop()
                                                        i_39 = stack.pop()
                                                        execute([lambda stack, G_38=G_38: stack.append(G_38), lambda stack, i_39=i_39: stack.append(i_39), op_get, binding_23], stack)
                                                        res.append(stack.pop())
                                                    stack.append(res)
                                                def binding_25(stack):
                                                    target = stack.pop()
                                                    res = []
                                                    for idx, x in enumerate(target):
                                                        stack.append(idx)
                                                        stack.append(x)
                                                        bk_45 = stack.pop()
                                                        k_44 = stack.pop()
                                                        execute([lambda stack, bk_45=bk_45: stack.append(bk_45), lambda stack, G_38=G_38: stack.append(G_38), lambda stack, k_44=k_44: stack.append(k_44), op_get, lambda stack, LR_2=LR_2: stack.append(LR_2), op_mul, op_sub], stack)
                                                        res.append(stack.pop())
                                                    stack.append(res)
                                                execute([lambda stack, W_21=W_21: stack.append(W_21), binding_22, lambda stack, B_20=B_20: stack.append(B_20), binding_25, [], op_cons, op_cons], stack)
                                            binding_21.is_binding = True
                                            execute([lambda stack, E_30=E_30: stack.append(E_30), binding_19, binding_20, binding_21], stack)
                                        binding_18.is_binding = True
                                        execute([lambda stack, E_30=E_30: stack.append(E_30), binding_17, binding_18], stack)
                                    binding_16.is_binding = True
                                    execute([lambda stack, W_21=W_21: stack.append(W_21), binding_13, binding_16], stack)
                                binding_12.is_binding = True
                                for idx, x in enumerate(target):
                                    stack.append(acc)
                                    stack.append(x)
                                    n_19 = stack.pop()
                                    st_18 = stack.pop()
                                    execute([lambda stack, mnist_images_1=mnist_images_1: stack.append(mnist_images_1), lambda stack, n_19=n_19: stack.append(n_19), op_get, lambda stack, mnist_labels_1=mnist_labels_1: stack.append(mnist_labels_1), lambda stack, n_19=n_19: stack.append(n_19), op_get, lambda stack, st_18=st_18: stack.append(st_18), 0, op_get, lambda stack, st_18=st_18: stack.append(st_18), 1, op_get, binding_12], stack)
                                    acc = stack.pop()
                                stack.append(acc)
                            for idx, x in enumerate(target):
                                stack.append(acc)
                                stack.append(x)
                                e_17 = stack.pop()
                                model_16 = stack.pop()
                                execute([lambda stack, IDX_15=IDX_15: stack.append(IDX_15), binding_11], stack)
                                acc = stack.pop()
                            stack.append(acc)
                        execute([[0, 1, 2, 3, 4], binding_10], stack)
                    binding_9.is_binding = True
                    execute([lambda stack, mnist_images_1=mnist_images_1: stack.append(mnist_images_1), binding_8, binding_9], stack)
                binding_7.is_binding = True
                execute([lambda stack, W0_10=W0_10: stack.append(W0_10), lambda stack, B0_11=B0_11: stack.append(B0_11), [], op_cons, op_cons, binding_7], stack)
            binding_6.is_binding = True
            execute([lambda stack, mnist_labels_1=mnist_labels_1: stack.append(mnist_labels_1), 0, op_get, binding_4, lambda stack, mnist_labels_1=mnist_labels_1: stack.append(mnist_labels_1), 0, op_get, binding_5, binding_6], stack)
        binding_3.is_binding = True
        execute([lambda stack, mnist_images_1=mnist_images_1: stack.append(mnist_images_1), 0, op_get, binding_2, binding_3], stack)
    binding_1.is_binding = True

    execute([0.05, binding_1], stack)
    return stack