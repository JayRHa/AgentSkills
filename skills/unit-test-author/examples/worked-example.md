# Worked Example: From Source to Tests

This shows the full workflow on a small Python module so the structure is concrete. The same reasoning transfers to any language.

## 1. Source under test

```python
# pricing.py
from dataclasses import dataclass

class PromoError(Exception):
    pass

@dataclass
class Clock:
    now: callable  # injected for determinism

class Cart:
    def __init__(self, clock, rates):
        self._clock = clock
        self._rates = rates  # collaborator: currency rate provider
        self._items = []

    def add(self, name, price_usd, qty=1):
        if qty <= 0:
            raise ValueError("qty must be positive")
        self._items.append((name, price_usd, qty))

    def total(self, currency="USD", promo=None):
        subtotal = sum(p * q for _, p, q in self._items)
        if promo:
            subtotal = self._apply_promo(subtotal, promo)
        rate = self._rates.get_rate(currency)  # collaborator call
        return round(subtotal * rate, 2)

    def _apply_promo(self, amount, promo):
        if promo == "HALF":
            return amount * 0.5
        raise PromoError(f"unknown promo: {promo}")
```

## 2. Contract analysis

- **Inputs:** items (name, price, qty), currency string, optional promo.
- **Outputs:** rounded total in target currency.
- **Errors:** `ValueError` for non-positive qty; `PromoError` for unknown promo.
- **Side effects:** mutates internal item list on `add`.
- **Dependencies to control:** `rates.get_rate` (collaborator → stub), `clock` (injected; not used in total but present → dummy here).

## 3. Test plan (from edge-case checklist)

| Case | Why |
|------|-----|
| empty cart total | empty collection boundary |
| single item, USD | happy path, rate 1.0 |
| multiple items + qty | aggregation |
| currency conversion (EUR rate 0.9) | collaborator value consumed (stub) |
| HALF promo applied | promo branch |
| unknown promo raises PromoError | error path |
| add qty=0 raises ValueError | boundary + error path |
| add qty=-1 raises ValueError | negative boundary |
| rounding (0.1+0.2 style) | float precision |

## 4. Test double strategy

- `rates`: **stub** — the test cares about the returned rate value the SUT consumes.
- `clock`: **dummy** — required by constructor, unused by `total`.
- No mock needed: there is no interaction we must verify (no email/charge). If we DID need to confirm `get_rate` was called exactly once with the right currency, we'd use a **spy**.

## 5. Tests

```python
import pytest
from pricing import Cart, Clock, PromoError

class StubRates:
    def __init__(self, rate):
        self._rate = rate
        self.calls = []
    def get_rate(self, currency):
        self.calls.append(currency)
        return self._rate

@pytest.fixture
def clock():
    return Clock(now=lambda: 0)  # dummy; deterministic

def make_cart(rate=1.0, clock=None):
    return Cart(clock or Clock(now=lambda: 0), StubRates(rate))

def test_empty_cart_total_is_zero():
    assert make_cart().total() == 0.0

@pytest.mark.parametrize("items, expected", [
    pytest.param([("a", 10.0, 1)], 10.0, id="single"),
    pytest.param([("a", 10.0, 2)], 20.0, id="qty"),
    pytest.param([("a", 10.0, 1), ("b", 5.5, 2)], 21.0, id="multiple"),
])
def test_total_usd(items, expected):
    cart = make_cart()
    for name, price, qty in items:
        cart.add(name, price, qty)
    assert cart.total() == expected

def test_currency_conversion_uses_rate():
    rates = StubRates(0.9)
    cart = Cart(Clock(now=lambda: 0), rates)
    cart.add("a", 10.0, 1)
    assert cart.total("EUR") == 9.0
    assert rates.calls == ["EUR"]  # spy assertion on the boundary interaction

def test_half_promo_halves_subtotal():
    cart = make_cart()
    cart.add("a", 10.0, 1)
    assert cart.total(promo="HALF") == 5.0

def test_unknown_promo_raises():
    cart = make_cart()
    cart.add("a", 10.0, 1)
    with pytest.raises(PromoError, match="unknown promo: BOGUS"):
        cart.total(promo="BOGUS")

@pytest.mark.parametrize("qty", [0, -1])
def test_add_non_positive_qty_raises(qty):
    with pytest.raises(ValueError, match="positive"):
        make_cart().add("a", 10.0, qty)

def test_total_is_rounded_to_cents():
    cart = make_cart()
    cart.add("a", 0.1, 1)
    cart.add("b", 0.2, 1)
    assert cart.total() == 0.3  # 0.1+0.2 rounded to 2dp
```

## 6. Mutation sanity check

- Change `qty <= 0` to `qty < 0` → `test_add_non_positive_qty_raises[0]` fails. Good.
- Change `round(..., 2)` to no rounding → `test_total_is_rounded_to_cents` fails. Good.
- Remove the promo branch → `test_half_promo_halves_subtotal` fails. Good.

Every test fails for a real reason — the suite is meaningful, not tautological.
