# Transpiled Scrooge v1.18 Code
import math
import sys

# Runtime Helper Functions
def execute(blk, stack):
    if callable(blk):
        blk(stack)
    elif isinstance(blk, list):
        for item in blk:
            if callable(item):
                item(stack)
            else:
                stack.append(item)
    else:
        stack.append(blk)

def op_add(stack): b = stack.pop(); a = stack.pop(); stack.append(a + b)
def op_sub(stack): b = stack.pop(); a = stack.pop(); stack.append(a - b)
def op_mul(stack): b = stack.pop(); a = stack.pop(); stack.append(a * b)
def op_div(stack): b = stack.pop(); a = stack.pop(); stack.append(a // b if isinstance(a, int) and isinstance(b, int) else a / b)
def op_mod(stack): b = stack.pop(); a = stack.pop(); stack.append(a % b)
def op_eq(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a == b))
def op_ne(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a != b))
def op_gt(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a > b))
def op_lt(stack): b = stack.pop(); a = stack.pop(); stack.append(int(a < b))
def op_and(stack): b = stack.pop(); a = stack.pop(); stack.append(int(bool(a) and bool(b)))
def op_or(stack): b = stack.pop(); a = stack.pop(); stack.append(int(bool(a) or bool(b)))
def op_not(stack): a = stack.pop(); stack.append(int(not bool(a)))
def op_dup(stack): stack.append(stack[-1])
def op_drop(stack): stack.pop()
def op_swap(stack): stack[-1], stack[-2] = stack[-2], stack[-1]
def op_rot(stack): stack[-3], stack[-2], stack[-1] = stack[-2], stack[-1], stack[-3]
def op_over(stack): stack.append(stack[-2])
def op_roll(stack): n = stack.pop(); stack.append(stack.pop(-1 - n))
def op_pk(stack): offset = stack.pop(); stack.append(stack[-1 - offset])
def op_cons(stack): lst = stack.pop(); x = stack.pop(); stack.append([x] + lst)
def op_to(stack): stack.append('SENTINEL_TO')
def op_select(stack): flag = stack.pop(); val_false = stack.pop(); val_true = stack.pop(); stack.append(val_true if flag != 0 else val_false)
def op_ifelse(stack):
    false_blk = stack.pop()
    true_blk = stack.pop()
    cond = stack.pop()
    if cond != 0:
        execute(true_blk, stack)
    else:
        execute(false_blk, stack)
def op_get(stack):
    top = stack.pop()
    if len(stack) > 0 and stack[-1] == 'SENTINEL_TO':
        stack.pop()
        start = stack.pop()
        lst = stack.pop()
        stack.append(lst[start:top])
    else:
        lst = stack.pop()
        stack.append(lst[top])
def op_len(stack): stack.append(len(stack.pop()))
def op_exp(stack): stack.append(math.exp(stack.pop()))
def op_log(stack): stack.append(math.log(stack.pop()))
def op_pow(stack): b = stack.pop(); a = stack.pop(); stack.append(a ** b)
def op_sqrt(stack): stack.append(math.sqrt(stack.pop()))
def op_abs(stack): stack.append(abs(stack.pop()))
def op_max(stack): b = stack.pop(); a = stack.pop(); stack.append(max(a, b))
def op_min(stack): b = stack.pop(); a = stack.pop(); stack.append(min(a, b))
def op_fill(stack): v = stack.pop(); l = stack.pop(); stack.append([v] * l)
def op_seed(stack): pass
def op_rand(stack): import random; stack.append(random.random())
def op_bitand(stack): b = stack.pop(); a = stack.pop(); stack.append(a & b)
def op_bitor(stack): b = stack.pop(); a = stack.pop(); stack.append(a | b)
def op_bitxor(stack): b = stack.pop(); a = stack.pop(); stack.append(a ^ b)
def op_bitshl(stack): b = stack.pop(); a = stack.pop(); stack.append(a << b)
def op_bitshr(stack): b = stack.pop(); a = stack.pop(); stack.append(a >> b)
def op_bitnot(stack): a = stack.pop(); stack.append(~a)

def macro_row(stack):
    stack.append(9)
    execute(op_div, stack)
def macro_col(stack):
    stack.append(9)
    execute(op_mod, stack)
def macro_box(stack):
    execute(op_dup, stack)
    stack.append(9)
    execute(op_div, stack)
    stack.append(3)
    execute(op_div, stack)
    stack.append(3)
    execute(op_mul, stack)
    execute(op_swap, stack)
    stack.append(9)
    execute(op_mod, stack)
    stack.append(3)
    execute(op_div, stack)
    execute(op_add, stack)
