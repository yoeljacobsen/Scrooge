import sys
sys.path.insert(0, '.')
import json
import time
import transpiler

# Load problems
with open("problems.json", "r") as f:
    problems = json.load(f)

# We will run both solvers on the first 5 easy puzzles
num_puzzles = 5

# Set python recursion limit higher for recursive Sudoku calls
sys.setrecursionlimit(5000)

# Load fixed code for both solvers
with open("programs/sudoku_opus48_1_7_fixed.sg", "r") as f:
    opus_code = f.read()

with open("programs/sudoku_gemini35_1_7_fixed.sg", "r") as f:
    gemini_code = f.read()

print("--- Compiling Solvers ---")
opus_py = transpiler.transpile(opus_code)
gemini_py = transpiler.transpile(gemini_code)
print("Compilation successful.\n")

results = []

for i in range(num_puzzles):
    prob = problems[i]
    name = prob["NAME"]
    grid_2d = prob["GRID"]
    # Flatten grid
    flat_grid = [cell for row in grid_2d for cell in row]
    
    print(f"Running puzzle: {name}...")
    
    # Run Opus
    t0 = time.time()
    try:
        opus_stack = transpiler.run_scrooge(opus_code, [flat_grid])
        opus_time = (time.time() - t0) * 1000
        # Opus stack layout: [ solved_grid, steps ]
        if len(opus_stack) >= 2:
            opus_grid = opus_stack[0]
            opus_steps = opus_stack[1]
            opus_solved = int(0 not in opus_grid)
            opus_status = "PASS" if opus_solved == 1 else "FAIL"
        else:
            opus_steps = -1
            opus_status = "FAIL (Stack underflow)"
    except Exception as e:
        opus_time = -1
        opus_steps = -1
        opus_status = f"ERROR: {str(e)}"
    
    # Run Gemini
    t0 = time.time()
    try:
        gemini_stack = transpiler.run_scrooge(gemini_code, [flat_grid])
        gemini_time = (time.time() - t0) * 1000
        # Gemini stack layout: [ solved_grid, steps, flag ]
        if len(gemini_stack) >= 3:
            gemini_grid = gemini_stack[0]
            gemini_steps = gemini_stack[1]
            gemini_solved = gemini_stack[2]
            gemini_status = "PASS" if gemini_solved == 1 else "FAIL"
        else:
            gemini_steps = -1
            gemini_status = "FAIL (Stack underflow)"
    except Exception as e:
        gemini_time = -1
        gemini_steps = -1
        gemini_status = f"ERROR: {str(e)}"
        
    print(f"  Opus: {opus_status} in {opus_steps} steps ({opus_time:.2f} ms)")
    print(f"  Gemini: {gemini_status} in {gemini_steps} steps ({gemini_time:.2f} ms)")
    
    results.append({
        "name": name,
        "opus_status": opus_status,
        "opus_steps": opus_steps,
        "opus_time_ms": opus_time,
        "gemini_status": gemini_status,
        "gemini_steps": gemini_steps,
        "gemini_time_ms": gemini_time
    })

# Print a nice summary table
print("\n--- Summary Table ---")
print("| Puzzle | Opus Status | Opus Steps | Opus Time | Gemini Status | Gemini Steps | Gemini Time |")
print("|---|---|---|---|---|---|---|")
for r in results:
    opus_time_str = f"{r['opus_time_ms']:.2f} ms" if r['opus_time_ms'] >= 0 else "N/A"
    gemini_time_str = f"{r['gemini_time_ms']:.2f} ms" if r['gemini_time_ms'] >= 0 else "N/A"
    print(f"| {r['name']} | {r['opus_status']} | {r['opus_steps']} | {opus_time_str} | {r['gemini_status']} | {r['gemini_steps']} | {gemini_time_str} |")
