import sys
import json
from importlib.machinery import SourceFileLoader

# Load interpreter using SourceFileLoader to bypass dot module name limits
interpreter = SourceFileLoader("interpreter", "programs/Scrooge_1.18_gemini35flash_interpreter.py").load_module()

# Load first problem
with open("problems.json", "r") as f:
    problems = json.load(f)

flat_grid = [c for r in problems[0]["GRID"] for c in r]

# Load raw sudoku_gemini35_1_18.sg
with open("programs/sudoku_gemini35_1_18.sg", "r") as f:
    code = f.read()

# To evaluate, we need to push inputs and run the solve macro
grid_str = "[" + " ".join(map(str, flat_grid)) + "]"
code_with_run = f"{grid_str} 0\n{code}\nsolve\n"

print("Evaluating using interpreter...")
try:
    final_stack = interpreter.run_scrooge(code_with_run)
    print("Execution Finished!")
    print("Final Stack:", final_stack)
except Exception as e:
    import traceback
    traceback.print_exc()
