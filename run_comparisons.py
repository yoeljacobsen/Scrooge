import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'compiler'))
import time
import json
import tokenize as py_tokenize
import io
import transpiler
import traceback

# Try importing tiktoken for cl100k_base tokens
try:
    import tiktoken
    tiktoken_available = True
    enc = tiktoken.get_encoding("cl100k_base")
except ImportError:
    tiktoken_available = False

# Define sample files
samples = [
    {
        "name": "Fibonacci",
        "scrooge_file": "samples/fibonacci.sg",
        "python_file": "samples/fibonacci.py",
        "args": [10],
        "expected": [55],
        "attempts_scrooge": 1,
        "attempts_python": 1
    },
    {
        "name": "GCD",
        "scrooge_file": "samples/gcd.sg",
        "python_file": "samples/gcd.py",
        "args": [105, 252],
        "expected": [21],
        "attempts_scrooge": 1,
        "attempts_python": 1
    },
    {
        "name": "SHA-3 Permutation Step",
        "scrooge_file": "samples/sha3_sim.sg",
        "python_file": "samples/sha3_sim.py",
        "args": [[10, 20, 30, 40, 50]],
        "expected": [[57, 11, 3, 23, 25]],
        "attempts_scrooge": 3,
        "attempts_python": 1
    },
    {
        "name": "Matrix Gen",
        "scrooge_file": "samples/matrix_gen.sg",
        "python_file": "samples/matrix_gen.py",
        "args": [10],
        "expected": [[( (i // 10) * (i % 10) * 1.0 ) / 1001.0 for i in range(100)]],
        "attempts_scrooge": 2,
        "attempts_python": 1
    },
    {
        "name": "Hessenberg QR (3x3)",
        "scrooge_file": "samples/hessenberg_qr_v1.3.sg",
        "python_file": "samples/hessenberg_qr_v1.3.py",
        "args": [],
        "expected": [[0.000999000999000999, 0.001998001998001998, 0.002997002997002997, 0.001998001998001998, 0.003996003996003996, 0.005994005994005994, 0.0, 0.005994005994005994, 0.008991008991008992]],
        "attempts_scrooge": 1,
        "attempts_python": 1
    }
]

def count_py_tokens(code):
    try:
        tokens = list(py_tokenize.generate_tokens(io.StringIO(code).readline))
        # Filter out ENDMARKER
        tokens = [t for t in tokens if t.type != py_tokenize.ENDMARKER]
        return len(tokens)
    except Exception:
        return len(code.split())

def count_sg_tokens(code):
    try:
        return len(transpiler.tokenize(code))
    except Exception:
        return len(code.split())

def count_llm_tokens(code):
    if tiktoken_available:
        return len(enc.encode(code))
    return None

print("# Performance & Design Metrics Comparison\n")

# Prepare columns for table
headers = ["Metric", "Fibonacci (Sg)", "Fibonacci (Py)", "GCD (Sg)", "GCD (Py)", "SHA-3 Step (Sg)", "SHA-3 Step (Py)", "Matrix Gen (Sg)", "Matrix Gen (Py)", "Hessenberg QR (Sg)", "Hessenberg QR (Py)"]
row_char = ["Character Count"]
row_tok_lang = ["Language Token Count"]
row_tok_llm = ["LLM Token (cl100k_base)"]
row_attempts = ["Attempts to Correctness"]
row_match = ["Output Correctness"]
row_time = ["Execution Time (ms)"]

for s in samples:
    # Read files
    with open(s["scrooge_file"], "r") as f:
        sg_code = f.read().strip()
    with open(s["python_file"], "r") as f:
        py_code = f.read().strip()
        
    # Char & Token count
    row_char.append(f"{len(sg_code)} chars")
    row_char.append(f"{len(py_code)} chars")
    
    row_tok_lang.append(f"{count_sg_tokens(sg_code)} tokens")
    row_tok_lang.append(f"{count_py_tokens(py_code)} tokens")
    
    llm_sg = count_llm_tokens(sg_code)
    llm_py = count_llm_tokens(py_code)
    if llm_sg is not None:
        row_tok_llm.append(f"{llm_sg} tokens")
        row_tok_llm.append(f"{llm_py} tokens")
    else:
        row_tok_llm.append("N/A")
        row_tok_llm.append("N/A")
        
    # Attempts
    row_attempts.append(f"{s['attempts_scrooge']}")
    row_attempts.append(f"{s['attempts_python']}")
    
    # Run Python
    import importlib.util
    spec = importlib.util.spec_from_file_location(s["name"].replace(" ", "_").replace("(", "").replace(")", ""), s["python_file"])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if s["name"] == "Fibonacci":
        py_func = module.fib
    elif s["name"] == "GCD":
        py_func = module.gcd
    elif s["name"] == "SHA-3 Permutation Step":
        py_func = module.sha3_step
    elif s["name"] == "Matrix Gen":
        py_func = module.generate_test_matrix
    else:
        py_func = module.run_hessenberg_qr
        
    # Profiling & Validation
    iterations = 10000
    if s["name"] in ("Matrix Gen", "Hessenberg QR (3x3)"):
        iterations = 100  # reduce matrix iterations to avoid slow down
        
    # Python profiling
    t0 = time.perf_counter()
    for _ in range(iterations):
        py_res = py_func(*s["args"])
    t1 = time.perf_counter()
    py_time = (t1 - t0) * 1000 / iterations
    
    # Scrooge profiling
    t0 = time.perf_counter()
    for _ in range(iterations):
        sg_res = transpiler.run_scrooge(sg_code, s["args"])
    t1 = time.perf_counter()
    sg_time = (t1 - t0) * 1000 / iterations
    
    # Check correctness
    correct = False
    if s["name"] in ("Fibonacci", "GCD"):
        correct = (sg_res == s["expected"]) and (py_res == s["expected"][0])
    else:
        if isinstance(sg_res, list) and len(sg_res) > 0 and isinstance(sg_res[0], list):
            import math
            correct = len(sg_res[0]) == len(s["expected"][0]) and all(math.isclose(a, b, rel_tol=1e-9) for a, b in zip(sg_res[0], s["expected"][0]))
        else:
            correct = (sg_res == s["expected"]) and (py_res == s["expected"][0])
        
    row_match.append("PASS" if correct else f"FAIL (got {sg_res})")
    row_match.append("PASS" if py_res == s["expected"][0] or (isinstance(py_res, list) and py_res == s["expected"][0]) else "FAIL")
    
    row_time.append(f"{sg_time:.4f} ms")
    row_time.append(f"{py_time:.4f} ms")

def print_row(row):
    print("| " + " | ".join(row) + " |")

# Print markdown table
print("| " + " | ".join(headers) + " |")
print("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
print_row(row_char)
print_row(row_tok_lang)
if tiktoken_available:
    print_row(row_tok_llm)
print_row(row_attempts)
print_row(row_match)
print_row(row_time)

print("\n## Verification of code_1.3.sg\n")

# Verify code_1.3.sg
try:
    with open("programs/code_1.3.sg", "r") as f:
        code_1_3 = f.read()
    
    # Check transpilation of code_1.3.sg
    transpiler.transpile(code_1_3)
    print("* **Transpilation:** PASS (code_1.3.sg transpiles successfully to Python source code)")
    
    # Check downscaled run of code_1.3.sg
    try:
        downscaled_code = code_1_3.replace("1000000", "9").replace("1000", "3").replace("999,999", "8")
        result = transpiler.run_scrooge(downscaled_code)
        
        # Verify correctness of downscaled Hessenberg matrix output
        expected_matrix = [0.000999000999000999, 0.001998001998001998, 0.002997002997002997, 0.001998001998001998, 0.003996003996003996, 0.005994005994005994, 0.0, 0.005994005994005994, 0.008991008991008992]
        import math
        correct = len(result[0]) == len(expected_matrix) and all(math.isclose(a, b, rel_tol=1e-9) for a, b in zip(result[0], expected_matrix))
        
        if correct:
            print("* **Execution:** PASS (Downscaled execution runs successfully and matches expected math results)")
        else:
            print(f"* **Execution:** FAIL (Output does not match expected Hessenberg form. Got: {result})")
    except Exception as run_err:
        tb = traceback.format_exc()
        last_line = tb.strip().split("\n")[-1]
        print(f"* **Execution:** FAIL")
        print(f"  * *Error Reason:* {last_line}")

except Exception as e:
    print(f"* **Verification Error:** FAILED to read/process files: {e}")