def macro_is_valid(stack):
    def fold_4(stack):
        target = stack.pop()
        print('DEBUG FOLD target:', target, 'type:', type(target), 'stack:', stack)
        c_4 = stack.pop()
        stack.append(1)
        a_2 = stack.pop()
        for idx, val in enumerate(target):
            i_1 = idx
            v_3 = val
            stack.append(0)
            (lambda stack, a_2=a_2: stack.append(a_2))(stack)
            (lambda stack, v_3=v_3: stack.append(v_3))(stack)
            (lambda stack, c_4=c_4: stack.append(c_4))(stack)
            stack.append(1)
            execute(op_get, stack)
            execute(op_eq, stack)
            (lambda stack, i_1=i_1: stack.append(i_1))(stack)
            (lambda stack, c_4=c_4: stack.append(c_4))(stack)
            stack.append(0)
            execute(op_get, stack)
            execute(op_ne, stack)
            execute(op_and, stack)
            (lambda stack, i_1=i_1: stack.append(i_1))(stack)
            execute(macro_row, stack)
            (lambda stack, c_4=c_4: stack.append(c_4))(stack)
            stack.append(0)
            execute(op_get, stack)
            execute(macro_row, stack)
            execute(op_eq, stack)
            (lambda stack, i_1=i_1: stack.append(i_1))(stack)
            execute(macro_col, stack)
            (lambda stack, c_4=c_4: stack.append(c_4))(stack)
            stack.append(0)
            execute(op_get, stack)
            execute(macro_col, stack)
            execute(op_eq, stack)
            execute(op_or, stack)
            (lambda stack, i_1=i_1: stack.append(i_1))(stack)
            execute(macro_box, stack)
            (lambda stack, c_4=c_4: stack.append(c_4))(stack)
            stack.append(0)
            execute(op_get, stack)
            execute(macro_box, stack)
            execute(op_eq, stack)
            execute(op_or, stack)
            execute(op_and, stack)
            execute(op_select, stack)
            a_2 = stack.pop()
        stack.append(a_2)
    (lambda stack: stack.append([]))(stack)
    execute(op_cons, stack)
    execute(op_cons, stack)
    execute(op_swap, stack)
    execute(fold_4, stack)
def macro_find_empty(stack):
    def fold_8(stack):
        target = stack.pop()
        print('DEBUG FOLD target:', target, 'type:', type(target), 'stack:', stack)
        c_8 = stack.pop()
        stack.append(81)
        a_6 = stack.pop()
        for idx, val in enumerate(target):
            i_5 = idx
            v_7 = val
            (lambda stack, i_5=i_5: stack.append(i_5))(stack)
            stack.append(81)
            (lambda stack, v_7=v_7: stack.append(v_7))(stack)
            stack.append(0)
            execute(op_eq, stack)
            execute(op_select, stack)
            (lambda stack, a_6=a_6: stack.append(a_6))(stack)
            (lambda stack, a_6=a_6: stack.append(a_6))(stack)
            stack.append(81)
            execute(op_eq, stack)
            execute(op_select, stack)
            a_6 = stack.pop()
        stack.append(a_6)
    (lambda stack: stack.append(None))(stack)
    execute(op_swap, stack)
    execute(fold_8, stack)
def macro_set_cell(stack):
    def map_11(stack):
        target = stack.pop()
        c_11 = stack.pop()
        res = []
        for idx, val in enumerate(target):
            i_9 = idx
            v_10 = val
            (lambda stack, c_11=c_11: stack.append(c_11))(stack)
            stack.append(1)
            execute(op_get, stack)
            (lambda stack, v_10=v_10: stack.append(v_10))(stack)
            (lambda stack, i_9=i_9: stack.append(i_9))(stack)
            (lambda stack, c_11=c_11: stack.append(c_11))(stack)
            stack.append(0)
            execute(op_get, stack)
            execute(op_eq, stack)
            execute(op_select, stack)
            res.append(stack.pop())
        stack.append(res)
    (lambda stack: stack.append([]))(stack)
    execute(op_cons, stack)
    execute(op_cons, stack)
    execute(op_swap, stack)
    execute(map_11, stack)
def macro_solve(stack):
    execute(op_over, stack)
    execute(macro_find_empty, stack)
    execute(macro_solve_check, stack)
def macro_solve_check(stack):
    def binding_12(stack):
        execute(op_drop, stack)
        stack.append(1)
    def binding_13(stack):
        stack.append(1)
        execute(macro_try_digits, stack)
    (lambda stack: stack.append(stack[-1 - 0]))(stack)
    stack.append(81)
    execute(op_eq, stack)
    (lambda stack: stack.append(binding_12))(stack)
    (lambda stack: stack.append(binding_13))(stack)
    execute(op_ifelse, stack)
