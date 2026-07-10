import transpiler

with open("hanoi_claude_1_7_fixed.sg", "r") as f:
    code = f.read()

try:
    print("--- Running Hanoi (N=3, src=1, dst=3, aux=2) ---")
    initial_stack = [3, 1, 3, 2]
    final_stack = transpiler.run_scrooge(code, initial_stack)
    print("Execution: SUCCESS")
    print("Final Stack:", final_stack)
    
    if len(final_stack) == 2:
        count, moves = final_stack[0], final_stack[1]
        print(f"Move Count: {count}")
        print(f"Moves: {moves}")
        
        expected_moves = [[1, 3], [1, 2], [3, 2], [1, 3], [2, 1], [2, 3], [1, 3]]
        if count == 7 and moves == expected_moves:
            print("\n>>> SUCCESS: Hanoi solver matches expectations exactly! <<<")
        else:
            print("\n>>> FAILURE: Mismatch in moves or count. <<<")
    else:
        print("Error: Stack elements count is not 2.")
except Exception as e:
    print("Execution: FAILED")
    import traceback
    traceback.print_exc()
