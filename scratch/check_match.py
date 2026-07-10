import re

with open("sudoku_opus48_1_7.sg", "r") as f:
    code = f.read()

lines = code.split("\n")

# Replace ok block to simulate the actual line shifts
ok_replacement = [
    "  [",
    "    [ -> [ g idx v ]",
    "      [ g idx v valid ]",
    "    ]",
    "  ] -> [ ok ]"
]
lines[8:19] = ok_replacement

for idx, line in enumerate(lines):
    if "? ]" in line:
        has_fold = (idx + 1 < len(lines)) and ("\\ 0" in lines[idx + 1] or "\\ 0" in lines[idx + 1].encode('unicode_escape').decode())
        # Let's print the next line and whether it matches \ 0
        print(f"Line {idx+1}: {line}")
        if idx + 1 < len(lines):
            print(f"  Next: {lines[idx+1]} | '\\ 0' in next: {'\\ 0' in lines[idx+1]}")