def macro_try_digits(stack):
    def binding_14(stack):
        execute(op_drop, stack)
        execute(op_drop, stack)
        stack.append(0)
    def binding_15(stack):
        def binding_20(stack):
            d_16 = stack.pop()
            i_17 = stack.pop()
            s_18 = stack.pop()
            b_19 = stack.pop()
            (lambda stack, b_19=b_19: stack.append(b_19))(stack)
            (lambda stack, s_18=s_18: stack.append(s_18))(stack)
            stack.append(1)
            execute(op_add, stack)
            (lambda stack, i_17=i_17: stack.append(i_17))(stack)
            (lambda stack, d_16=d_16: stack.append(d_16))(stack)
            (lambda stack, b_19=b_19: stack.append(b_19))(stack)
            (lambda stack, i_17=i_17: stack.append(i_17))(stack)
            (lambda stack, d_16=d_16: stack.append(d_16))(stack)
            execute(macro_is_valid, stack)
            execute(macro_try_digit_branch, stack)
        execute(binding_20, stack)
    (lambda stack: stack.append(stack[-1 - 0]))(stack)
    stack.append(9)
    execute(op_gt, stack)
    (lambda stack: stack.append(binding_14))(stack)
    (lambda stack: stack.append(binding_15))(stack)
    execute(op_ifelse, stack)
def macro_try_digit_branch(stack):
    def binding_21(stack):
        execute(macro_try_valid, stack)
    def binding_22(stack):
        execute(macro_try_invalid, stack)
    (lambda stack: stack.append(binding_21))(stack)
    (lambda stack: stack.append(binding_22))(stack)
    execute(op_ifelse, stack)
def macro_try_invalid(stack):
    stack.append(1)
    execute(op_add, stack)
    execute(macro_try_digits, stack)
def macro_try_valid(stack):
    def binding_27(stack):
        d_23 = stack.pop()
        i_24 = stack.pop()
        s_25 = stack.pop()
        b_26 = stack.pop()
        (lambda stack, b_26=b_26: stack.append(b_26))(stack)
        (lambda stack, i_24=i_24: stack.append(i_24))(stack)
        (lambda stack, d_23=d_23: stack.append(d_23))(stack)
        execute(macro_set_cell, stack)
        (lambda stack, s_25=s_25: stack.append(s_25))(stack)
        (lambda stack, b_26=b_26: stack.append(b_26))(stack)
        (lambda stack, s_25=s_25: stack.append(s_25))(stack)
        (lambda stack, i_24=i_24: stack.append(i_24))(stack)
        (lambda stack, d_23=d_23: stack.append(d_23))(stack)
        execute(macro_solve_helper, stack)
    execute(binding_27, stack)
def macro_solve_helper(stack):
    def binding_34(stack):
        d_28 = stack.pop()
        i_29 = stack.pop()
        s_o_30 = stack.pop()
        b_o_31 = stack.pop()
        s_32 = stack.pop()
        b_n_33 = stack.pop()
        (lambda stack, b_n_33=b_n_33: stack.append(b_n_33))(stack)
        (lambda stack, s_32=s_32: stack.append(s_32))(stack)
        execute(macro_solve, stack)
        (lambda stack, b_o_31=b_o_31: stack.append(b_o_31))(stack)
        (lambda stack, s_o_30=s_o_30: stack.append(s_o_30))(stack)
        (lambda stack, i_29=i_29: stack.append(i_29))(stack)
        (lambda stack, d_28=d_28: stack.append(d_28))(stack)
        execute(macro_handle_res, stack)
    execute(binding_34, stack)
def macro_handle_res(stack):
    def binding_44(stack):
        def binding_42(stack):
            (lambda stack, b_n_41=b_n_41: stack.append(b_n_41))(stack)
            (lambda stack, s_n_40=s_n_40: stack.append(s_n_40))(stack)
            stack.append(1)
        def binding_43(stack):
            (lambda stack, b_o_38=b_o_38: stack.append(b_o_38))(stack)
            (lambda stack, s_n_40=s_n_40: stack.append(s_n_40))(stack)
            (lambda stack, i_36=i_36: stack.append(i_36))(stack)
            (lambda stack, d_35=d_35: stack.append(d_35))(stack)
            stack.append(1)
            execute(op_add, stack)
            execute(macro_try_digits, stack)
        d_35 = stack.pop()
        i_36 = stack.pop()
        s_o_37 = stack.pop()
        b_o_38 = stack.pop()
        succ_39 = stack.pop()
        s_n_40 = stack.pop()
        b_n_41 = stack.pop()
        (lambda stack, succ_39=succ_39: stack.append(succ_39))(stack)
        (lambda stack: stack.append(binding_42))(stack)
        (lambda stack: stack.append(binding_43))(stack)
        execute(op_ifelse, stack)
    execute(binding_44, stack)

def run(initial_stack=None):
    if initial_stack is None:
        stack = []
    else:
        stack = list(initial_stack)
    execute(macro_solve, stack)
    return stack