import sys
import os

# Adjust path to import scrooge_check and scrooge interpreter
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../check')))
import scrooge_check
import scrooge

# scoring metric
def compute_conformance_score(phase_results):
    score_map = {
        "reserved-word": 1,
        "parse": 2,
        "arity": 3,
        "types": 4
    }
    
    current_score = 0
    for phase in phase_results:
        if phase.ok:
            current_score = score_map[phase.name]
        else:
            print(f"      Failing phase '{phase.name}' with error(s):")
            for e in phase.errors:
                print(f"        - {e}")
            break
            
    return current_score

# Scrooge v1.37 Generations
v137_code_a = """
#lst_reverse ( list -- reversed_list )
  [fold| idx acc val _ | val acc cons from nil ]
end
"""

v137_code_b = """
#filter_pos_step ( acc val -- new_acc )
  -> [ acc val ] [ val 0 > ]
  cond [ val acc cons ] else [ acc ] ?
end

#lst_reverse ( list -- reversed_list )
  [fold| idx acc val _ | val acc cons from nil ]
end

#lst_filter_pos ( list -- filtered_list )
  [fold| idx acc val _ | acc val filter_pos_step from nil ]
  lst_reverse
end
"""

v137_code_c = """
#h_find_val_step ( ptr size val idx -- index )
  -> [ ptr size val idx ] [ ptr idx hread val = ]
  cond [ idx ] else [
    ptr size val idx 1 + h_find_val_rec
  ] ?
end

#h_find_val_rec ( ptr size val idx -- index )
  -> [ ptr size val idx ] [ idx size = ]
  cond [ -1 ] else [
    ptr size val idx h_find_val_step
  ] ?
end

#h_find_val ( ptr size val -- index )
  0 h_find_val_rec
end
"""

# Scrooge v1.38 Generations
v138_code_a = """
#lst_reverse ( list -- reversed_list )
  -> [ list ] [ list ]
  [fold| idx acc val _ | val acc cons from nil ]
end
"""

v138_code_b = """
#filter_pos_helper ( val acc -- new_acc )
  -> [ val acc ] [ val 0 > ]
  cond [ val acc cons ] else [ acc ] ?
end

#lst_reverse ( list -- reversed_list )
  -> [ list ] [ list ]
  [fold| idx acc val _ | val acc cons from nil ]
end

#lst_filter_pos ( list -- filtered_list )
  -> [ list ] [ list ]
  [fold| idx acc val _ | val acc filter_pos_helper from nil ]
  lst_reverse
end
"""

v138_code_c = """
#h_find_val_loop ( ptr size val idx -- index )
  -> [ ptr size val idx ] [ idx size = ]
  cond [ -1 ] else [ ptr size val idx h_find_val_check ] ?
end

#h_find_val_check ( ptr size val idx -- index )
  -> [ ptr size val idx ] [ ptr idx hread val = ]
  cond [ idx ] else [ ptr size val idx 1 + h_find_val_loop ] ?
end

#h_find_val ( ptr size val -- index )
  -> [ ptr size val ] [ ptr size val 0 h_find_val_loop ]
end
"""

# Test execution expressions
run_expr_a = "[ 1 2 3 ] lst_reverse"
run_expr_b = "[ -5 0 2 -1 3 0 10 ] lst_filter_pos"
# Task C test creates a heap pointer of size 5, writes [ 10 20 30 40 50 ], then searches for 30, and then for 100
run_expr_c = """
5 hnew -> [ p ] [
  10 p 0 hwrite
  20 p 1 hwrite
  30 p 2 hwrite
  40 p 3 hwrite
  50 p 4 hwrite
  p 5 30 h_find_val
  p 5 100 h_find_val
]
"""

def evaluate_suite(version, tasks):
    print(f"=== Evaluating Scrooge {version} ===")
    total = 0
    all_conforming = True
    for name, code in tasks.items():
        print(f"Evaluating {name}...")
        phases = scrooge_check.check_source(code)
        score = compute_conformance_score(phases)
        print(f"  Score for {name}: {score}/4")
        total += score
        if score < 4:
            all_conforming = False
            continue
            
        # Run test expression
        expr = run_expr_a if name == "Task A" else (run_expr_b if name == "Task B" else run_expr_c)
        try:
            res = scrooge.run(code + "\n" + expr)
            print(f"  Runtime result for {name}: {res}")
            # validation
            if name == "Task A":
                assert res[-1] == [3, 2, 1], f"Wrong result {res}"
            elif name == "Task B":
                assert res[-1] == [2, 3, 10], f"Wrong result {res}"
            elif name == "Task C":
                assert res[-2] == 2 and res[-1] == -1, f"Wrong results {res}"
            print("  Runtime validation: PASS")
        except Exception as e:
            print(f"  Runtime crash/fail for {name}: {e}")
            all_conforming = False
            
    print(f"Total Score: {total}/12 | All Conforming & Correct: {all_conforming}\n")
    return total, all_conforming

v137_tasks = {"Task A": v137_code_a, "Task B": v137_code_b, "Task C": v137_code_c}
v138_tasks = {"Task A": v138_code_a, "Task B": v138_code_b, "Task C": v138_code_c}

evaluate_suite("v1.37", v137_tasks)
evaluate_suite("v1.38", v138_tasks)
