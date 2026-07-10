import transpiler
import re

with open("programs/sudoku_gemini35_1_7.sg", "r") as f:
    code = f.read()

gemini_lines = code.split("\n")

# 1. Replace check_valid implementation (lines 3-19, 0-indexed 2-18) with a wrapper for native 'valid'
valid_replacement = [
    "[ -> [ g i v ]",
    "  g i v valid",
    "] -> [ check_valid ]"
]

print("Replacing check_valid implementation with native valid wrapper...")
gemini_lines[2:19] = valid_replacement

# Rebuild code_fixed for further replacements
code_fixed = "\n".join(gemini_lines)

# 2. Fix missing execute (comma ',') operator ONLY for find_empty call
code_fixed = code_fixed.replace("grid find_empty -> [ empty_idx ]", "grid find_empty , -> [ empty_idx ]")

# 3. Fix the backtracking bug in Gemini's solve function
# If the recursive solve fails (r_f is 0), we must return the original grid '^g' instead of the failed grid 'r_g'
code_fixed = code_fixed.replace(
    "r_f r_s r_g [ ] cons cons cons",
    "r_f [ 1 r_s r_g [ ] cons cons cons ] else [ 0 r_s ^g [ ] cons cons cons ] ?"
)

# Replace 'and' with '&' and 'or' with '|' (taking care to match them as whole words)
code_fixed = re.sub(r'\band\b', '&', code_fixed)
code_fixed = re.sub(r'\bor\b', '|', code_fixed)

with open("scratch/sudoku_gemini35_1_7_fixed.sg", "w") as f:
    f.write(code_fixed)

print("Corrections applied to Gemini code.")

try:
    py_source = transpiler.transpile(code_fixed)
    print("\nTranspilation: SUCCESS!")
    with open("scratch/sudoku_gemini35_1_7_transpiled.py", "w") as f_out:
        f_out.write(py_source)
    print("Saved transpiled python output to scratch/sudoku_gemini35_1_7_transpiled.py")
except Exception as e:
    print("\nTranspilation: FAILED")
    import traceback
    traceback.print_exc()

print("\n--- Running Gemini 3.5 Sudoku Solver ---")
import sys
sys.setrecursionlimit(5000)
# The initial grid to solve
grid = [
    5, 3, 0, 0, 7, 0, 0, 0, 0,
    6, 0, 0, 1, 9, 5, 0, 0, 0,
    0, 9, 8, 0, 0, 0, 0, 6, 0,
    8, 0, 0, 0, 6, 0, 0, 0, 3,
    4, 0, 0, 8, 0, 3, 0, 0, 1,
    7, 0, 0, 0, 2, 0, 0, 0, 6,
    0, 6, 0, 0, 0, 0, 2, 8, 0,
    0, 0, 0, 4, 1, 9, 0, 0, 5,
    0, 0, 0, 0, 8, 0, 0, 7, 9
]

try:
    final_stack = transpiler.run_scrooge(code_fixed, [grid])
    print("Execution: SUCCESS")
    print("Final Stack:")
    for idx, el in enumerate(final_stack):
        if isinstance(el, list) and len(el) == 81:
            print(f"  [{idx}]: Grid of length 81: {el}")
        else:
            print(f"  [{idx}]: {el}")
except Exception as e:
    print("Execution: FAILED")
    import traceback
    traceback.print_exc()
