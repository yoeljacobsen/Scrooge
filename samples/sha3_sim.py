def sha3_step(state):
    new_state = []
    for i in range(5):
        val = state[i]
        next_val = state[(i + 1) % 5]
        mixed = (val ^ 1) & ~next_val ^ state[(i - 1) % 5]
        new_state.append(mixed)
    return new_state

if __name__ == "__main__":
    import sys
    import json
    state = json.loads(sys.argv[1]) if len(sys.argv) > 1 else [10, 20, 30, 40, 50]
    print("SHA-3 step:", sha3_step(state))
