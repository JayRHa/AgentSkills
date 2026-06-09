# Table-Driven / Parametrized Tests

Use a table when the **same assertion logic** runs over multiple input/output pairs (≥3). Benefits: adding a case is one line, the intent is a data table, and each case reports independently.

## Rules for good tables

- Give every row a descriptive `name`/`id` so failures point to the case.
- Keep the loop body tiny: arrange from the row, act once, assert.
- One table per behavior. Don't mix happy-path and error rows unless the row carries a `wantErr` field that the body branches on.
- Don't put logic in the table (no conditionals computing expected values) — precompute literals so the expected column is obvious.
- Cover the edge cases from `references/edge-cases.md` as rows.

## Python (pytest.mark.parametrize)

```python
import pytest
from calc import slugify

@pytest.mark.parametrize("raw, expected", [
    pytest.param("Hello World", "hello-world", id="spaces"),
    pytest.param("  trim  ", "trim", id="trim-whitespace"),
    pytest.param("Café", "cafe", id="unicode-accent"),
    pytest.param("", "", id="empty"),
    pytest.param("a--b", "a-b", id="collapse-dashes"),
])
def test_slugify(raw, expected):
    assert slugify(raw) == expected
```

Multiple params stack; use `ids=` or `pytest.param(..., id=...)` for readable output.

## JavaScript / TypeScript (it.each / test.each)

```ts
import { describe, it, expect } from 'vitest';
import { slugify } from './slug';

describe('slugify', () => {
  it.each([
    { raw: 'Hello World', expected: 'hello-world' },
    { raw: '  trim  ',    expected: 'trim' },
    { raw: '',            expected: '' },
    { raw: 'a--b',        expected: 'a-b' },
  ])('slugifies "$raw" -> "$expected"', ({ raw, expected }) => {
    expect(slugify(raw)).toBe(expected);
  });
});
```

## Go (slice of structs + subtests)

```go
func TestSlugify(t *testing.T) {
    cases := []struct {
        name string
        raw  string
        want string
    }{
        {"spaces", "Hello World", "hello-world"},
        {"trim", "  trim  ", "trim"},
        {"empty", "", ""},
        {"collapse", "a--b", "a-b"},
    }
    for _, tc := range cases {
        tc := tc // capture (pre-Go 1.22)
        t.Run(tc.name, func(t *testing.T) {
            t.Parallel()
            if got := Slugify(tc.raw); got != tc.want {
                t.Errorf("Slugify(%q) = %q, want %q", tc.raw, got, tc.want)
            }
        })
    }
}
```

## Java (JUnit 5 @ParameterizedTest)

```java
@ParameterizedTest(name = "[{index}] {0} -> {1}")
@CsvSource({
    "'Hello World', hello-world",
    "'  trim  ',    trim",
    "'a--b',        a-b",
})
void slugify(String raw, String expected) {
    assertEquals(expected, Slug.of(raw));
}
```

For complex objects use `@MethodSource` returning a `Stream<Arguments>`.

## C# (xUnit [Theory])

```csharp
[Theory]
[InlineData("Hello World", "hello-world")]
[InlineData("  trim  ", "trim")]
[InlineData("", "")]
public void Slugify(string raw, string expected)
    => Assert.Equal(expected, Slug.Of(raw));
```

Use `[MemberData]`/`[ClassData]` for non-constant cases.

## Rust

```rust
#[test]
fn slugify_table() {
    let cases = [
        ("Hello World", "hello-world"),
        ("  trim  ", "trim"),
        ("", ""),
    ];
    for (raw, want) in cases {
        assert_eq!(slugify(raw), want, "input: {raw:?}");
    }
}
```
