import os
import csv
import math
import numpy as np
import transpiler
import traceback

def load_first_sample():
    csv_path = os.path.join("data", "mnist_train.csv")
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        row = next(reader)
    label = int(row[0])
    pixels = [float(x) / 255.0 for x in row[1:]]
    one_hot = [0.0] * 10
    one_hot[label] = 1.0
    return pixels, one_hot, label

def run_mnist_py(X, W, B, labels, lr):
    # Forward Pass
    logits = []
    for i in range(10):
        dot = sum(W[i][j] * X[j] for j in range(784))
        logits.append(dot + B[i])
        
    # Softmax
    exps = [math.exp(l) for l in logits]
    sum_exps = sum(exps)
    probs = [e / sum_exps for e in exps]
    
    # Backward Pass (d_logits = probs - labels)
    d_logits = [probs[i] - labels[i] for i in range(10)]
    
    # Update B
    new_B = [B[i] - lr * d_logits[i] for i in range(10)]
    
    # Update W
    new_W = []
    for i in range(10):
        row_w = []
        for j in range(784):
            row_w.append(W[i][j] - lr * d_logits[i] * X[j])
        new_W.append(row_w)
        
    return new_W, new_B

def test_mnist():
    X, labels, digit = load_first_sample()
    
    np.random.seed(42)
    W = (np.random.randn(10, 784) * 0.01).tolist()
    B = [0.0] * 10
    lr = 0.1
    
    # Run Python reference
    new_W_py, new_B_py = run_mnist_py(X, W, B, labels, lr)
    
    with open("mnst.sg", "r") as f:
        scrooge_code = f.read()
        
    # Append the execution trigger
    scrooge_code = scrooge_code + "\nv1.4_mnist_nn"
    
    try:
        py_source = transpiler.transpile(scrooge_code)
        print("Transpilation: SUCCESS")
    except Exception as e:
        print("Transpilation: FAILED")
        traceback.print_exc()
        return

    print("\n--- Running Scrooge NN Step ---")
    try:
        initial_stack = [X, W, B, labels, lr]
        final_stack = transpiler.run_scrooge(scrooge_code, initial_stack)
        print("Scrooge Run: SUCCESS")
        
        print(f"Final Stack elements count: {len(final_stack)}")
        if len(final_stack) >= 2:
            new_W_sg = final_stack[0]
            new_B_sg = final_stack[1]
            
            # Compare biases
            b_diff = np.abs(np.array(new_B_py) - np.array(new_B_sg))
            print(f"Max Bias Difference: {b_diff.max():.2e}")
            
            # Compare weights
            w_diff = np.abs(np.array(new_W_py) - np.array(new_W_sg))
            print(f"Max Weight Difference: {w_diff.max():.2e}")
            
            if b_diff.max() < 1e-9 and w_diff.max() < 1e-9:
                print("\n>>> SUCCESS: Scrooge output matches Python reference exactly! <<<")
            else:
                print("\n>>> FAILURE: Outputs do not match. <<<")
        else:
            print("Error: Scrooge final stack did not return updated W and B.")
            print("Stack elements:", final_stack)
    except Exception as e:
        print("Scrooge Run: FAILED")
        traceback.print_exc()

if __name__ == "__main__":
    test_mnist()
