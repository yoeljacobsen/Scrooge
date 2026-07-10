import sys
sys.path.insert(0, 'scratch')
import json
import time
import transpiler_1_18

# Load problems
with open("problems.json", "r") as f:
    problems = json.load(f)

# We will run the v1.18 solver on the first 5 easy puzzles
num_puzzles = 5

sys.setrecursionlimit(200000)

with open("programs/sudoku_gemini35_1_18_fixed.sg", "r") as f:
    code = f.read()

# Add main execution block to call the solve macro
code_with_solve = code + "\n\nsolve\n"

print("--- Compiling Scrooge v1.18 Solver ---")
try:
    py_code = transpiler_1_18.transpile(code_with_solve)
    print("Compilation successful.\n")
except Exception as e:
    print(f"Compilation failed: {e}")
    sys.exit(1)

results = []

for i in range(num_puzzles):
    prob = problems[i]
    name = prob["NAME"]
    grid_2d = prob["GRID"]
    flat_grid = [cell for row in grid_2d for cell in row]
    
    print(f"Running puzzle: {name}...")
    
    t0 = time.time()
    try:
        final_stack = transpiler_1_18.run_scrooge(code_with_solve, [flat_grid, 0])
        time_ms = (time.time() - t0) * 1000
        
        # final_stack layout: [solved_grid, steps, success]
        if len(final_stack) >= 3:
            solved_grid = final_stack[0]
            steps = final_stack[1]
            success = final_stack[2]
            solved = int(0 not in solved_grid) and (success == 1)
            status = "PASS" if solved else "FAIL"
        else:
            steps = -1
            status = f"FAIL (Unexpected stack: {final_stack})"
    except Exception as e:
        import traceback
        traceback.print_exc()
        time_ms = -1
        steps = -1
        status = f"ERROR: {str(e)}"
        
    print(f"  Result: {status} in {steps} steps ({time_ms:.2f} ms)")
    
    results.append({
        "name": name,
        "status": status,
        "steps": steps,
        "time_ms": time_ms
    })

print("\n--- Summary Table (Scrooge v1.18) ---")
print("| Puzzle | Status | Steps | Time |")
print("|---|---|---|---|")
for r in results:
    time_str = f"{r['time_ms']:.2f} ms" if r['time_ms'] >= 0 else "N/A"
    print(f"| {r['name']} | {r['status']} | {r['steps']} | {time_str} |")
