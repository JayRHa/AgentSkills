# Characterization Tests (Pinning Legacy Behavior)

When the code you must refactor has no tests, you cannot safely change its structure — you have nothing telling you whether behavior stayed the same. **Characterization tests** capture what the code *currently does* (warts included) so you can refactor with confidence. They document actual behavior, not intended behavior.

## When to use

- Refactoring legacy code with little/no coverage.
- Working with code whose correct behavior is unclear but must be preserved.
- Before extracting from or restructuring a function you don't fully understand.

## Workflow

1. **Find a seam.** Locate the smallest unit you can call directly (a function, a class method). If it's tangled with I/O or globals, find the nearest pure-ish entry point, or introduce a thin seam (e.g. inject a dependency) as its *own* tiny, tested step first.

2. **Write a test that calls it and asserts on whatever you can observe** — return value, thrown error, mutated argument, recorded side effect.

3. **Don't guess the expected value.** Assert something obviously wrong, run the test, and let it tell you the real output. Then paste the real output as the expectation. The test now *characterizes* current behavior.

```python
# Step A: deliberately wrong, just to learn the output
def test_legacy_discount():
    assert apply_discount(120, 'GOLD') == 'WRONG'
# Run -> failure message reveals: got 96.0

# Step B: pin it
def test_legacy_discount():
    assert apply_discount(120, 'GOLD') == 96.0
```

4. **Cover the branches.** Add cases for each path you can reach: edge values, empty/None inputs, error conditions, boundary numbers. Aim to exercise every branch you intend to touch. Use a coverage tool to confirm the target lines are covered.

5. **Capture quirks deliberately.** If the code does something odd (returns `-1` on error, rounds strangely), pin that too. You are preserving behavior, not improving it. If a quirk is actually a bug, note it; fix it in a separate commit *after* refactoring.

6. **Now refactor** following the catalog. The characterization tests are your safety net. They should stay green through every step.

## Techniques for hard-to-test code

| Obstacle | Technique |
|---|---|
| Hidden global state | Save/restore it in setup/teardown; or inject it |
| Time / randomness | Pass a clock/RNG in; or freeze/seed it in the test |
| Network / DB / filesystem | Wrap behind a tiny interface and pass a fake; or use a local fixture |
| Output via print/log | Capture stdout/log; assert on captured text |
| Huge object output | Snapshot/approval test: serialize result, store golden file, compare |

## Approval (golden master) testing

For code with large or complex output and many input combinations:

1. Generate a broad set of representative inputs.
2. Run the code, serialize each output to a stable text form.
3. Save these as the **approved** golden file(s).
4. After each refactoring step, regenerate and diff against the approved file. Any diff = behavior changed = revert.

This is powerful for legacy code where writing individual assertions is impractical.

## Exit criteria

You have enough characterization when:
- Every code path you plan to modify is exercised by at least one test.
- The tests fail if you intentionally break the logic (mutation sanity check).
- You can run them fast enough to use as an inner refactoring loop.
