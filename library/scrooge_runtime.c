#include "scrooge_runtime.h"

ScroogeValue stack[STACK_SIZE];
int sp = 0;

ScroogeValue frame_storage[FRAME_SIZE];
int fp = 0;

HeapBlock heap[HEAP_SIZE];
int next_heap_id = 0;

void init_runtime() {
    sp = 0;
    fp = 0;
    next_heap_id = 0;
    frames_cnt = 0;
    current_frame_idx = -1;
    frame_storage_top = 0;
    memset(stack, 0, sizeof(stack));
    memset(frame_storage, 0, sizeof(frame_storage));
    memset(heap, 0, sizeof(heap));
}

void push(ScroogeValue val) {
    if (sp >= STACK_SIZE) {
        fprintf(stderr, "Fatal: Stack overflow\n");
        exit(1);
    }
    stack[sp++] = val;
}

ScroogeValue pop() {
    if (sp <= 0) {
        fprintf(stderr, "Fatal: Stack underflow\n");
        exit(1);
    }
    return stack[--sp];
}

ScroogeValue make_int(long long v) {
    ScroogeValue val;
    val.type = VAL_INT;
    val.int_val = v;
    return val;
}

ScroogeValue make_float(double v) {
    ScroogeValue val;
    val.type = VAL_FLOAT;
    val.float_val = v;
    return val;
}

ScroogeValue make_block(ScroogeValue* elems, int len) {
    ScroogeValue val;
    val.type = VAL_BLOCK;
    val.block.elems = elems;
    val.block.len = len;
    return val;
}

ScroogeValue make_ptr(int id) {
    ScroogeValue val;
    val.type = VAL_PTR;
    val.ptr_val = id;
    return val;
}

ScroogeValue op_add(ScroogeValue a, ScroogeValue b) {
    if (a.type == VAL_INT && b.type == VAL_INT) {
        return make_int(a.int_val + b.int_val);
    }
    double av = (a.type == VAL_FLOAT) ? a.float_val : (double)a.int_val;
    double bv = (b.type == VAL_FLOAT) ? b.float_val : (double)b.int_val;
    return make_float(av + bv);
}

ScroogeValue op_sub(ScroogeValue a, ScroogeValue b) {
    if (a.type == VAL_INT && b.type == VAL_INT) {
        return make_int(a.int_val - b.int_val);
    }
    double av = (a.type == VAL_FLOAT) ? a.float_val : (double)a.int_val;
    double bv = (b.type == VAL_FLOAT) ? b.float_val : (double)b.int_val;
    return make_float(av - bv);
}

ScroogeValue op_mul(ScroogeValue a, ScroogeValue b) {
    if (a.type == VAL_INT && b.type == VAL_INT) {
        return make_int(a.int_val * b.int_val);
    }
    double av = (a.type == VAL_FLOAT) ? a.float_val : (double)a.int_val;
    double bv = (b.type == VAL_FLOAT) ? b.float_val : (double)b.int_val;
    return make_float(av * bv);
}

ScroogeValue op_div(ScroogeValue a, ScroogeValue b) {
    if (a.type == VAL_INT && b.type == VAL_INT) {
        if (b.int_val == 0) {
            fprintf(stderr, "Fatal: Division by zero\n");
            exit(1);
        }
        return make_int(a.int_val / b.int_val);
    }
    double av = (a.type == VAL_FLOAT) ? a.float_val : (double)a.int_val;
    double bv = (b.type == VAL_FLOAT) ? b.float_val : (double)b.int_val;
    if (bv == 0.0) {
        fprintf(stderr, "Fatal: Division by zero\n");
        exit(1);
    }
    return make_float(av / bv);
}

ScroogeValue op_mod(ScroogeValue a, ScroogeValue b) {
    if (a.type != VAL_INT || b.type != VAL_INT) {
        fprintf(stderr, "Fatal: Modulo requires integers\n");
        exit(1);
    }
    if (b.int_val == 0) {
        fprintf(stderr, "Fatal: Modulo by zero\n");
        exit(1);
    }
    long long av = a.int_val;
    long long bv = b.int_val;
    long long r = av % bv;
    if ((r > 0 && bv < 0) || (r < 0 && bv > 0)) {
        r += bv;
    }
    return make_int(r);
}

