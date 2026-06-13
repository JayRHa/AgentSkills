# Worked Example: Explaining Recursion at Three Levels

## ELI5
Imagine you're standing in a long line and want to know your position. You can't see the front, so you tap the person ahead and ask, "What's your number?" They don't know either, so they ask the person ahead of *them*. This keeps going until it reaches the very first person, who says "I'm number 1!" Then each answer comes back: "I'm 2", "I'm 3"… until you learn you're number 50. **Recursion is solving a problem by asking a smaller version of the same problem, until you hit a case simple enough to answer directly.**

## Novice (with code)
A recursive function calls itself on a smaller input and has a **base case** that stops the chain.

```python
def factorial(n):
    if n <= 1:        # base case — answer directly
        return 1
    return n * factorial(n - 1)   # recursive case — smaller problem
```
`factorial(3)` → `3 * factorial(2)` → `3 * 2 * factorial(1)` → `3 * 2 * 1 = 6`.

**Where it breaks:** the line analogy suggests it's free, but each call uses stack memory. Too deep (e.g. `factorial(100000)`) and you get a *stack overflow*.

## Practitioner
Recursion trades clarity for stack cost. Every recursive problem can be rewritten iteratively. Use recursion when the problem is **naturally recursive** (trees, divide-and-conquer, backtracking) and depth is bounded; otherwise prefer iteration or convert to **tail recursion** (where supported) to reuse a single stack frame. Watch for: missing/incorrect base case (infinite recursion), recomputation of overlapping subproblems (add memoization — that's dynamic programming), and depth limits.

**Check:** Why does `factorial` with no base case crash, and what's the fix?
