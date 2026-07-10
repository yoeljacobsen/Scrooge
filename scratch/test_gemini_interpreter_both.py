import sys
import json
from importlib.machinery import SourceFileLoader

sys.setrecursionlimit(200000)

# Load interpreter using SourceFileLoader to bypass dot module name limits
interpreter = SourceFileLoader("interpreter", "programs/Scrooge_1.18_gemini35flash_interpreter.py").load_module()

# Load first problem
with open("problems.json", "r") as f:
    problems = json.load(f)

flat_grid = [c for r in problems[0]["GRID"] for c in r]
grid_str = "[ " + " ".join(map(str, flat_grid)) + " ]"

def run_test(file_path):
    print(f"\n--- Testing {file_path} ---")
    with open(file_path, "r") as f:
        code = f.read()
    
    code_with_run = f"{grid_str} 0\n{code}\nsolve\n"
    try:
        final_stack = interpreter.run_scrooge(code_with_run)
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

run_test("programs/sudoku_gemini35_1_18.sg")
run_test("programs/sudoku_gemini35_1_18_fixed.sg")
