import os
import csv
import math
import numpy as np
import transpiler
import traceback

def load_dataset_samples(num_samples=5):
    csv_path = os.path.join("data", "mnist_train.csv")
    dataset = []
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        for idx, row in enumerate(reader):
            if idx >= num_samples:
                break
            label = int(row[0])
            pixels = [float(x) / 255.0 for x in row[1:]]
            one_hot = [0.0] * 10
            one_hot[label] = 1.0
            # Each sample is [x, y]
            dataset.append([pixels, one_hot])
    return dataset

def run_mnist_epochs_py(D, W, b, epochs=3, lr=0.01):
    W_curr = [list(row) for row in W]
    b_curr = list(b)
    
    for epoch in range(epochs):
        for sample in D:
            x, y = sample[0], sample[1]
            
            # Forward Pass (fwd)
            logits = []
            for i in range(10):
                dot = sum(W_curr[i][j] * x[j] for j in range(784))
                logits.append(dot + b_curr[i])
                
            # Softmax (smax)
            exps = [math.exp(l) for l in logits]
            sum_exps = sum(exps)
            probs = [e / sum_exps for e in exps]
            
            # Gradients (grad)
            g = [probs[i] - y[i] for i in range(10)]
            
            # Weight & Bias update (step)
            new_b = [b_curr[i] - lr * g[i] for i in range(10)]
            new_W = []
            for i in range(10):
                row_w = []
                for j in range(784):
                    row_w.append(W_curr[i][j] - lr * g[i] * x[j])
                new_W.append(row_w)
                
            W_curr = new_W
            b_curr = new_b
            
    return W_curr, b_curr

def run_evaluation(label, filename, D, W0, b0, W_star_py, b_star_py):
    print(f"\n==================================================")
    print(f"EVALUATING: {label} ({filename})")
    print(f"==================================================")
    with open(filename, "r") as f:
        scrooge_code = f.read()
        
    try:
        py_source = transpiler.transpile(scrooge_code)
        print("Transpilation: SUCCESS")
        debug_path = f"scratch/transpiled_{label.lower().replace(' ', '_')}.py"
        os.makedirs("scratch", exist_ok=True)
        with open(debug_path, "w") as f:
            f.write(py_source)
        print(f"Wrote transpiled code to {debug_path}")
    except Exception as e:
        print("Transpilation: FAILED")
        traceback.print_exc()
        return

    try:
        initial_stack = [D, W0, b0]
        final_stack = transpiler.run_scrooge(scrooge_code, initial_stack)
        print("Scrooge Run: SUCCESS")
        print(f"Final Stack elements count: {len(final_stack)}")
        
        if len(final_stack) == 2:
            W_star_sg = final_stack[0]
            b_star_sg = final_stack[1]
            
            # Compare biases
            b_diff = np.abs(np.array(b_star_py) - np.array(b_star_sg))
            print(f"Max Bias Difference: {b_diff.max():.2e}")
            
            # Compare weights
            w_diff = np.abs(np.array(W_star_py) - np.array(W_star_sg))
            print(f"Max Weight Difference: {w_diff.max():.2e}")
            
            if b_diff.max() < 1e-9 and w_diff.max() < 1e-9:
                print(">>> SUCCESS: Scrooge output matches Python reference exactly! <<<")
            else:
                print(">>> FAILURE: Outputs do not match. <<<")
        else:
            print("Error: Scrooge final stack did not return exactly [W*, b*].")
            print("Stack elements count:", len(final_stack))
            if len(final_stack) < 10:
                print("Stack contents:", final_stack)
    except Exception as e:
        print("Scrooge Run: FAILED")
        traceback.print_exc()

def test_mnist_claude():
    D = load_dataset_samples(5)
    
    np.random.seed(42)
    W0 = (np.random.randn(10, 784) * 0.01).tolist()
    b0 = [0.0] * 10
    
    # Run Python reference epochs training
    print("--- Running Python Reference epochs training ---")
    W_star_py, b_star_py = run_mnist_epochs_py(D, W0, b0, epochs=3, lr=0.01)
    
    # Run evaluation on both versions
    run_evaluation("Original Claude v1.5", "mnist_claude_15.sg", D, W0, b0, W_star_py, b_star_py)
    run_evaluation("Fixed Claude v1.5", "mnist_claude_15_fixed.sg", D, W0, b0, W_star_py, b_star_py)

if __name__ == "__main__":
    test_mnist_claude()
