# Mermaid Example Gallery

Each example shows the **prompt** and the resulting renderable Mermaid. Copy any block into a ```mermaid fence.

---

## 1. Flowchart — Order fulfillment
**Prompt:** "Diagram order processing: receive order, check stock; if in stock ship it, otherwise backorder and notify the customer."
```mermaid
flowchart TD
    A([Order received]) --> B{In stock?}
    B -- Yes --> C[Reserve inventory]
    C --> D[Ship order]
    D --> E([Order complete])
    B -- No --> F[Create backorder]
    F --> G[Notify customer]
    G --> H([Await restock])
```

---

## 2. Sequence — OAuth login
**Prompt:** "Show the OAuth authorization-code flow between a browser, our app, and the identity provider."
```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant B as Browser
    participant App as App Server
    participant IdP as Identity Provider
    U->>B: Click "Log in"
    B->>IdP: Redirect to /authorize
    IdP-->>B: Login page
    U->>IdP: Enter credentials
    IdP-->>B: Redirect with auth code
    B->>App: GET /callback?code=...
    App->>IdP: POST /token (code + secret)
    IdP-->>App: access_token + id_token
    App-->>B: Set session cookie
    B-->>U: Logged in
```

---

## 3. ER — Blog schema
**Prompt:** "Model a blog: users write posts, posts have many comments, posts have tags (many-to-many)."
```mermaid
erDiagram
    USER ||--o{ POST : writes
    POST ||--o{ COMMENT : has
    USER ||--o{ COMMENT : authors
    POST }o--o{ TAG : tagged_with
    USER {
        int id PK
        string email UK
        string display_name
    }
    POST {
        int id PK
        int author_id FK
        string title
        text body
        datetime published_at
    }
    COMMENT {
        int id PK
        int post_id FK
        int author_id FK
        text body
    }
    TAG {
        int id PK
        string name UK
    }
```

---

## 4. Class — Payment domain
**Prompt:** "Class diagram for a payment system with an abstract PaymentMethod and Card/Wallet subclasses."
```mermaid
classDiagram
    class PaymentMethod {
        <<abstract>>
        +String id
        +charge(amount) Receipt
    }
    class Card {
        +String last4
        +int expMonth
        +charge(amount) Receipt
    }
    class Wallet {
        +String provider
        +charge(amount) Receipt
    }
    class Receipt {
        +String id
        +Decimal amount
        +DateTime at
    }
    PaymentMethod <|-- Card
    PaymentMethod <|-- Wallet
    PaymentMethod ..> Receipt : creates
```

---

## 5. State — Subscription lifecycle
**Prompt:** "State machine for a subscription: trialing, active, past_due, canceled."
```mermaid
stateDiagram-v2
    [*] --> Trialing
    Trialing --> Active : payment succeeds
    Trialing --> Canceled : trial expires
    Active --> PastDue : payment fails
    PastDue --> Active : retry succeeds
    PastDue --> Canceled : retries exhausted
    Active --> Canceled : user cancels
    Canceled --> [*]
```

---

## 6. Gantt — Quarter plan
**Prompt:** "Gantt for Q1: research 1 week, design 2 weeks, build 4 weeks, launch milestone."
```mermaid
gantt
    title Q1 Delivery Plan
    dateFormat YYYY-MM-DD
    axisFormat %m/%d
    section Discovery
        Research   :done,   r1, 2026-01-05, 5d
        Design     :active, d1, after r1, 10d
    section Delivery
        Build      :crit,   b1, after d1, 20d
        Launch     :milestone, m1, after b1, 0d
```

---

## 7. C4 Context — SaaS
**Prompt:** "C4 context diagram: customers and admins use our SaaS, which integrates Stripe and SendGrid."
```mermaid
C4Context
    title System Context — Acme SaaS
    Person(customer, "Customer", "Uses the product")
    Person(admin, "Admin", "Manages tenants")
    System(saas, "Acme SaaS", "Core application")
    System_Ext(stripe, "Stripe", "Billing")
    System_Ext(sendgrid, "SendGrid", "Transactional email")
    Rel(customer, saas, "Uses", "HTTPS")
    Rel(admin, saas, "Administers", "HTTPS")
    Rel(saas, stripe, "Bills via", "REST")
    Rel(saas, sendgrid, "Sends email via", "REST")
```

---

## 8. Architecture-beta — Web stack
**Prompt:** "Cloud architecture: load balancer to two API servers, shared Postgres and Redis."
```mermaid
architecture-beta
    group cloud(cloud)[Production]
    service lb(internet)[Load Balancer] in cloud
    service api1(server)[API 1] in cloud
    service api2(server)[API 2] in cloud
    service db(database)[Postgres] in cloud
    service cache(disk)[Redis] in cloud
    lb:B --> T:api1
    lb:B --> T:api2
    api1:R --> L:db
    api2:R --> L:db
    api1:B --> T:cache
    api2:B --> T:cache
```

---

## 9. Styled flowchart (architecture fallback) — Layered system
**Prompt:** "Show our layered architecture with frontend, backend, and data layers as boundaries."
```mermaid
flowchart TB
    subgraph FE[Frontend]
        SPA[React SPA]
    end
    subgraph BE[Backend]
        API[REST API]
        Worker[Job Worker]
    end
    subgraph DATA[Data]
        PG[(Postgres)]
        MQ[(Queue)]
    end
    SPA -->|HTTPS| API
    API --> PG
    API --> MQ
    MQ --> Worker
    Worker --> PG
    classDef store fill:#eef,stroke:#36c;
    class PG,MQ store;
```
