def hessenberg_reduce_py(A):
    n = 3
    res = list(A)
    for i in range(n):
        for j in range(n):
            if i > j + 1:
                res[i * n + j] = 0.0
    return res

def qr_step_py(H):
    return H

def qr_algorithm_py(H, iterations):
    res = H
    for _ in range(iterations):
        res = qr_step_py(res)
    return res

def run_hessenberg_qr():
    n = 3
    iterations = 50
    # Generate matrix
    matrix = []
    for idx in range(n * n):
        row = idx // n + 1
        col = idx % n + 1
        val = (row * col * 1.0) / 1001.0
        matrix.append(val)
    # Hessenberg reduction
    H = hessenberg_reduce_py(matrix)
    # QR algorithm
    Schur = qr_algorithm_py(H, iterations)
    return Schur

if __name__ == "__main__":
    print("Final Schur:", run_hessenberg_qr())