int values_equal(ScroogeValue a, ScroogeValue b) {
    if (a.type != b.type) {
        if (a.type == VAL_INT && b.type == VAL_FLOAT) {
            return (double)a.int_val == b.float_val;
        }
        if (a.type == VAL_FLOAT && b.type == VAL_INT) {
            return a.float_val == (double)b.int_val;
        }
        return 0;
    }
    if (a.type == VAL_INT) return a.int_val == b.int_val;
    if (a.type == VAL_FLOAT) return a.float_val == b.float_val;
    if (a.type == VAL_PTR) return a.ptr_val == b.ptr_val;
    if (a.type == VAL_BLOCK) {
        if (a.block.len != b.block.len) return 0;
        for (int i = 0; i < a.block.len; i++) {
            if (!values_equal(a.block.elems[i], b.block.elems[i])) {
                return 0;
            }
        }
        return 1;
    }
    return 0;
}

ScroogeValue op_eq(ScroogeValue a, ScroogeValue b) {
    return make_int(values_equal(a, b) ? 1 : 0);
}

ScroogeValue op_ne(ScroogeValue a, ScroogeValue b) {
    return make_int(values_equal(a, b) ? 0 : 1);
}

ScroogeValue op_gt(ScroogeValue a, ScroogeValue b) {
    if (a.type == VAL_INT && b.type == VAL_INT) {
        return make_int(a.int_val > b.int_val ? 1 : 0);
    }
    double av = (a.type == VAL_FLOAT) ? a.float_val : (double)a.int_val;
    double bv = (b.type == VAL_FLOAT) ? b.float_val : (double)b.int_val;
    return make_int(av > bv ? 1 : 0);
}

ScroogeValue op_lt(ScroogeValue a, ScroogeValue b) {
    if (a.type == VAL_INT && b.type == VAL_INT) {
        return make_int(a.int_val < b.int_val ? 1 : 0);
    }
    double av = (a.type == VAL_FLOAT) ? a.float_val : (double)a.int_val;
    double bv = (b.type == VAL_FLOAT) ? b.float_val : (double)b.int_val;
    return make_int(av < bv ? 1 : 0);
}

int is_truthy(ScroogeValue a) {
    if (a.type == VAL_INT) return a.int_val != 0;
    if (a.type == VAL_FLOAT) return a.float_val != 0.0;
    return 1; // Blocks and pointers are truthy
}

ScroogeValue op_and(ScroogeValue a, ScroogeValue b) {
    return make_int((is_truthy(a) && is_truthy(b)) ? 1 : 0);
}

ScroogeValue op_or(ScroogeValue a, ScroogeValue b) {
    return make_int((is_truthy(a) || is_truthy(b)) ? 1 : 0);
}

ScroogeValue op_not(ScroogeValue a) {
    return make_int(!is_truthy(a) ? 1 : 0);
}

ScroogeValue op_bitand(ScroogeValue a, ScroogeValue b) {
    return make_int(a.int_val & b.int_val);
}

ScroogeValue op_bitor(ScroogeValue a, ScroogeValue b) {
    return make_int(a.int_val | b.int_val);
}

ScroogeValue op_bitxor(ScroogeValue a, ScroogeValue b) {
    return make_int(a.int_val ^ b.int_val);
}

ScroogeValue op_bitshl(ScroogeValue a, ScroogeValue b) {
    return make_int((a.int_val << b.int_val) & 0xFFFFFFFFFFFFFFFFULL);
}

ScroogeValue op_bitshr(ScroogeValue a, ScroogeValue b) {
    unsigned long long ua = (unsigned long long)a.int_val;
    return make_int(ua >> b.int_val);
}

ScroogeValue op_bitnot(ScroogeValue a) {
    return make_int(~a.int_val & 0xFFFFFFFFFFFFFFFFULL);
}

ScroogeValue op_select(ScroogeValue vt, ScroogeValue vf, ScroogeValue flag) {
    return is_truthy(flag) ? vt : vf;
}

