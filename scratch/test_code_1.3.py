import transpiler
import traceback

def test_run():
    print("--- Transpiling Original code_1.3.sg ---")
    with open("programs/code_1.3.sg", "r") as f:
        code = f.read()
        
    try:
        py_source = transpiler.transpile(code)
        print("Transpilation of code_1.3.sg: SUCCESS")
    except Exception as e:
        print("Transpilation of code_1.3.sg: FAILED")
        traceback.print_exc()
        return

    print("\n--- Running Downscaled v1.3 Test (Dimension N=3) ---")
    downscaled_code = code.replace("1000000", "9").replace("1000", "3").replace("999,999", "8")
    
    try:
        result = transpiler.run_scrooge(downscaled_code)
        print("Downscaled Run: SUCCESS")
        print("Final Stack:", result)
    except Exception as e:
        print("Downscaled Run: FAILED")
        traceback.print_exc()

if __name__ == "__main__":
    test_run()
