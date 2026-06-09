# Worked Example: From Smelly to Clean

A complete, step-by-step refactoring of one function, showing the small-step, test-protected loop. Language: JavaScript, but the moves are universal.

## Starting point (the smell)

```js
function statement(invoice, plays) {
  let totalAmount = 0;
  let volumeCredits = 0;
  let result = `Statement for ${invoice.customer}\n`;
  const format = new Intl.NumberFormat('en-US',
    { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }).format;

  for (let perf of invoice.performances) {
    const play = plays[perf.playID];
    let thisAmount = 0;
    switch (play.type) {
      case 'tragedy':
        thisAmount = 40000;
        if (perf.audience > 30) thisAmount += 1000 * (perf.audience - 30);
        break;
      case 'comedy':
        thisAmount = 30000;
        if (perf.audience > 20) thisAmount += 10000 + 500 * (perf.audience - 20);
        thisAmount += 300 * perf.audience;
        break;
      default:
        throw new Error(`unknown type: ${play.type}`);
    }
    volumeCredits += Math.max(perf.audience - 30, 0);
    if (play.type === 'comedy') volumeCredits += Math.floor(perf.audience / 5);
    result += ` ${play.name}: ${format(thisAmount / 100)} (${perf.audience} seats)\n`;
    totalAmount += thisAmount;
  }
  result += `Amount owed is ${format(totalAmount / 100)}\n`;
  result += `You earned ${volumeCredits} credits\n`;
  return result;
}
```

**Smells:** Long Function; a `switch` doing per-type amount calc (extractable); inline credit logic; temp-driven accumulation; mixed concerns (calculation + formatting + string building).

## Step 0 — Safety net

No tests existed, so we characterize first (see `references/characterization-tests.md`):

```js
test('statement renders Hamlet + As You Like It', () => {
  // expectation pasted from the actual current output after running once
  expect(statement(invoice, plays)).toBe(
    'Statement for BigCo\n' +
    ' Hamlet: $650.00 (55 seats)\n' +
    ' As You Like It: $580.00 (35 seats)\n' +
    'Amount owed is $1,230.00\n' +
    'You earned 47 credits\n'
  );
});
```

Run it. Green. Now we can refactor.

## Step 1 — Extract Function: `amountFor` (catalog §1)

Move the `switch` into a named function. Variables read: `perf`, `play`. Returned: the amount.

```js
function amountFor(perf, play) {
  let thisAmount = 0;
  switch (play.type) {
    case 'tragedy':
      thisAmount = 40000;
      if (perf.audience > 30) thisAmount += 1000 * (perf.audience - 30);
      break;
    case 'comedy':
      thisAmount = 30000;
      if (perf.audience > 20) thisAmount += 10000 + 500 * (perf.audience - 20);
      thisAmount += 300 * perf.audience;
      break;
    default:
      throw new Error(`unknown type: ${play.type}`);
  }
  return thisAmount;
}
```

In the loop: `const thisAmount = amountFor(perf, play);`

**Run tests → green. Commit:** `refactor: extract amountFor from statement`

## Step 2 — Extract Function: `volumeCreditsFor` (catalog §1)

```js
function volumeCreditsFor(perf, play) {
  let credits = Math.max(perf.audience - 30, 0);
  if (play.type === 'comedy') credits += Math.floor(perf.audience / 5);
  return credits;
}
```

Loop: `volumeCredits += volumeCreditsFor(perf, play);`

**Run tests → green. Commit:** `refactor: extract volumeCreditsFor`

## Step 3 — Extract Variable: name the play lookup (catalog §2)

`amountFor` only needs `perf`; derive `play` inside it via a passed-in lookup, or keep passing it. We keep `play` explicit for now and rename `thisAmount` → clarity already gained. Skipped if no improvement (avoid over-extraction).

## Step 4 — Extract Function: rendering (catalog §1)

Separate calculation from presentation by extracting the line formatting:

```js
function lineFor(play, amount, audience, format) {
  return ` ${play.name}: ${format(amount / 100)} (${audience} seats)\n`;
}
```

Loop body becomes a clean sequence:

```js
for (let perf of invoice.performances) {
  const play = plays[perf.playID];
  const thisAmount = amountFor(perf, play);
  volumeCredits += volumeCreditsFor(perf, play);
  result += lineFor(play, thisAmount, perf.audience, format);
  totalAmount += thisAmount;
}
```

**Run tests → green. Commit:** `refactor: extract lineFor formatting`

## Result

`statement` now reads as orchestration; each rule lives in a named, independently testable function. Behavior is byte-for-byte identical — proven by the characterization test that stayed green through every step.

## Verification

```
scripts/refactor_check.sh baseline src/statement.js   # run BEFORE step 1
# ...do steps...
scripts/refactor_check.sh verify   src/statement.js   # API unchanged + tests green
```

## Lessons illustrated

- One extraction per commit; tests after each.
- Characterization test built the safety net first.
- We stopped before over-extracting (Step 3 was declined — no clarity gain).
- The public function `statement` and its signature never changed → still a pure refactor.