ScroogeValue op_cons(ScroogeValue val, ScroogeValue block) {
    if (block.type != VAL_BLOCK) {
        fprintf(stderr, "Fatal: cons second operand must be a block/list\n");
        exit(1);
    }
    int new_len = block.block.len + 1;
    ScroogeValue* new_elems = malloc(new_len * sizeof(ScroogeValue));
    new_elems[0] = val;
    for (int i = 0; i < block.block.len; i++) {
        new_elems[i + 1] = block.block.elems[i];
    }
    return make_block(new_elems, new_len);
}

ScroogeValue op_pair(ScroogeValue val1, ScroogeValue val2) {
    ScroogeValue* new_elems = malloc(2 * sizeof(ScroogeValue));
    new_elems[0] = val1;
    new_elems[1] = val2;
    return make_block(new_elems, 2);
}

ScroogeValue op_len(ScroogeValue block) {
    if (block.type != VAL_BLOCK) {
        fprintf(stderr, "Fatal: len operand must be a block/list\n");
        exit(1);
    }
    return make_int(block.block.len);
}

ScroogeValue op_get(ScroogeValue block, ScroogeValue idx) {
    if (block.type != VAL_BLOCK) {
        fprintf(stderr, "Fatal: get (:) operand must be a block/list\n");
        exit(1);
    }
    if (idx.type != VAL_INT) {
        fprintf(stderr, "Fatal: get (:) index must be an integer\n");
        exit(1);
    }
    long long index = idx.int_val;
    if (index < 0 || index >= block.block.len) {
        fprintf(stderr, "Fatal: get (:) index out of range\n");
        exit(1);
    }
    return block.block.elems[index];
}

void op_hnew(ScroogeValue size) {
    if (size.type != VAL_INT) {
        fprintf(stderr, "Fatal: hnew size must be an integer\n");
        exit(1);
    }
    int sz = (int)size.int_val;
    if (sz < 0) {
        fprintf(stderr, "Fatal: hnew size cannot be negative\n");
        exit(1);
    }
    if (next_heap_id >= HEAP_SIZE) {
        fprintf(stderr, "Fatal: Heap overflow (max %d allocations)\n", HEAP_SIZE);
        exit(1);
    }
    heap[next_heap_id].elems = (ScroogeValue*)calloc(sz, sizeof(ScroogeValue));
    heap[next_heap_id].len = sz;
    for(int i=0; i<sz; i++) heap[next_heap_id].elems[i] = make_int(0);
    push(make_ptr(next_heap_id));
    next_heap_id++;
}

void op_hwrite(ScroogeValue ptr, ScroogeValue val, ScroogeValue offset) {
    if (ptr.type != VAL_PTR) {
        fprintf(stderr, "Fatal: hwrite address must be a pointer\n");
        exit(1);
    }
    if (offset.type != VAL_INT) {
        fprintf(stderr, "Fatal: hwrite offset must be an integer\n");
        exit(1);
    }
    int id = ptr.ptr_val;
    int off = (int)offset.int_val;
    if (id < 0 || id >= next_heap_id) {
        fprintf(stderr, "Fatal: hwrite invalid pointer\n");
        exit(1);
    }
    if (off < 0 || off >= heap[id].len) {
        fprintf(stderr, "Fatal: hwrite offset out of range\n");
        exit(1);
    }
    heap[id].data[off] = val;
}

ScroogeValue op_hread(ScroogeValue ptr, ScroogeValue offset) {
    if (ptr.type != VAL_PTR) {
        fprintf(stderr, "Fatal: hread address must be a pointer\n");
        exit(1);
    }
    if (offset.type != VAL_INT) {
        fprintf(stderr, "Fatal: hread offset must be an integer\n");
        exit(1);
    }
    int id = ptr.ptr_val;
    int off = (int)offset.int_val;
    if (id < 0 || id >= next_heap_id) {
        fprintf(stderr, "Fatal: hread invalid pointer\n");
        exit(1);
    }
    if (off < 0 || off >= heap[id].len) {
        fprintf(stderr, "Fatal: hread offset out of range\n");
        exit(1);
    }
    return heap[id].data[off];
}

void op_print_int(ScroogeValue val) {
    if (val.type == VAL_INT) {
        printf("%lld", val.int_val);
    } else if (val.type == VAL_FLOAT) {
        printf("%f", val.float_val);
    } else {
        fprintf(stderr, "Fatal: print_int requires scalar value\n");
        exit(1);
    }
}

