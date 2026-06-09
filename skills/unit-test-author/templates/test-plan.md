# Test Plan: <unit name>

Fill this in BEFORE writing tests. Delete rows that don't apply.

## Unit under test

- File / symbol: `path/to/file::Symbol`
- Public behavior (contract in one sentence):

## Contract

| Aspect | Detail |
|--------|--------|
| Inputs (type, valid range) | |
| Outputs (type, meaning) | |
| Errors/exceptions raised | |
| Side effects | |
| Dependencies (collaborators) | |

## Test double strategy

| Collaborator | Double (dummy/stub/spy/mock/fake) | Why |
|--------------|-----------------------------------|-----|
| | | |

Determinism to inject: [ ] clock  [ ] randomness  [ ] ids/uuids  [ ] network  [ ] filesystem

## Cases

| # | Case name | Input | Expected output / error | Edge category |
|---|-----------|-------|-------------------------|---------------|
| 1 | happy path | | | universal |
| 2 | empty input | | | collection |
| 3 | boundary min | | | number/string |
| 4 | boundary max | | | number/string |
| 5 | null/none | | | universal |
| 6 | invalid type | | raises | error |
| 7 | error path A | | raises <Type> | error |
| 8 | side effect once | | | state |
| 9 | idempotence | | | universal |

## Structure decision

- [ ] Table-driven / parametrized (≥3 input→output pairs share assertion logic)
- [ ] Individual named tests
- [ ] Property-based (invariant holds over input space): property = ___________

## Mutation sanity check (after writing)

For each core branch, name one mutation and the test that would catch it:

- Mutation: __________ → caught by test: __________
