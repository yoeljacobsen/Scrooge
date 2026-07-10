import transpiler
import re

with open("sudoku_opus48_1_7.sg", "r") as f:
    code = f.read()

opus_lines = code.split("\n")

# 1. Replace custom ok implementation (lines 9-19, 0-indexed 8-18) with a wrapper for native 'valid'
ok_replacement = [
    "  [",
    "    [ -> [ g idx v ]",
    "      [ g idx v valid ]",
    "    ]",
    "  ] -> [ ok ]"
]

print("Replacing custom ok function with native valid wrapper...")
opus_lines[8:19] = ok_replacement

# 2. Fix the solve binding scope on line 46
found_idx = -1
for idx, line in enumerate(opus_lines):
    if "] -> [ solve ]" in line:
        found_idx = idx
        break

if found_idx != -1:
    print(f"Fixing solve scope line {found_idx+1}: {opus_lines[found_idx]}")
    opus_lines[found_idx] = opus_lines[found_idx].replace("] -> [ solve ]", "-> [ solve ]")
else:
    print("WARNING: Could not find solve binding line!")

# 3. Fix the nested body block of -> [ rf rg rs ]
found_33 = -1
found_37 = -1
for idx, line in enumerate(opus_lines):
    if "-> [ rf rg rs ]" in line:
        found_33 = idx
    if "? ]" in line and idx + 1 < len(opus_lines) and "else" in opus_lines[idx + 1].strip() and found_33 != -1 and found_37 == -1:
        found_37 = idx

if found_33 != -1 and found_37 != -1:
    print(f"Fixing binding body on line {found_33+1} and {found_37+1}")
    opus_lines[found_33] = opus_lines[found_33] + " ["
    opus_lines[found_37] = opus_lines[found_37] + " ]"
else:
    print("WARNING: Could not find lines for nested body block wrapping!", found_33, found_37)

# 4. Fix the multiple body blocks for 'res' on line 43
found_43 = -1
for idx, line in enumerate(opus_lines):
    if "[ res 0 : ] [ res 1 : ] [ res 2 : ]" in line:
        found_43 = idx
        break

if found_43 != -1:
    print(f"Fixing res index line {found_43+1}: {opus_lines[found_43]}")
    opus_lines[found_43] = opus_lines[found_43].replace("[ res 0 : ] [ res 1 : ] [ res 2 : ]", "[ res 0 : res 1 : res 2 : ]")
else:
    print("WARNING: Could not find res index line!")

# 5. Fix early closed fold block (using robust next-line lookahead for '\ 0')
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

code_fixed = "\n".join(opus_lines)

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