void op_print_char(ScroogeValue val) {
    if (val.type != VAL_INT) {
        fprintf(stderr, "Fatal: print_char requires integer value\n");
        exit(1);
    }
    printf("%c", (char)val.int_val);
    fflush(stdout);
}

ScroogeFrame frames[MAX_FRAMES];
int frames_cnt = 0;
int current_frame_idx = -1;
int frame_storage_top = 0;

void enter_frame(int size) {
    if (frames_cnt >= MAX_FRAMES) {
        fprintf(stderr, "Fatal: Max frames exceeded\n");
        exit(1);
    }
    if (frame_storage_top + size >= FRAME_SIZE) {
        fprintf(stderr, "Fatal: Frame storage overflow\n");
        exit(1);
    }
    int new_frame_idx = frames_cnt++;
    frames[new_frame_idx].base_idx = frame_storage_top;
    frames[new_frame_idx].parent_idx = current_frame_idx;
    frames[new_frame_idx].size = size;
    
    current_frame_idx = new_frame_idx;
    frame_storage_top += size;
}

void leave_frame() {
    if (current_frame_idx < 0) {
        fprintf(stderr, "Fatal: No active frame to leave\n");
        exit(1);
    }
    int size = frames[current_frame_idx].size;
    frame_storage_top -= size;
    current_frame_idx = frames[current_frame_idx].parent_idx;
    frames_cnt--;
}

ScroogeValue load_var(int resolved_idx) {
    int depth = resolved_idx >> 4;
    int local_idx = resolved_idx & 0x0F;
    int f_idx = current_frame_idx;
    for (int i = 0; i < depth; i++) {
        if (f_idx < 0) {
            fprintf(stderr, "Fatal: Lexical depth out of bounds on load\n");
            exit(1);
        }
        f_idx = frames[f_idx].parent_idx;
    }
    if (f_idx < 0) {
        fprintf(stderr, "Fatal: Invalid frame on load\n");
        exit(1);
    }
    if (local_idx < 0 || local_idx >= frames[f_idx].size) {
        fprintf(stderr, "Fatal: Local index out of bounds on load\n");
        exit(1);
    }
    return frame_storage[frames[f_idx].base_idx + local_idx];
}

void store_var(int resolved_idx, ScroogeValue val) {
    int depth = resolved_idx >> 4;
    int local_idx = resolved_idx & 0x0F;
    int f_idx = current_frame_idx;
    for (int i = 0; i < depth; i++) {
        if (f_idx < 0) {
            fprintf(stderr, "Fatal: Lexical depth out of bounds on store\n");
            exit(1);
        }
        f_idx = frames[f_idx].parent_idx;
    }
    if (f_idx < 0) {
        fprintf(stderr, "Fatal: Invalid frame on store\n");
        exit(1);
    }
    if (local_idx < 0 || local_idx >= frames[f_idx].size) {
        fprintf(stderr, "Fatal: Local index out of bounds on store\n");
        exit(1);
    }
    frame_storage[frames[f_idx].base_idx + local_idx] = val;
}

void print_value(ScroogeValue val) {
    if (val.type == VAL_INT) {
        printf("%lld", val.int_val);
    } else if (val.type == VAL_FLOAT) {
        printf("%f", val.float_val);
    } else if (val.type == VAL_PTR) {
        printf("('__ptr__', [");
        int id = val.ptr_val;
        for (int i = 0; i < heap[id].len; i++) {
            print_value(heap[id].data[i]);
            if (i < heap[id].len - 1) {
                printf(", ");
            }
        }
        printf("])");
    } else if (val.type == VAL_BLOCK) {
        printf("[");
        for (int i = 0; i < val.block.len; i++) {
            print_value(val.block.elems[i]);
            if (i < val.block.len - 1) {
                printf(", ");
            }
        }
        printf("]");
    }
}

void print_stack() {
    printf("STACK: [");
    for (int i = 0; i < sp; i++) {
        print_value(stack[i]);
        if (i < sp - 1) {
            printf(", ");
        }
    }
    printf("]\n");
}
