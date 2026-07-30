#ifndef SCROOGE_RUNTIME_H
#define SCROOGE_RUNTIME_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    VAL_INT,
    VAL_FLOAT,
    VAL_BLOCK,
    VAL_PTR
} ScroogeType;

struct ScroogeValue;

typedef struct {
    struct ScroogeValue* elems;
    int len;
} ScroogeBlock;

typedef struct ScroogeValue {
    ScroogeType type;
    union {
        long long int_val;
        double float_val;
        ScroogeBlock block;
        int ptr_val; // heap block ID
    };
} ScroogeValue;

#define STACK_SIZE 4096
#define FRAME_SIZE 4096
#define HEAP_SIZE 1000000

extern ScroogeValue stack[STACK_SIZE];
extern int sp;

extern ScroogeValue frame_storage[FRAME_SIZE];
extern int fp;

typedef struct {
    ScroogeValue* data;
    int len;
} HeapBlock;

extern HeapBlock heap[HEAP_SIZE];
extern int next_heap_id;

// Runtime API
void init_runtime();
void push(ScroogeValue val);
ScroogeValue pop();

ScroogeValue make_int(long long v);
ScroogeValue make_float(double v);
ScroogeValue make_block(ScroogeValue* elems, int len);
ScroogeValue make_ptr(int id);

// Operations
ScroogeValue op_add(ScroogeValue a, ScroogeValue b);
ScroogeValue op_sub(ScroogeValue a, ScroogeValue b);
ScroogeValue op_mul(ScroogeValue a, ScroogeValue b);
ScroogeValue op_div(ScroogeValue a, ScroogeValue b);
ScroogeValue op_mod(ScroogeValue a, ScroogeValue b);

ScroogeValue op_eq(ScroogeValue a, ScroogeValue b);
ScroogeValue op_ne(ScroogeValue a, ScroogeValue b);
ScroogeValue op_gt(ScroogeValue a, ScroogeValue b);
ScroogeValue op_lt(ScroogeValue a, ScroogeValue b);

ScroogeValue op_and(ScroogeValue a, ScroogeValue b);
ScroogeValue op_or(ScroogeValue a, ScroogeValue b);
ScroogeValue op_not(ScroogeValue a);
ScroogeValue op_select(ScroogeValue vt, ScroogeValue vf, ScroogeValue flag);
int is_truthy(ScroogeValue a);

ScroogeValue op_bitand(ScroogeValue a, ScroogeValue b);
ScroogeValue op_bitor(ScroogeValue a, ScroogeValue b);
ScroogeValue op_bitxor(ScroogeValue a, ScroogeValue b);
ScroogeValue op_bitshl(ScroogeValue a, ScroogeValue b);
ScroogeValue op_bitshr(ScroogeValue a, ScroogeValue b);
ScroogeValue op_bitnot(ScroogeValue a);

ScroogeValue op_cons(ScroogeValue val, ScroogeValue block);
ScroogeValue op_pair(ScroogeValue val1, ScroogeValue val2);
ScroogeValue op_len(ScroogeValue block);
ScroogeValue op_get(ScroogeValue block, ScroogeValue idx);

void op_hnew(ScroogeValue size);
void op_hwrite(ScroogeValue ptr, ScroogeValue val, ScroogeValue offset);
ScroogeValue op_hread(ScroogeValue ptr, ScroogeValue offset);

void op_print_int(ScroogeValue val);
void op_print_char(ScroogeValue val);

typedef struct {
    int base_idx;
    int parent_idx;
    int size;
} ScroogeFrame;

#define MAX_FRAMES 1024
extern ScroogeFrame frames[MAX_FRAMES];
extern int frames_cnt;
extern int current_frame_idx;
extern int frame_storage_top;

void enter_frame(int size);
void leave_frame();
ScroogeValue load_var(int resolved_idx);
void store_var(int resolved_idx, ScroogeValue val);

void print_value(ScroogeValue val);
void print_stack();

#endif
