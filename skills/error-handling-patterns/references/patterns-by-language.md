# Idiomatic Error-Handling Patterns by Language

Concise, correct patterns for result/exception signaling, retries, and timeouts in five common languages. Match the idioms of the codebase you're in.

---

## Python

**Exceptions (idiomatic default).** Catch *specific* types; chain with `from`.

```python
class OrderError(Exception):
    pass

try:
    resp = client.charge(amount)
except ConnectionError as err:
    raise OrderError(f"charge failed for order {order_id}") from err  # preserve cause
```

**Never** `except: pass` or bare `except Exception` that continues. Catch the narrowest type.

**Result type** when failure is normal (avoids exceptions for control flow):

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar("T"); E = TypeVar("E")

@dataclass
class Ok(Generic[T]):
    value: T

@dataclass
class Err(Generic[E]):
    error: E

Result = Union[Ok[T], Err[E]]

def parse_port(s: str) -> Result[int, str]:
    if not s.isdigit():
        return Err(f"not a number: {s!r}")
    return Ok(int(s))
```

**Timeout** (requests / httpx): always pass `timeout=(connect, read)`.

```python
requests.get(url, timeout=(3.05, 10))  # never omit timeout
```

**Cleanup**: context managers (`with`) or `try/finally`.

---

## TypeScript / JavaScript

**Exceptions** with `cause` (ES2022):

```ts
try {
  await charge(amount);
} catch (err) {
  throw new Error(`charge failed for order ${orderId}`, { cause: err });
}
```

**Result type** (discriminated union) — preferred for expected failures:

```ts
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function parsePort(s: string): Result<number, string> {
  const n = Number(s);
  return Number.isInteger(n) ? { ok: true, value: n }
                            : { ok: false, error: `not an int: ${s}` };
}
```

**Timeout** with `AbortController` (no native fetch timeout):

```ts
const ac = new AbortController();
const t = setTimeout(() => ac.abort(), 10_000);
try {
  const res = await fetch(url, { signal: ac.signal });
} finally {
  clearTimeout(t);
}
```

Avoid: unhandled promise rejections, `catch (e) {}` empty blocks, throwing non-Error values.

---

## Go

**Errors are values.** Return `error`, wrap with `%w`, inspect with `errors.Is/As`.

```go
resp, err := client.Charge(ctx, amount)
if err != nil {
    return fmt.Errorf("charge order %s: %w", orderID, err) // wrap, keep cause
}

// Classify:
if errors.Is(err, context.DeadlineExceeded) { /* transient */ }
var apiErr *APIError
if errors.As(err, &apiErr) && apiErr.Status == 429 { /* retry */ }
```

**Sentinel / typed errors** for classification:

```go
var ErrNotFound = errors.New("not found")

type APIError struct{ Status int; Msg string }
func (e *APIError) Error() string { return e.Msg }
func (e *APIError) Retryable() bool { return e.Status == 429 || e.Status >= 500 }
```

**Timeout/deadline**: pass `context.Context` everywhere.

```go
ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
defer cancel()
```

Panics are for programmer errors only; never use them for normal flow.

---

## Rust

**`Result<T, E>` everywhere**; `?` propagates; `thiserror`/`anyhow` for ergonomics.

```rust
use thiserror::Error;

#[derive(Error, Debug)]
enum ChargeError {
    #[error("network failure")] Network(#[from] reqwest::Error),
    #[error("declined: {0}")] Declined(String),
}

fn charge(amount: u64) -> Result<Receipt, ChargeError> {
    let resp = client.post(url).send()?;        // ? converts via #[from]
    if resp.status() == 402 {
        return Err(ChargeError::Declined("insufficient funds".into()));
    }
    Ok(resp.json()?)
}
```

Classify with `matches!` or methods on the error enum. Use `panic!`/`expect` only for invariants that indicate bugs. `Option` for absence, `Result` for failure.

**Timeout** (reqwest): `.timeout(Duration::from_secs(10))` on the client/request.

---

## Java

**Exceptions**; prefer unchecked for unrecoverable, checked for recoverable domain failures. Chain causes.

```java
try {
    client.charge(amount);
} catch (IOException e) {
    throw new OrderException("charge failed for order " + orderId, e); // cause preserved
}
```

**Classify** with a typed exception:

```java
class ApiException extends RuntimeException {
    final int status;
    ApiException(int status, String msg) { super(msg); this.status = status; }
    boolean retryable() { return status == 429 || status >= 500; }
}
```

**Result-style** with `Optional` (absence) or a sealed `Result` type (Java 17+ sealed interfaces) for expected failures. Don't return `null` to mean error.

**Timeout**: `HttpClient` builder `.connectTimeout(...)` plus per-request `.timeout(...)`. Always set both. Clean up with try-with-resources.

---

## Cross-Language Rules

- Translate errors at module boundaries: catch low-level, surface domain-level.
- One signaling style per layer; convert between layers deliberately.
- Always preserve the original cause.
- Absence (`Optional`/`Option`/`None`/`null`-with-care) is not the same as failure (`Result`/exception). Model them distinctly.
