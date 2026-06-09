# Code Smell Catalog

A *smell* is a surface symptom that often (not always) points to a deeper problem. Smells are heuristics, not rules — confirm before acting.

## Bloaters

| Smell | Detection signal | Likely refactoring |
|---|---|---|
| **Long Function** | More than ~1 screen; multiple responsibilities; many local variables; comments dividing sections | Extract Function; Replace Temp with Query |
| **Large Class / God Object** | Many fields/methods; mixes unrelated concerns; "Manager"/"Util" in name | Extract Class; Move Method/Field |
| **Long Parameter List** | 4+ params; same group of params passed together repeatedly | Introduce Parameter Object; Preserve Whole Object |
| **Primitive Obsession** | Strings/ints standing in for domain concepts (e.g. `String currency`) | Replace Primitive with Object; Introduce Parameter Object |
| **Data Clumps** | The same 3 fields appear together everywhere | Extract Class; Introduce Parameter Object |

## Change Preventers

| Smell | Detection signal | Likely refactoring |
|---|---|---|
| **Divergent Change** | One module changes for many unrelated reasons | Extract Class (split by reason to change) |
| **Shotgun Surgery** | One conceptual change forces edits in many files | Move Method/Field to consolidate; Inline Class |

## Couplers

| Smell | Detection signal | Likely refactoring |
|---|---|---|
| **Feature Envy** | A method uses another object's data more than its own | Move Method; Extract then Move Function |
| **Inappropriate Intimacy** | Two classes reach into each other's internals | Move Method/Field; Hide Delegate |
| **Message Chains** | `a.getB().getC().getD()` | Hide Delegate; Extract Function |

## Dispensables

| Smell | Detection signal | Likely refactoring |
|---|---|---|
| **Duplicated Code** | Identical or near-identical logic in 2+ places | Extract Function; Pull Up Method |
| **Dead Code** | Unreferenced functions/branches/variables | Delete it (verify with usage search) |
| **Speculative Generality** | Abstractions/hooks with one or zero users | Inline Class/Function; Collapse Hierarchy |
| **Comments (as deodorant)** | Comments explaining *what* convoluted code does | Extract Function with intention-revealing name; Rename |

## Obscurers (readability)

| Smell | Detection signal | Likely refactoring |
|---|---|---|
| **Mysterious Name** | `data2`, `tmp`, `handle()`, ambiguous abbreviations | Rename Variable/Function |
| **Deep Nesting** | 3+ levels of indentation; arrow-shaped code | Replace Nested Conditional with Guard Clauses; Extract Function |
| **Complex Conditional** | Long boolean expressions; nested ternaries | Decompose Conditional; Extract Variable |
| **Mutable Sprawl** | Temp variables reassigned/accumulated across a long body | Split Variable; Replace Temp with Query |

## Severity / priority heuristic

Fix in roughly this order, because each unlocks the next:

1. **Mysterious names** — cheap, immediately improves comprehension.
2. **Deep nesting / guard clauses** — flattens control flow so you can read it.
3. **Long function → extract** — once readable, carve out cohesive pieces.
4. **Duplication** — now that pieces are named, deduplicate.
5. **Class/structure smells** — the larger, riskier moves, done last with the most test cover.

Rule of thumb: if a smell isn't in code you're about to touch and isn't actively hurting, leave it. Refactor opportunistically, not exhaustively.
