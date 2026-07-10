def generate_test_matrix(n):
    matrix = []
    for idx in range(n * n):
        row = idx // n
        col = idx % n
        val = (row * col * 1.0) / 1001.0
        matrix.append(val)
    return matrix

if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    print("Matrix:", generate_test_matrix(n))
