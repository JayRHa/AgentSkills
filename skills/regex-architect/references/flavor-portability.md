# Regex Flavor Portability

Regex syntax is not universal. Confirm the runtime before delivering a pattern.

## Engine families
- **Backtracking (full-featured):** PCRE/PCRE2, Python `re`, JavaScript (ECMAScript),
  Java `java.util.regex`, .NET, Ruby, Perl. Support lookarounds and backreferences;
  vulnerable to ReDoS.
- **Automaton (linear-time):** RE2 (Go `regexp`, Rust `regex`, C++ RE2). No
  backreferences, no lookarounds; immune to ReDoS.

## Feature support matrix
| Feature | PCRE | Python re | JavaScript | Java | .NET | Go/Rust (RE2) |
|---|---|---|---|---|---|---|
| Lookahead `(?=)` `(?!)` | yes | yes | yes | yes | yes | NO |
| Lookbehind `(?<=)` `(?<!)` | yes | fixed-width | yes (modern) | yes | yes (variable) | NO |
| Backreference `\1` | yes | yes | yes | yes | yes | NO |
| Named group def | `(?<name>)` / `(?P<name>)` | `(?P<name>)` | `(?<name>)` | `(?<name>)` | `(?<name>)` | `(?P<name>)` |
| Named backref | `\k<name>` | `(?P=name)` | `\k<name>` | `\k<name>` | `\k<name>` | n/a |
| Atomic group `(?>)` | yes | 3.11+ | NO | yes | yes | n/a (linear) |
| Possessive `a++` | yes | 3.11+ | NO | yes | yes | NO |
| Inline flags `(?i)` | yes | yes | scoped `(?i:)` modern | yes | yes | yes |
| Inline scoped `(?i:...)` | yes | 3.6+ | yes (ES2018) | yes | yes | yes |
| `\A` `\z`/`\Z` | yes | yes | NO (use `^`/`$` + flags) | yes | yes | `\A` `\z` |
| `\d` is Unicode by default | depends | yes (str) | NO (ASCII) | depends | yes | configurable |
| Verbose/extended `x` | yes | `re.X` | NO (no native) | `(?x)` | yes | `(?x)` |
| Unicode prop `\p{L}` | yes | `regex` module only | yes (`u` flag) | yes | yes | yes |

## Key gotchas by flavor
- **JavaScript**
  - No `\A`/`\z`. Use `^`/`$`; without the `m` flag they mean string start/end.
  - No verbose mode — build long patterns from string concatenation or `RegExp`.
  - `\d`, `\w` are ASCII-only unless you use Unicode property escapes with the `u` flag.
  - Use `.test()` for boolean, `String.prototype.match`/`matchAll` for extraction.
  - No possessive quantifiers or atomic groups → guard against ReDoS by design.
- **Python `re`**
  - Use `re.fullmatch()` for validation (implicit `\A...\z`); `^...$` alone allows
    a trailing newline at `$`.
  - `(?P<name>...)` for named groups; `\g<name>` in replacement strings.
  - For `\p{...}` Unicode properties, use the third-party `regex` module.
  - Possessive/atomic available in 3.11+.
- **Java**
  - Double-escape in string literals: `\\d` in source for `\d`.
  - `Pattern.compile(..., Pattern.COMMENTS)` for verbose mode.
- **.NET**
  - Supports variable-length lookbehind and `RegexOptions.NonBacktracking` (linear).
  - Set `matchTimeout` for untrusted input.
- **Go / Rust (RE2)**
  - No lookarounds or backreferences — if a pattern uses them, redesign or change
    engines. Trade-off: guaranteed linear time. Named groups use `(?P<name>)`.

## Porting checklist
- [ ] Replace `\A`/`\z` with `^`/`$` for JavaScript (and confirm no `m` flag).
- [ ] Rewrite lookbehind/backreferences if targeting RE2.
- [ ] Adjust named-group syntax to the target.
- [ ] Double-escape backslashes for Java/string-literal contexts.
- [ ] Decide `\d`/`\w` ASCII vs Unicode and switch to `[0-9]`/`[A-Za-z0-9_]` if needed.
- [ ] Convert verbose-mode patterns to concatenated strings for JS.
- [ ] Confirm whether possessive/atomic constructs are available; if not, redesign
      for ReDoS safety.
