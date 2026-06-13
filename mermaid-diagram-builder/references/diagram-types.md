# Mermaid Diagram Type Selection Guide

Use this to map the user's intent to the right diagram. Each entry lists what it models, the header keyword, when to use it, and when to avoid it.

---

## Flowchart (`flowchart` / `graph`)
**Models:** processes, decisions, control flow, pipelines, decision trees.
**Header:** `flowchart TD` (also `TB`, `BT`, `LR`, `RL`). Legacy alias: `graph`.
**Use when:** the user describes steps, branches ("if/else", "on success/failure"), loops, or a workflow.
**Avoid when:** the focus is time-ordered messages between participants (use Sequence) or pure data structure (use ER/Class).
**Node shapes & meaning:**
| Shape | Syntax | Convention |
|---|---|---|
| Rounded / terminator | `A([Start])` | start / end |
| Rectangle | `A[Do thing]` | action / process step |
| Diamond | `A{Decision?}` | branch |
| Subroutine | `A[[Process]]` | reusable sub-process |
| Cylinder | `A[(DB)]` | datastore |
| Circle | `A((Node))` | connector / hub |
| Parallelogram | `A[/Input/]` | input / output |
| Hexagon | `A{{Prep}}` | preparation |

---

## Sequence Diagram (`sequenceDiagram`)
**Models:** interactions between participants ordered in time (API calls, protocols, message passing).
**Header:** `sequenceDiagram`.
**Use when:** the user says "request/response", "calls", "who sends what to whom", auth handshakes, distributed flows.
**Avoid when:** there is branching logic without participants (use Flowchart) or no temporal ordering.
**Key syntax:** `participant A`, `actor U`, `A->>B: sync call`, `B-->>A: response (dashed)`, `A-)B: async`, `activate`/`deactivate`, `alt`/`else`/`opt`/`loop`/`par`, `Note over A,B: text`.

---

## Entity Relationship (`erDiagram`)
**Models:** data models, database schemas, table relationships and cardinality.
**Header:** `erDiagram`.
**Use when:** the user says "schema", "tables", "foreign keys", "one-to-many", "data model".
**Avoid when:** modeling object behavior/methods (use Class) or runtime flow.
**Cardinality crow's-foot syntax:** `||--o{` (one to zero-or-many), `||--||` (one to one), `}o--o{` (many to many), `||--|{` (one to one-or-many). Left/right symbols: `|o` zero-or-one, `||` exactly-one, `}o` zero-or-many, `}|` one-or-many. Use `..` for non-identifying (dashed) relationships.

---

## Class Diagram (`classDiagram`)
**Models:** OOP structure — classes, attributes, methods, inheritance, composition.
**Header:** `classDiagram`.
**Use when:** "classes", "inheritance", "interfaces", "methods/attributes", domain model in code.
**Avoid when:** modeling tables/cardinality (use ER) or a process (use Flowchart).
**Relationship arrows:** `<|--` inheritance, `*--` composition, `o--` aggregation, `-->` association, `..>` dependency, `..|>` realization. Visibility: `+` public, `-` private, `#` protected, `~` package.

---

## State Diagram (`stateDiagram-v2`)
**Models:** finite state machines, lifecycles, status transitions.
**Header:** `stateDiagram-v2` (prefer v2 always).
**Use when:** "states", "status", "lifecycle", "transitions", "can only move from X to Y".
**Avoid when:** steps don't represent persistent states (use Flowchart).
**Key syntax:** `[*] --> Idle` (start), `Idle --> Running : start`, `Running --> [*]` (end), composite states with `state Name { ... }`, `<<choice>>`, `<<fork>>`, `<<join>>`, parallel regions with `--`.

---

## Gantt (`gantt`)
**Models:** project schedules, timelines, milestones, task dependencies.
**Header:** `gantt`.
**Use when:** "timeline", "schedule", "project plan", "roadmap with dates".
**Avoid when:** there are no dates/durations.
**Key syntax:** `dateFormat YYYY-MM-DD`, `title ...`, `section Name`, `Task :id, 2026-01-01, 7d`, dependencies via `after id`, states `:done,`, `:active,`, `:crit,`, milestones `:milestone,`.

---

## C4 / Architecture
Two options depending on Mermaid version and intent:

### C4 model (`C4Context`, `C4Container`, `C4Component`)
**Models:** software architecture at C4 abstraction levels (system context, containers, components).
**Use when:** the user explicitly wants C4, system boundaries, external systems, personas.
**Key syntax:** `Person(alias, "Label", "desc")`, `System(alias, ...)`, `Container(alias, "Name", "Tech", "desc")`, `Rel(from, to, "verb", "protocol")`, `System_Boundary(alias, "Name") { ... }`.

### Architecture-beta (`architecture-beta`)
**Models:** cloud/service architecture with groups, services, and icon edges.
**Use when:** drawing services, queues, databases grouped by environment/cloud.
**Key syntax:** `group api(cloud)[API]`, `service db(database)[DB] in api`, `db:L -- R:server`.
Note: `architecture-beta` is newer; if a target renderer is old, prefer C4 or a styled flowchart with subgraphs.

---

## User Journey (`journey`)
**Models:** a user's experience across steps with sentiment scores (1-5).
**Use when:** UX journeys, CX mapping.
**Key syntax:** `title ...`, `section Phase`, `Task: 5: Actor1, Actor2`.

---

## Git Graph (`gitGraph`)
**Models:** branch/commit/merge history.
**Use when:** explaining a branching strategy or release flow.
**Key syntax:** `commit`, `branch dev`, `checkout dev`, `merge main`, `commit tag: "v1.0"`.

---

## Pie / Quadrant / Mindmap / Timeline
- `pie` — share-of-total. Avoid for >6 slices.
- `quadrantChart` — 2x2 prioritization (effort vs impact).
- `mindmap` — brainstorm hierarchy.
- `timeline` — chronological events without dependencies (simpler than gantt).

## Decision shortcut
1. Time-ordered messages between named actors? -> **Sequence**.
2. Branching steps / a process? -> **Flowchart**.
3. Data tables and relationships? -> **ER**.
4. Code classes and inheritance? -> **Class**.
5. A thing that is in exactly one state at a time? -> **State**.
6. Dates and durations? -> **Gantt**.
7. Boxes-and-boundaries of a system? -> **C4 / architecture-beta** (or styled flowchart with subgraphs).
