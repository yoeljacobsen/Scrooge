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
            dataset.append([pixels, one_hot])
    return dataset

def run_mnist_epochs_py(D, epochs=5, lr=0.05):
    W_curr = [[0.0] * 784 for _ in range(10)]
    b_curr = [0.0] * 10
    
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
            g = [probs[k] - y[k] for k in range(10)]
            
            # Weight & Bias update (step)
            new_b = [b_curr[k] - lr * g[k] for k in range(10)]
            new_W = []
            for i in range(10):
                row_w = []
                for j in range(784):
                    row_w.append(W_curr[i][j] - lr * g[i] * x[j])
                new_W.append(row_w)
                
            W_curr = new_W
            b_curr = new_b
            
    return W_curr, b_curr

def print_nested_shape(val, name="stack", indent=0):
    ind = " " * indent
    if isinstance(val, list):
        print(f"{ind}{name}: list of length {len(val)}")
        if len(val) > 0:
            print_nested_shape(val[0], f"{name}[0]", indent + 4)
    else:
        print(f"{ind}{name}: {type(val)} = {val}")

def test_mnist_claude_16():
    D = load_dataset_samples(5)
    mnist_images = [sample[0] for sample in D]
    mnist_labels = [sample[1] for sample in D]
    
    W_star_py, b_star_py = run_mnist_epochs_py(D, epochs=5, lr=0.05)
    
    with open("mnist_claude_16_fixed.sg", "r") as f:
        scrooge_code = f.read()
        
    try:
        py_source = transpiler.transpile(scrooge_code)
        print("Transpilation: SUCCESS")
    except Exception as e:
        print("Transpilation: FAILED")
        traceback.print_exc()
        return

    try:
        initial_stack = [mnist_images, mnist_labels]
        final_stack = transpiler.run_scrooge(scrooge_code, initial_stack)
        print("Scrooge Run: SUCCESS")
        print("\n--- Scrooge Final Stack Diagnostic Shape Analysis ---")
        print_nested_shape(final_stack, "final_stack")
        
        # Try to unpack the weights and biases from the nested structure
        # Let's see: we expect [W_final, b_final] somewhere in the stack
        curr = final_stack
        while isinstance(curr, list) and len(curr) == 1:
            curr = curr[0]
            
        if isinstance(curr, list) and len(curr) == 2:
            W_star_sg = curr[0]
            b_star_sg = curr[1]
            
            # Compare biases
            b_diff = np.abs(np.array(b_star_py) - np.array(b_star_sg))
            print(f"\nMax Bias Difference: {b_diff.max():.2e}")
            
            # Compare weights
            w_diff = np.abs(np.array(W_star_py) - np.array(W_star_sg))
            print(f"Max Weight Difference: {w_diff.max():.2e}")
            
            if b_diff.max() < 1e-9 and w_diff.max() < 1e-9:
                print("\n>>> SUCCESS: Scrooge Claude v1.6 output matches Python reference exactly! <<<")
            else:
                print("\n>>> FAILURE: Outputs do not match. <<<")
        else:
            print("\nError: Could not locate [W, b] structure automatically.")
    except Exception as e:
        print("Scrooge Run: FAILED")
        traceback.print_exc()

if __name__ == "__main__":
    test_mnist_claude_16()
