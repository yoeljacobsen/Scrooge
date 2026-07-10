import sys
sys.path.insert(0, 'programs/interpreter_118_opus48')
import json
import scrooge

sys.setrecursionlimit(200000)

# Load first problem
with open("problems.json", "r") as f:
    problems = json.load(f)

flat_grid = [c for r in problems[0]["GRID"] for c in r]

# Load sudoku_opus48_1_18.sg
with open("programs/sudoku_opus48_1_18.sg", "r") as f:
    code = f.read()

# Add main execution block: push flat_grid, push 0 (steps), call solve
grid_str = "[ " + " ".join(map(str, flat_grid)) + " ]"
code_with_run = f"{grid_str} 0\n{code}\nsolve\n"

print("Evaluating using Opus 4.8 interpreter...")
try:
    final_stack = scrooge.run(code_with_run)
    print("Execution Finished!")
    print("Final Stack length:", len(final_stack))
    if len(final_stack) >= 3:
        print("Solved Grid:", final_stack[0])
        print("Steps:", final_stack[1])
        print("Success:", final_stack[2])
    else:
        print("Final Stack:", final_stack)
except Exception as e:
    import traceback
    traceback.print_exc()
