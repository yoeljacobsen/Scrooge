def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

if __name__ == "__main__":
    import sys
    a = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    b = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    print("GCD:", gcd(a, b))
