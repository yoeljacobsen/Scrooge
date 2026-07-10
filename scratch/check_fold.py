import transpiler

with open("scratch/sudoku_opus48_1_7_fixed.sg", "r") as f:
    code = f.read()

tokens = transpiler.tokenize(code)
parsed = transpiler.parse(tokens)

# Let's find the block containing | f v | recursively
def find_fv_block(items):
    for item in items:
        if isinstance(item, transpiler.Block):
            if len(item.elements) > 0 and isinstance(item.elements[0], tuple) and item.elements[0][0] == 'BAR_BLOCK' and 'f' in item.elements[0][1] and 'v' in item.elements[0][1]:
                return item
            res = find_fv_block(item.elements)
            if res:
                return res
    return None

fv_block = find_fv_block(parsed)
if fv_block:
    print("Found | f v | block!")
    print("Elements count:", len(fv_block.elements))
    for idx, el in enumerate(fv_block.elements):
        print(f"  [{idx}]: {el}")
else:
    print("Could not find | f v | block!")
