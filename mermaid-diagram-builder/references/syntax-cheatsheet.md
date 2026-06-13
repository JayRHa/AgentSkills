# Mermaid Syntax Cheatsheet

Dense, copy-paste-ready syntax. Header keyword must be the first non-comment line. Comments use `%% ...`.

## Flowchart
```mermaid
flowchart LR
    %% directions: TD/TB (top-down), BT, LR, RL
    Start([Start]) --> Step[Do work]
    Step --> Q{OK?}
    Q -- Yes --> Done([Done])
    Q -- No --> Fix[Retry] --> Step
    DB[(Database)]
    Step -.reads.-> DB
    subgraph Service A
        Step
        Fix
    end
```
Edges: `-->` arrow, `---` line, `-.->` dotted, `==>` thick, `--text-->` labeled, `--o` circle end, `--x` cross end. Multiple targets: `A --> B & C`. Chain: `A --> B --> C`.
Node shapes: `[rect]`, `(rounded)`, `([stadium])`, `[[subroutine]]`, `[(cylinder)]`, `((circle))`, `>asymmetric]`, `{rhombus}`, `{{hexagon}}`, `[/parallelogram/]`, `[\\trapezoid\\]`.
Quote labels with specials: `A["Save (draft) #amp; exit"]`. Line break: `A["Line1<br/>Line2"]`.

## Sequence
```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant W as Web
    participant A as Auth
    U->>W: Submit form
    activate W
    W->>A: POST /login
    alt valid credentials
        A-->>W: 200 + token
        W-->>U: Redirect
    else invalid
        A-->>W: 401
        W-->>U: Show error
    end
    deactivate W
    Note over U,W: optional commentary
    loop every 5 min
        W->>A: refresh token
    end
```
Arrows: `->` line, `-->` dotted line, `->>` solid arrowhead (sync), `-->>` dotted arrowhead (response), `-x` lost, `-)` async open arrow. Blocks: `alt/else`, `opt`, `loop`, `par/and`, `critical/option`, `break`, `rect rgb(...)` for background.

## Entity Relationship
```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    PRODUCT ||--o{ LINE_ITEM : "appears in"
    CUSTOMER {
        int id PK
        string email UK
        string name
    }
    ORDER {
        int id PK
        int customer_id FK
        datetime created_at
    }
```
Cardinality (left--right): `|o` zero-or-one, `||` exactly-one, `}o` zero-or-many, `}|` one-or-many. `--` identifying (solid), `..` non-identifying (dashed). Keys: `PK`, `FK`, `UK`.

## Class
```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound() void
    }
    class Dog {
        +fetch() void
    }
    Animal <|-- Dog
    Dog "1" *-- "1" Collar : has
    interface Pet
    Pet <|.. Dog
```
Arrows: `<|--` inherit, `*--` composition, `o--` aggregation, `-->` association, `..>` dependency, `..|>` realize. Visibility: `+ - # ~`. Generics: `List~int~`. Annotations: `<<interface>>`, `<<abstract>>`, `<<enumeration>>`.

## State
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Running : start
    Running --> Paused : pause
    Paused --> Running : resume
    Running --> [*] : finish
    state Running {
        [*] --> Processing
        Processing --> Waiting
        Waiting --> Processing
    }
    state choose <<choice>>
    Idle --> choose
    choose --> Running : if ready
    choose --> Idle : else
```
Special: `[*]` start/end, `<<choice>>`, `<<fork>>`, `<<join>>`, `--` separates parallel regions, `note right of X: ...`.

## Gantt
```mermaid
gantt
    title Project Roadmap
    dateFormat YYYY-MM-DD
    axisFormat %m/%d
    section Design
        Research      :done,    r1, 2026-01-01, 5d
        Wireframes    :active,  w1, after r1, 7d
    section Build
        API           :crit,    a1, after w1, 10d
        Launch        :milestone, m1, after a1, 0d
```
States: `done`, `active`, `crit`. `:milestone,` for points. Dependencies via `after <id>`.

## C4 Context
```mermaid
C4Context
    title System Context — Payments
    Person(customer, "Customer", "Buys products")
    System(shop, "Shop", "E-commerce platform")
    System_Ext(stripe, "Stripe", "Payment processor")
    Rel(customer, shop, "Browses & buys", "HTTPS")
    Rel(shop, stripe, "Charges card", "REST/HTTPS")
```

## Architecture-beta
```mermaid
architecture-beta
    group cloud(cloud)[Cloud]
    service web(server)[Web] in cloud
    service api(server)[API] in cloud
    service db(database)[DB] in cloud
    service q(disk)[Queue] in cloud
    web:R --> L:api
    api:R --> L:db
    api:B --> T:q
```

## User Journey
```mermaid
journey
    title Onboarding
    section Sign up
        Visit site: 4: User
        Create account: 3: User
    section First use
        Import data: 2: User, System
        See dashboard: 5: User
```

## Git Graph
```mermaid
gitGraph
    commit
    branch develop
    checkout develop
    commit
    checkout main
    merge develop tag: "v1.0"
```

## Config & theming directive
Put at the very top to control theme/layout:
```
%%{init: {'theme':'neutral', 'flowchart':{'curve':'basis'}}}%%
flowchart TD
    A --> B
```
Themes: `default`, `neutral`, `dark`, `forest`, `base`. With `base` you can set `themeVariables`.

## Styling nodes
```mermaid
flowchart TD
    A[Critical] --> B[Normal]
    classDef danger fill:#fee,stroke:#c00,color:#900;
    class A danger;
    style B fill:#eef,stroke:#06c;
```
Links can be styled with `linkStyle 0 stroke:#f66,stroke-width:2px;` (index = order of definition).
