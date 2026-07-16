# Scrooge Robust Development Skill (v1.43)

This skill governs the testing, verification, and design-evolution loops of the Scrooge v1.43 ecosystem. It decouples execution and safety policies from core language syntax.

## Core Directives

### 1. Execution-First Verification (Step B2 Gate)
- Passing `scrooge_check.py` is a necessary baseline but NEVER guarantees correctness. Static-clean code can be semantically broken or crash at runtime.
- You must always verify logic by appending a validation execution step, running it through the reference interpreter (`scrooge.py`), and checking that the returned scalar values match the execution specification.
- If a patch passes the linter but fails the runtime execution check, it is a FAILED patch. Roll back immediately.

### 2. Sandbox Security & Integrity
- Never execute, alter, or write files to the neighbor `../Scrooge` production directory during repair loop operations.
- The system prompt must remain entirely declarative and code-focused. It must never contain instructions for git execution, dependency installation, or shell tool calls.

### 3. Anti-Thrashing & Honest RFEs
- If a word fails to converge within N = 3 retries, do not force a degenerate, useless "arity-only" patch (e.g., dropping raw elements or inserting dummy values just to silence the compiler).
- If the language lacks the library or core primitives required to express the operation, trigger the Intelligent RFE Diagnostic Pass. Save a structured RFE JSON file containing draft library implementations or compiler updates.

### 4. Code vs. Data Nesting Enforcer
- Code Nesting: Any bracketed block containing operations, word calls, or bindings nested inside another block is strictly ILLEGAL.
- Data Nesting: Bracketed blocks containing only numeric scalars, spaces, or nested data blocks are explicitly EXEMPT from the nesting cap.
