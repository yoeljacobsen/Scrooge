import transpiler

with open("scratch/sudoku_opus48_1_7_fixed.sg", "r") as f:
    code = f.read()

tokens = transpiler.tokenize(code)
parsed = transpiler.parse(tokens)

block_b = parsed[3]
block_d = block_b.elements[6]
child = block_d.elements[0]

print("Child block elements:")
for i, el in enumerate(child.elements):
    if isinstance(el, transpiler.Block):
         print(f"[{i}] Block with {len(el.elements)} elements")
    else:
         print(f"[{i}] Token: {el}")
