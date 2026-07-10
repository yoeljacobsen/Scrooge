import sys
from importlib.machinery import SourceFileLoader

sys.setrecursionlimit(200000)

# Load interpreter
interpreter = SourceFileLoader("interpreter", "programs/Scrooge_1.18_gemini35flash_interpreter.py").load_module()

# Load scheme interpreter code
with open("programs/scheme_interpreter.sg", "r") as f:
    code = f.read()

# Input tokens for: ((lambda (x y) (+ x y)) 3 4)
tokens = [-1, -1, -8, -1, -10, -11, -2, -1, -3, -10, -11, -2, -2, 3, 4, -2]
tokens_str = "[ " + " ".join(map(str, tokens)) + " ]"

code_with_run = f"{tokens_str}\n{code}\nrun_scheme\n"

print("Evaluating Scheme interpreter in Scrooge v1.23...")
try:
    final_stack = interpreter.run_scrooge(code_with_run)
    print("Execution Finished!")
    print("Final Stack:", final_stack)
except Exception as e:
    print("\n--- CRASH DIAGNOSTIC ---")
    print(f"Exception: {type(e).__name__}: {e}")
