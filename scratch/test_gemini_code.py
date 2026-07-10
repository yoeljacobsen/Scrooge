import transpiler
import traceback

def test_run():
    # Read both files
    with open("gemini-code-1783591633935.txt", "r") as f:
        code1 = f.read()
    with open("gemini-code-1783591637507.txt", "r") as f:
        code2 = f.read()
        
    combined_code = code1 + "\n" + code2
    print("--- Transpiling Combined Code ---")
    try:
        py_source = transpiler.transpile(combined_code)
        print("Transpilation: SUCCESS")
    except Exception as e:
        print("Transpilation: FAILED")
        traceback.print_exc()
        return

    print("\n--- Running Combined Code ---")
    try:
        result = transpiler.run_scrooge(combined_code)
        print("Run: SUCCESS")
        print("Final Stack:", result)
    except Exception as e:
        print("Run: FAILED")
        traceback.print_exc()

if __name__ == "__main__":
    test_run()
