# Worked Example: "Checkout intermittently returns 500"

A full pass through the debug-detective workflow on a realistic bug.

## 1. Report / Symptom
`POST /checkout` returns HTTP 500 for *some* requests. Started after the Tuesday deploy. ~3% of checkouts affected.

Log excerpt:
```
Traceback (most recent call last):
  File "app/checkout.py", line 88, in calculate_total
    discount = customer.loyalty_tier.discount_rate
AttributeError: 'NoneType' object has no attribute 'loyalty_tier'
```

## 2. Environment
- prod, Python 3.11, web app behind load balancer (8 workers).
- Branch: `main` @ `9f2c1ab`. Bug absent before Tuesday's deploy.
- Not reproducible on a fresh local checkout with seeded data — *environment/data dependent*.

## 3. Reproduction
First attempts with a normal test customer always pass (0/50). Failure rate in prod ~3%, so a *specific* customer state triggers it. Hypothesis-driven repro:
- Suspect the `customer` is `None`. Found that the failing requests share customer ids that were **soft-deleted** between order start and checkout.
- Built a deterministic repro: create customer → start order → soft-delete customer → call checkout.
```sh
pytest tests/test_checkout.py::test_checkout_soft_deleted_customer -q
```
Now **100%** reproducible. Gate passed.

## 4. Isolation
- Last good point: order creation — `customer` is a valid object.
- First bad point: `calculate_total` — `get_customer(order.customer_id)` returns `None`.
- Minimized case: any order whose customer is soft-deleted before checkout.

## 5. Hypothesis Log
| # | Hypothesis | Prediction (if true) | Experiment | Result | Verdict |
|---|---|---|---|---|---|
| 1 | `customer` is None at line 88 | Logging `customer` before line 88 shows `None` | Add log, run repro | `customer=None` | CONFIRMED |
| 2 | DB row truly missing | Direct query returns 0 rows | `SELECT ... WHERE id=?` | 1 row, `deleted_at` set | REJECTED (row exists) |
| 3 | Default query scope filters soft-deleted rows | Querying without the scope returns the row | Bypass default scope | Row returned | CONFIRMED |

Unexplained-gap check: Why only after Tuesday? Tuesday's deploy added a global `deleted_at IS NULL` default scope to the customer repository. Before, soft-deleted customers were still returned. Gap closed.

## 6. Root Cause
- **Trigger:** customer soft-deleted between order start and checkout (rare → ~3%, hence "intermittent").
- **Root cause:** Tuesday's deploy introduced a default scope that hides soft-deleted customers, but `checkout` assumes the customer always resolves and never validates customer status. The crash is a *symptom*; the real defect is the missing precondition + the silent assumption that the lookup can't fail.
- **Contributing factor:** `get_customer` returns `None` rather than raising a typed, handled error.

## 7. Fix (root cause, not symptom)
Wrong (symptom only): `if customer is None: discount = 0` — hides a deleted-customer checkout, wrong business behavior.

Right:
1. `checkout` validates customer status up front and returns a clear 409/422 ("customer no longer active") instead of pricing a ghost.
2. `get_customer` for checkout explicitly decides soft-deleted policy rather than relying on an implicit global scope.

Searched for sibling occurrences of `customer.loyalty_tier` / unchecked `get_customer(...)` — found one more in `invoice.py`, fixed too.

## 8. Verification
- [x] Original repro passes (now returns 422, not 500).
- [x] Re-ran the soft-delete scenario across all 8-worker config — no 500s.
- [x] Added regression test `test_checkout_soft_deleted_customer` — fails on `9f2c1ab`, passes with fix.
- [x] Confirmed normal checkout still works (no behavior change for active customers).

## 9. Notes / Latent Issues
- The new default scope silently changed lookup semantics app-wide; audited other callers relying on the old behavior. Filed a follow-up to make repository scopes explicit at call sites.
