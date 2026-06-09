# Worked Example: From Brief to Draft

This shows the full pipeline for one post so you can see the skill in action.

## 1. Brief
- Topic: speeding up a slow CI pipeline.
- Reader: backend engineers who own their team's CI, intermediate.
- Single takeaway: most CI slowness is wasted setup work, not test runtime — cache and parallelize first.
- Type: deep dive ("how we did it").
- Length: ~1,200 words. Platform: dev.to.

## 2. Headline options
1. How We Cut Our CI Pipeline From 22 Minutes to 4
2. Your CI Is Slow Because of Setup, Not Tests
3. 3 Changes That Quartered Our Build Time

**Chosen:** "How We Cut Our CI Pipeline From 22 Minutes to 4" — specific, numbers, benefit.

**Meta:** "The three changes that took our GitHub Actions pipeline from 22 to 4 minutes — dependency caching, test sharding, and what to measure first."

## 3. Outline
- Hook: the daily cost of a 22-minute pipeline.
- Where the time actually went (measure first).
- Change 1: cache dependencies.
- Change 2: shard the tests.
- Change 3: stop rebuilding the Docker image every job.
- Results with numbers.
- Takeaway.

## 4. Draft

### How We Cut Our CI Pipeline From 22 Minutes to 4

Our test suite runs in 90 seconds on a laptop. So why did every pull request sit in CI for 22 minutes? That gap was costing the team roughly 15 engineer-hours a week in context-switching alone. Here are the three changes that closed it — and the one measurement that made them obvious.

**First, we measured instead of guessing.** We added timing to each CI step and found the truth: tests were 90 seconds. The other 20 minutes were `npm install`, building a Docker image, and a single job running everything in series. The lesson that shaped everything else: *CI slowness is usually setup, not tests.*

#### Change 1: Cache dependencies
Every run reinstalled 1,100 packages from scratch — about 6 minutes. Caching the dependency directory keyed on the lockfile hash dropped that to 20 seconds on a cache hit.

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: npm-${{ hashFiles('package-lock.json') }}
```
Result: ~6 min → ~20 s on warm cache.

#### Change 2: Shard the tests
One runner executed all tests serially. We split them across four parallel jobs.

```yaml
strategy:
  matrix:
    shard: [1, 2, 3, 4]
steps:
  - run: npm test -- --shard=${{ matrix.shard }}/4
```
Wall-clock test time fell roughly 4x because the jobs run at once.

#### Change 3: Build the image once
Four jobs were each rebuilding the same Docker image — 4 minutes, four times over. We built it once in a setup job, pushed to the registry cache, and pulled it in the others. That reclaimed the redundant builds entirely.

#### The results
| Stage | Before | After |
|---|---|---|
| Install | 6:00 | 0:20 |
| Image build | 4:00 (×4) | 1:30 (×1) |
| Tests | 8:00 serial | 2:00 sharded |
| **Total** | **22:00** | **4:10** |

#### Takeaway
Before optimizing CI, add timing to every step — you'll almost certainly find the cost is setup, not your tests. Then attack it in this order: cache dependencies, parallelize, and stop repeating work across jobs. Start with the measurement; it tells you which of the three to do first.

---

## 5. Why this works
- Hook = surprising-number + question, with an explicit payoff bridge.
- Each H2 is one change with code and a measured result.
- The takeaway is an ordered, repeatable action — not "hope this helps."
- Every claim has a number.
