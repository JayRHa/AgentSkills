# Worked Example: Splitting a Checkout Epic

**Epic:** "As a shopper, I want to check out and pay so that I can buy my cart."

Too big for one sprint. Split by **workflow steps** + **happy/unhappy path**:

### Story 1 — Address (happy path)
> As a shopper, I want to enter a shipping address so that my order can be delivered.
```gherkin
Scenario: Valid address accepted
  Given a cart with 1+ items
  When I enter a complete, valid shipping address
  Then I can proceed to the shipping-method step
```

### Story 2 — Shipping method
> As a shopper, I want to choose a shipping method so that I control cost vs. speed.
```gherkin
Scenario: Method updates total
  Given a valid address
  When I select "Express (+$9)"
  Then the order total increases by $9
```

### Story 3 — Pay (happy path)
> As a shopper, I want to pay by card so that I can complete my purchase.
```gherkin
Scenario: Successful payment
  Given a valid card and a confirmed order
  When I submit payment
  Then the order is created and I see a confirmation number
```

### Story 4 — Declined payment (unhappy path)
> As a shopper, I want clear feedback when payment fails so that I can fix it and retry.
```gherkin
Scenario: Card declined
  Given a card that the processor declines
  When I submit payment
  Then I see "Payment declined — try another card" and the cart is preserved
```

**Why this works:** each story is a vertical slice (UI + logic + data), independently
demoable, and individually valuable. Stories 1–3 form a shippable MVP; story 4 hardens it.
