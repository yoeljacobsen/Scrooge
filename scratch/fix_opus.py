import transpiler
import re

with open("programs/sudoku_opus48_1_7.sg", "r") as f:
    code = f.read()

opus_lines = code.split("\n")

# 1. Replace custom ok implementation (lines 10-19, 0-indexed 9-18) with a wrapper for native 'valid'
ok_replacement = [
    "    [ -> [ g idx v ]",
    "      [ g idx v valid ]",
    "    ] -> [ ok ]"
]

print("Replacing custom ok function with native valid wrapper...")
opus_lines[9:19] = ok_replacement

# 2. Fix the multiple body blocks for 'res' on line 43 (which has shifted to line 37)
found_43 = -1
for idx, line in enumerate(opus_lines):
    if "[ res 0 : ] [ res 1 : ] [ res 2 : ]" in line:
        found_43 = idx
        break

if found_43 != -1:
    print(f"Fixing res index line {found_43+1}: {opus_lines[found_43]}")
    opus_lines[found_43] = opus_lines[found_43].replace("[ res 0 : ] [ res 1 : ] [ res 2 : ]", "res 0 : res 1 : res 2 :")
else:
    print("WARNING: Could not find res index line!")

# 3. Fix early closed fold block on line 40 (which has shifted to line 34)
found_40 = -1
for idx, line in enumerate(opus_lines):
    if "? ]" in line and idx + 1 < len(opus_lines) and "\\ 0" in opus_lines[idx + 1]:
        found_40 = idx
        break

if found_40 != -1:
    print(f"Fixing fold block boundaries on line {found_40+1}")
    opus_lines[found_40] = opus_lines[found_40].replace("? ]", "?")
else:
    print("WARNING: Could not find fold block boundary line!")

# 4. Fix [ f 0 : ] and [ f 2 : ] bracket lookups to run eagerly
for idx, line in enumerate(opus_lines):
    if "[ f 0 : ]" in line:
        print(f"Fixing f 0 : index line {idx+1}: {line}")
        opus_lines[idx] = line.replace("[ f 0 : ]", "f 0 :")
    if "[ f 2 : ]" in line:
        print(f"Fixing f 2 : index line {idx+1}: {line}")
        opus_lines[idx] = line.replace("[ f 2 : ]", "f 2 :")

code_fixed = "\n".join(opus_lines)

# 5. Replace hardcoded runner block with dynamic solver execution on stack grid
runner_old = """      [
        [ 5 3 0 0 7 0 0 0 0
          6 0 0 1 9 5 0 0 0
          0 9 8 0 0 0 0 6 0
          8 0 0 0 6 0 0 0 3
          4 0 0 8 0 3 0 0 1
          7 0 0 0 2 0 0 0 6
          0 6 0 0 0 0 2 8 0
          0 0 0 4 1 9 0 0 5
          0 0 0 0 8 0 0 7 9 ]
        0 ^solve -> [ f grid steps ]
        [ grid steps
          | grid:Int[81] : solved:Int[81] | ]
      ]"""

runner_new = """      [
        0 ^solve -> [ f grid steps ]
        grid steps
      ]"""

print("Replacing hardcoded grid runner with dynamic grid runner...")
code_fixed = code_fixed.replace(runner_old, runner_new)

# Replace 'and' with '&' and 'or' with '|' (taking care to match them as whole words)
code_fixed = re.sub(r'\band\b', '&', code_fixed)
code_fixed = re.sub(r'\bor\b', '|', code_fixed)

with open("scratch/sudoku_opus48_1_7_fixed.sg", "w") as f:
    f.write(code_fixed)

print("Corrections applied to Opus code.")

try:
    py_source = transpiler.transpile(code_fixed)
    print("\nTranspilation: SUCCESS!")
    with open("scratch/sudoku_opus48_1_7_transpiled.py", "w") as f_out:
        f_out.write(py_source)
    print("Saved transpiled python output to scratch/sudoku_opus48_1_7_transpiled.py")
except Exception as e:
    print("\nTranspilation: FAILED")
    import traceback
    traceback.print_exc()
