import transpiler

scrooge_code = """
#generate_test_matrix [
    . . *
    [ ]
    @ $ @
    0 $
    [
        2 pick
        1 pick
        $ //
        3 pick
        2 pick
        $ \\
        * 1.0 * 1001.0 /
        @ $ + $ 1 +
    ] !
    % $ %
]
3 generate_test_matrix
"""

try:
    print("Transpiling matrix generator...")
    py_code = transpiler.transpile(scrooge_code)
    print("Transpilation successful!")
    print("\nRunning matrix generator...")
    stack = transpiler.run_scrooge(scrooge_code)
    print("Final Stack:", stack)
except Exception as e:
    import traceback
    traceback.print_exc()
