import transpiler

# 1. Fix Opus 4.8 syntax
with open("sudoku_opus48_1_7.sg", "r") as f:
    opus_lines = f.readlines()
# Remove the last line if it's just ']'
if opus_lines[-1].strip() == "]":
    opus_fixed = "".join(opus_lines[:-1])
else:
    opus_fixed = "".join(opus_lines)

with open("scratch/sudoku_opus48_1_7_fixed.sg", "w") as f:
    f.write(opus_fixed)

# 2. Fix Gemini 3.5 syntax
with open("sudoku_gemini35_1_7.sg", "r") as f:
    gemini_lines = f.readlines()

# Wrap the last line in a block
last_line = gemini_lines[-1]
gemini_lines[-1] = f"[ {last_line.strip()} ]\n"
gemini_fixed = "".join(gemini_lines)

with open("scratch/sudoku_gemini35_1_7_fixed.sg", "w") as f:
    f.write(gemini_fixed)

print("Syntax correction files generated.")

# Try transpiling both
for name in ["scratch/sudoku_opus48_1_7_fixed.sg", "scratch/sudoku_gemini35_1_7_fixed.sg"]:
    print(f"\nTranspiling {name}...")
    try:
        with open(name, "r") as f:
            code = f.read()
        py_source = transpiler.transpile(code)
        print("SUCCESS!")
        with open(name.replace(".sg", "_transpiled.py"), "w") as f_out:
            f_out.write(py_source)
    except Exception as e:
        print("FAILED!")
        import traceback
        traceback.print_exc()
