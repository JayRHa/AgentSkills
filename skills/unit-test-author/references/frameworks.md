# Framework Idioms & Skeletons

Match the repo's existing conventions first. These are sensible defaults.

## Python — pytest

- Files: `test_*.py` or `*_test.py`; functions `test_*`; classes `Test*` (no `__init__`).
- Use plain `assert`; pytest rewrites it for rich messages.
- Fixtures via `@pytest.fixture`; parametrize via `@pytest.mark.parametrize`.
- Exceptions: `with pytest.raises(ValueError, match="insufficient"):`.
- Approx floats: `pytest.approx`.
- Async: `pytest.mark.asyncio` (anyio/pytest-asyncio).
- Run: `pytest -q`; coverage `pytest --cov=pkg --cov-branch`.

```python
import pytest
from bank import Account, InsufficientFunds

@pytest.fixture
def account():
    return Account(balance=100)

def test_withdraw_reduces_balance(account):
    account.withdraw(40)
    assert account.balance == 60

def test_withdraw_more_than_balance_raises(account):
    with pytest.raises(InsufficientFunds, match="balance"):
        account.withdraw(150)
```

## JavaScript / TypeScript — Jest or Vitest

- Files: `*.test.ts` / `*.spec.ts` (or `__tests__/`).
- `describe`/`it`/`expect`. Vitest mirrors Jest's API; swap `jest` ↔ `vi`.
- Mock: `vi.fn()`/`jest.fn()`, `vi.mock('./mod')`.
- Fake timers: `vi.useFakeTimers()` / `jest.useFakeTimers()`.
- Async: `await expect(p).rejects.toThrow(...)`.
- Run: `vitest run` / `jest`; coverage `--coverage`.

```ts
import { describe, it, expect, vi } from 'vitest';
import { Account, InsufficientFunds } from './bank';

describe('Account.withdraw', () => {
  it('reduces the balance', () => {
    const acct = new Account(100);
    acct.withdraw(40);
    expect(acct.balance).toBe(60);
  });

  it('throws when amount exceeds balance', () => {
    const acct = new Account(100);
    expect(() => acct.withdraw(150)).toThrow(InsufficientFunds);
  });
});
```

## Go — testing

- Files: `*_test.go`, functions `func TestXxx(t *testing.T)`.
- Table-driven with subtests `t.Run(tc.name, ...)`.
- Helpers call `t.Helper()`. Parallel: `t.Parallel()`.
- Prefer `if got != want { t.Errorf(...) }`; use `cmp.Diff` for structs.
- Run: `go test ./...`; coverage `go test -cover -coverprofile=c.out ./...`.

```go
func TestWithdraw(t *testing.T) {
    tests := []struct {
        name    string
        start   int
        amount  int
        want    int
        wantErr bool
    }{
        {"normal", 100, 40, 60, false},
        {"exact", 100, 100, 0, false},
        {"overdraw", 100, 150, 0, true},
    }
    for _, tc := range tests {
        t.Run(tc.name, func(t *testing.T) {
            a := &Account{Balance: tc.start}
            err := a.Withdraw(tc.amount)
            if (err != nil) != tc.wantErr {
                t.Fatalf("err = %v, wantErr %v", err, tc.wantErr)
            }
            if err == nil && a.Balance != tc.want {
                t.Errorf("balance = %d, want %d", a.Balance, tc.want)
            }
        })
    }
}
```

## Java — JUnit 5

- `@Test`, `@ParameterizedTest` with `@CsvSource`/`@MethodSource`.
- `assertThrows`, `assertEquals`, AssertJ `assertThat(x).isEqualTo(y)`.
- `@BeforeEach` setup; Mockito `@Mock` + `mock()/when()/verify()`.
- Run: `mvn test` / `gradle test`.

```java
@Test
void withdraw_amountExceedsBalance_throws() {
    Account a = new Account(100);
    assertThrows(InsufficientFundsException.class, () -> a.withdraw(150));
}
```

## Ruby — RSpec

- `describe`/`context`/`it`; `expect(x).to eq(y)`.
- `expect { }.to raise_error(Klass, /msg/)`.
- `double`, `instance_double`, `allow().to receive()`, `expect().to receive()`.
- Run: `rspec`.

```ruby
RSpec.describe Account do
  subject(:account) { described_class.new(balance: 100) }
  it 'raises when overdrawing' do
    expect { account.withdraw(150) }.to raise_error(InsufficientFunds)
  end
end
```

## C# / .NET — xUnit

- `[Fact]` for single, `[Theory]` + `[InlineData]` for table.
- `Assert.Equal`, `Assert.Throws<T>`; FluentAssertions `x.Should().Be(y)`.
- Moq for mocking.

```csharp
[Theory]
[InlineData(100, 40, 60)]
[InlineData(100, 100, 0)]
public void Withdraw_ValidAmount_UpdatesBalance(int start, int amt, int expected)
{
    var a = new Account(start);
    a.Withdraw(amt);
    Assert.Equal(expected, a.Balance);
}
```

## Rust

- `#[cfg(test)] mod tests { ... }` with `#[test]` fns.
- `assert_eq!`, `assert!`, `#[should_panic(expected = "...")]`.
- `Result`-returning tests with `?`. Run: `cargo test`.

```rust
#[test]
fn overdraw_returns_err() {
    let mut a = Account::new(100);
    assert!(a.withdraw(150).is_err());
}
```
