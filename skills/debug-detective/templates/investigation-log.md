# Debug Investigation Log

> Fill this out as you go. The act of writing it forces the discipline.

## 1. Report / Symptom
- **Reported by / source:**
- **Date:**
- **Symptom (exact):** <error message, wrong output vs. expected, screenshot, exit code>
- **Severity / impact:**
- **Stack trace / logs:**
```
<paste here>
```

## 2. Environment
| Field | Value |
|---|---|
| OS / arch | |
| Runtime + version | |
| Key dependency versions | |
| Config / env vars | |
| Data / input | |
| Concurrency / load | |
| Branch / commit | |

## 3. Reproduction
- **Minimal repro command/steps:**
```
<command or steps>
```
- **Failure rate:** <100% | N out of M runs>
- **Repro confirmed?** [ ] yes  [ ] not yet (DO NOT FIX until yes)

## 4. Isolation
- **Last known-good layer/point:**
- **First known-bad layer/point:**
- **Minimized input/case:**

## 5. Hypothesis Log
| # | Hypothesis (falsifiable) | Prediction (if true) | Experiment | Result | Verdict |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

## 6. Root Cause
- **Trigger:** <what condition exercised it>
- **Root cause:** <the actual defect — explain the full causal chain>
- **Contributing factors:**
- **Why it wasn't caught earlier:**

## 7. Fix
- **Change made (root cause, not symptom):**
- **Files / commits:**
- **Sibling occurrences searched/fixed:** [ ] yes

## 8. Verification
- [ ] Original repro now passes.
- [ ] Re-run in original failing manner (loop/env/data) — passes.
- [ ] Regression test added (fails without fix, passes with fix).
- [ ] For flaky bugs: amplified loop run N times, zero failures (N = ____).
- **Evidence:**
```
<test output>
```

## 9. Notes / Latent Issues
-
