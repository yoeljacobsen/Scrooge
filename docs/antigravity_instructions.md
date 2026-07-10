# Antigravity Orchestration Profile: Code Generation Instructions for Scrooge (v1.2)

This document contains instructions to configure the system prompt, agent profile context, or custom Skill definitions inside your **Google Antigravity** environment to generate error-free Scrooge script blocks.

---

## 1. Antigravity Agent Directives

When processing or issuing an Implementation Plan involving Scrooge files, enforce the following constraints on the agent's logic engine:

1. **Enforce the Immutability Model:** Scrooge list operations (especially `::`) are copy-on-write. Warn subagents never to write destruction loops; backtrack flows should rely entirely on passing the updated array state down the execution line.
2. **Never Invent Namespaces:** Scrooge contains no variables. If an implementation draft shows names assigned to temporary scopes (e.g., inside a `[ ... ]` block), discard the code artifact immediately and force a rewrite.
3. **Optimize Using Deep Access:** If a task requires processing data elements located deeper than three levels down the current stack register, do not write wrapping operations (`wrap +`). Instruct the agent to use `pick` or `roll` directly to eliminate structural token overhead.
4. **Isolate Concatenation from Prepends:** Emphasize to the agent that `+` combines lists together. When pushing an item to the head of a matrix line without losing its structural identity, the agent must use the native `cons` primitive.

---

## 2. Structured Task System Prompt Template

Copy and paste this instruction directly into the **Antigravity Workspace Settings** or your agent's initial generation prompt:

```text
You are a development agent operating inside the Scrooge language framework (v1.2).
You must write code using absolute token economy, zero mutable naming conventions, and purely functional stack operations.

Your Code Compilation Checklist:
1. Verify Stack Balance: Ensure every macro block accurately clears or fulfills its target stack footprint.
2. Use Flat Layouts: Prefer shallow stack depths using `pick` or loop maps (`!`) over nested code trees.
3. Format Explicit Outputs: Wrap the final clean Scrooge script code cleanly within code fences like:
   ```text
   [ code here ]
   ```
```

---

## 3. Practical Verification Strategy

To test whether your Antigravity agent has fully digested these properties, run this baseline verification prompt on its scratchpad:

> **Validation Task:** "Write a Scrooge v1.2 macro called `#square_sum` that takes a block array of integers, squares each individual integer, sums them up, and outputs only the final single integer to the stack."

**Expected Valid Agent Output:**
```text
#square_sum [ 0 $ [ . * + ] ! ]
```
*(Token Count: 10. Trace: Seed total with 0, swap the array to the top, map each item, duplicate it, square it via `*`, add to the cumulative total via `+`.)*
