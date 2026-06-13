# Root Cause Analysis Techniques

Use these in sequence: Five Whys to reach systemic depth, then the contributing-factors sweep to find everything the single-cause view misses. Optionally layer a causal map for complex multi-system incidents.

## 1. The Five Whys (driven to systemic depth)

Start from the **symptom** and ask "why?" repeatedly. Stop only when the answer names a fixable property of a system or process — never when it names a person.

### Worked example

- **Symptom:** Checkout API returned 500s for 40% of requests for 51 minutes.
- **Why?** The database CPU was saturated and queries timed out.
- **Why?** A new query introduced in the 14:02 deploy was missing an index and did full table scans under load.
- **Why?** The query regression was not caught before production.
- **Why?** CI runs only unit tests against a tiny seed dataset; it has no representative-load query analysis stage.
- **Why?** A load/EXPLAIN gate was deprioritized because it was assumed code review would catch slow queries.

**Root cause:** No automated pre-production detection of query-performance regressions; reliance on manual review for a class of problem humans are poor at catching.

### Rules for good Whys

- One cause may branch into multiple Whys — follow each branch.
- If a Why answer is "someone made a mistake", the real next Why is "why did the system let that mistake reach production / go undetected?"
- Stop at a systemic, actionable condition. "Engineer should have tested more" is NOT a stopping point — it is a signal you stopped too early.

## 2. Contributing-Factors Sweep

Root cause explains *why it happened at all*. Contributing factors explain *why it was this bad / this long / this hard to fix*. Sweep these categories explicitly:

| Category | Question to ask |
|----------|-----------------|
| Detection | How long until anyone/anything knew? Auto-detected or customer-reported? Were alerts late, missing, or noisy? |
| Alerting/thresholds | Were thresholds stale relative to current traffic/behavior? Did the right people get paged? |
| Latent risk | What pre-existing weakness was waiting to be triggered (missing index, no rollback, single point of failure)? |
| Change management | Was there a canary/gradual rollout? Automatic rollback? Change freeze awareness? |
| Runbooks/knowledge | Did responders have a playbook? Was tribal knowledge a bottleneck? |
| Tooling | Did dashboards/logs/access slow diagnosis? Could responders reproduce/see the problem? |
| Coordination | Clear incident commander? Comms to stakeholders? Handoffs across timezones? |
| Dependencies | Did an upstream/downstream service amplify or mask the issue? |

Every checked box that contributed should produce at least one action item.

## 3. Causal Mapping (for complex incidents)

When multiple systems interact, draw a cause→effect chain instead of a single linear Five Whys:

```
[stale alert threshold] --------------\
                                        v
[deploy w/ unindexed query] --> [DB CPU saturation] --> [API timeouts] --> [40% 500s]
          ^                                                   |
          |                                                   v
[no load test in CI]                             [no auto-rollback] --> [extended duration]
```

Each node with no upstream cause that is *fixable* is a root cause. Each node on the path that made it worse is a contributing factor. This view prevents the "one true cause" fallacy.

## 4. Distinguishing the four cause types

- **Symptom** — what was observed/measured (the 500s).
- **Trigger** — the proximate event that started this instance (the deploy).
- **Root cause** — the systemic condition that let a trigger cause an outage (no load gate; no auto-rollback). Fix this and the *class* of incident becomes unlikely.
- **Contributing factor** — anything that increased severity, duration, or difficulty (stale alert, missing runbook).

Fix triggers and you prevent *this* incident. Fix root causes and you prevent *this kind* of incident. Always aim for the latter.
