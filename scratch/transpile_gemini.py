import transpiler

with open("programs/sudoku_gemini35_1_7.sg", "r") as f:
    code = f.read()

try:
    py_source = transpiler.transpile(code)
    print("Transpilation SUCCESS!")
    with open("scratch/sudoku_gemini35_1_7_transpiled.py", "w") as f_out:
        f_out.write(py_source)
except Exception as e:
    print("Transpilation FAILED!")
    import traceback
    traceback.print_exc()
