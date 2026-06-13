# GraphQL Design Checklist

## Schema Design
- [ ] Schema-first SDL is the source of truth; resolvers conform to it.
- [ ] Types model the domain; field names are camelCase, types PascalCase, enums SCREAMING_SNAKE.
- [ ] Nullability is intentional — non-null (`!`) only where the value truly always exists. A null in a non-null field nulls the parent.
- [ ] IDs use the `ID` scalar and are globally unique/opaque (consider base64(type:id) for Relay).
- [ ] Mutations follow `verbNoun` (`createOrder`) and take a single `input` object argument.
- [ ] Mutations return a payload type wrapping the affected entity plus a `userErrors`/`errors` list, not raw fields.
- [ ] Custom scalars (`DateTime`, `Decimal`, `URL`) defined and documented rather than overloading `String`.

## Pagination
- [ ] List fields use Relay Connections (`edges { node cursor } pageInfo { hasNextPage endCursor }`) or a documented simpler equivalent.
- [ ] `first`/`after` (and optionally `last`/`before`) with an enforced max page size.
- [ ] Connections support stable, deterministic ordering.

## Errors
- [ ] Distinguish protocol errors (top-level `errors`) from business/user errors (typed fields in mutation payloads).
- [ ] Error `extensions.code` is stable and machine-readable.
- [ ] No internal stack traces leaked in production; mask unexpected errors.

## Performance & Safety
- [ ] DataLoader (or equivalent) batching prevents N+1 resolver queries.
- [ ] Query depth limit enforced.
- [ ] Query complexity/cost analysis enforced with a max budget.
- [ ] Persisted queries / allowlist for public high-traffic clients.
- [ ] Timeouts on resolvers; pagination prevents unbounded lists.
- [ ] Introspection disabled or restricted in production if the API is private.

## Evolution
- [ ] Additive changes preferred; never remove/rename fields without deprecation.
- [ ] Use `@deprecated(reason: "...")` and track field usage before removal.
- [ ] Avoid versioned schemas; evolve the single schema additively.

## Operational
- [ ] AuthZ enforced at the field/resolver level, not just the gateway.
- [ ] Rate limiting based on query cost, not request count alone.
- [ ] Caching strategy defined (response cache by query+vars, or `@cacheControl` hints).
- [ ] Observability: per-resolver tracing and error metrics.
