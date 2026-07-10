import transpiler
import traceback

print("--- Running Opus 4.8 Sudoku Solver ---")
with open("scratch/sudoku_opus48_1_7_fixed.sg", "r") as f:
    code = f.read()

try:
    final_stack = transpiler.run_scrooge(code, [])
    print("Execution: SUCCESS")
    print("Final Stack:")
    for idx, el in enumerate(final_stack):
        print(f"  [{idx}]: {el}")
except Exception as e:
    print("Execution: FAILED")
    traceback.print_exc()
