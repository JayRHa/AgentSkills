# Refactoring Catalog (Mechanics)

Each entry is a *behavior-preserving* transformation. Run tests after every numbered step where indicated. Examples are illustrative; language differs but mechanics are universal.

---

## §1 Extract Function

**When:** a fragment of code can be grouped under an intention-revealing name; long function; duplicated fragment; comment explaining a block.

**Mechanics:**
1. Create a new function named after *what it does* (the intent), not how.
2. Copy the extracted code into the new function.
3. Identify variables read by the fragment → pass as parameters. Identify variables assigned and used after → return them.
4. Replace the original fragment with a call to the new function.
5. Run tests.
6. Look for other places with the same/similar code; replace them with the call too (this removes duplication).

```js
// before
function printOwing(invoice) {
  printBanner();
  let outstanding = 0;
  for (const o of invoice.orders) outstanding += o.amount;
  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${outstanding}`);
}

// after
function printOwing(invoice) {
  printBanner();
  const outstanding = calculateOutstanding(invoice);
  printDetails(invoice, outstanding);
}
function calculateOutstanding(invoice) {
  return invoice.orders.reduce((sum, o) => sum + o.amount, 0);
}
function printDetails(invoice, outstanding) {
  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${outstanding}`);
}
```

---

## §2 Extract Variable (Explaining Variable)

**When:** a complex expression is hard to read.

**Mechanics:**
1. Ensure the expression has no side effects.
2. Declare an immutable variable named for the expression's meaning, set to the expression.
3. Replace the expression with the variable.
4. Run tests.

```js
// before
return order.quantity * order.itemPrice -
  Math.max(0, order.quantity - 500) * order.itemPrice * 0.05 +
  Math.min(order.quantity * order.itemPrice * 0.1, 100);

// after
const basePrice = order.quantity * order.itemPrice;
const quantityDiscount = Math.max(0, order.quantity - 500) * order.itemPrice * 0.05;
const shipping = Math.min(basePrice * 0.1, 100);
return basePrice - quantityDiscount + shipping;
```

---

## §3 Inline Function / Inline Variable

**When:** a function body is as clear as its name; an indirection adds no value; a variable just mirrors an expression.

**Mechanics (function):**
1. Verify it's not polymorphic / overridden.
2. Find all callers.
3. Replace each call with the function body.
4. Run tests after each replacement.
5. Delete the function.

```js
// before
function rating(driver) { return moreThanFiveDeliveries(driver) ? 2 : 1; }
function moreThanFiveDeliveries(driver) { return driver.deliveries > 5; }
// after
function rating(driver) { return driver.deliveries > 5 ? 2 : 1; }
```

---

## §4 Replace Nested Conditional with Guard Clauses

**When:** deep nesting; one path is the "normal" path buried inside `else`s.

**Mechanics:**
1. Pick the outermost condition that handles an edge/early case.
2. Convert it to a guard clause that returns/throws early.
3. Run tests.
4. Repeat for the next condition. Flatten until the main path is at top indentation.

```js
// before
function pay(employee) {
  let result;
  if (employee.isSeparated) result = { amount: 0, reason: 'separated' };
  else {
    if (employee.isRetired) result = { amount: 0, reason: 'retired' };
    else result = computePay(employee);
  }
  return result;
}
// after
function pay(employee) {
  if (employee.isSeparated) return { amount: 0, reason: 'separated' };
  if (employee.isRetired)   return { amount: 0, reason: 'retired' };
  return computePay(employee);
}
```

---

## §5 Rename (Variable / Function / Class)

**When:** a name doesn't reveal intent.

**Mechanics:**
1. Prefer the IDE/automated rename — it updates all references safely.
2. If manual: find ALL references (including strings, reflection, serialized forms, public API docs).
3. For a *published/public* name, this is a breaking change — keep the old name as a thin deprecated alias, or do it as an explicit API change (not a pure refactor).
4. Run tests.

---

## §6 Introduce Parameter Object

**When:** a group of parameters travels together repeatedly (data clump).

**Mechanics:**
1. Define a class/struct/record for the group.
2. Add the new parameter to the function (keep old params temporarily).
3. Update callers to pass the object; route fields through.
4. Replace internal uses of the loose params with object fields.
5. Remove the old loose parameters. Run tests after each call site migration.

```js
// before
function amountInvoiced(startDate, endDate) { /* ... */ }
function amountReceived(startDate, endDate) { /* ... */ }
// after
class DateRange { constructor(start, end){ this.start=start; this.end=end; } }
function amountInvoiced(range) { /* uses range.start / range.end */ }
function amountReceived(range) { /* ... */ }
```

---

## §7 Remove Duplication (Consolidate)

**When:** identical/near-identical logic in multiple spots.

**Mechanics:**
1. Confirm the duplicates truly represent the *same concept that will change together* (not coincidental similarity).
2. Extract the common code (§1). Parameterize the differences.
3. Replace each duplicate with a call.
4. Run tests after each replacement.

> Caution: Two snippets that look alike but change for different reasons should stay separate. Premature DRY creates the wrong coupling.

---

## §8 Replace Conditional with Polymorphism

**When:** the same `switch`/`if` on a type code appears in multiple methods.

**Mechanics:**
1. Create a subclass/strategy per type-code branch.
2. Create a factory that returns the right instance for the type code.
3. Move one conditional's branches into overriding methods on each subclass.
4. Replace the conditional with a polymorphic call.
5. Run tests; repeat per conditional.

```js
// before
function speed(bird) {
  switch (bird.type) {
    case 'European': return 35;
    case 'African':  return 40 - bird.load * 2;
    case 'Norwegian':return bird.isNailed ? 0 : 10 + bird.voltage;
  }
}
// after: Bird subclasses each implement speed()
class EuropeanSwallow { speed() { return 35; } }
class AfricanSwallow  { speed() { return 40 - this.load * 2; } }
class NorwegianBlue   { speed() { return this.isNailed ? 0 : 10 + this.voltage; } }
```

---

## §9 Extract Class / Move Method

**When:** a class has subsets of data+methods that belong together (large class, divergent change).

**Mechanics:**
1. Decide which responsibility to split out.
2. Create the new class; the old class holds a reference to it.
3. Move fields one at a time (Move Field), then methods (Move Method). Run tests after each move.
4. Decide whether the new class is exposed or hidden behind the original.

```js
// before: Person owns phone formatting
class Person { areaCode; number;
  telephoneNumber() { return `(${this.areaCode}) ${this.number}`; } }
// after
class TelephoneNumber { areaCode; number;
  toString() { return `(${this.areaCode}) ${this.number}`; } }
class Person { telephone = new TelephoneNumber();
  telephoneNumber() { return this.telephone.toString(); } }
```

---

## Cross-cutting checklist for every refactoring

- [ ] Tests were green before I started.
- [ ] I took the smallest step possible.
- [ ] I ran tests immediately after.
- [ ] No public/exported signature changed (or it's an intentional, separately-noted API change).
- [ ] No behavior, output, or side effect changed.
- [ ] Commit message starts with `refactor:` and names the transformation.
