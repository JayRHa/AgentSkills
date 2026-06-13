# Patterns Cookbook (vetted & ReDoS-safe)

All patterns below avoid nested/overlapping quantifiers. Unless stated, they are
shown anchored for **validation**. For **search/extract**, remove `^`/`$`.
Flavor: PCRE/Python/JavaScript unless noted. `\d` matches Unicode digits in some
flavors — substitute `[0-9]` for ASCII-only.

## Numbers
| Need | Pattern | Notes |
|---|---|---|
| Integer (optional sign) | `^[+-]?[0-9]+$` | No leading-zero rule. |
| Integer, no leading zeros | `^[+-]?(0|[1-9][0-9]*)$` | Rejects `007`. |
| Decimal / float | `^[+-]?[0-9]+(\.[0-9]+)?$` | Requires digit before dot. |
| Float w/ exponent | `^[+-]?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?$` | Scientific. |
| Currency (US) | `^\$?[0-9]{1,3}(,[0-9]{3})*(\.[0-9]{2})?$` | Commas optional only as full groups. |
| Percentage 0-100 | `^(100|[0-9]{1,2})(\.[0-9]+)?%?$` | Loose upper bound. |
| Hex color | `^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$` | 3 or 6 digits. |

## Identifiers & slugs
| Need | Pattern | Notes |
|---|---|---|
| Identifier (C-style) | `^[A-Za-z_][A-Za-z0-9_]*$` | Letter/underscore first. |
| Kebab-case slug | `^[a-z0-9]+(?:-[a-z0-9]+)*$` | No leading/trailing/double hyphen. |
| Snake_case | `^[a-z0-9]+(?:_[a-z0-9]+)*$` | |
| UUID v4 | `^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$` | Case-insensitive flag for upper. |
| Semantic version | `^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$` | Per semver.org core+pre+build. |

## Dates & times
| Need | Pattern | Notes |
|---|---|---|
| ISO date YYYY-MM-DD | `^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$` | Does NOT validate Feb 30 — use code for true calendar checks. |
| 24h time HH:MM | `^([01][0-9]|2[0-3]):[0-5][0-9]$` | |
| 24h time HH:MM:SS | `^([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$` | |
| ISO 8601 datetime | `^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](?:\.[0-9]+)?(?:Z|[+-](0[0-9]|1[0-4]):[0-5][0-9])$` | Z or offset. |

## Network
| Need | Pattern | Notes |
|---|---|---|
| IPv4 (octet-checked) | `^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$` | Rejects 256+. |
| Port number | `^(?:6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[1-9][0-9]{0,3})$` | 1-65535. |
| Hostname label | `^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$` | RFC 1123 single label. |
| MAC address | `^[0-9A-Fa-f]{2}(?:[:-][0-9A-Fa-f]{2}){5}$` | Colon or hyphen separators. |

## Email & URL (practical, not full RFC)
| Need | Pattern | Notes |
|---|---|---|
| Email (pragmatic) | `^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$` | Good enough for forms. Full RFC 5322 needs a parser. |
| HTTP(S) URL | `^https?://[^\s/$.?#].[^\s]*$` | Lightweight; for strict parsing use a URL library. |

## Strings & whitespace
| Need | Pattern | Notes |
|---|---|---|
| Trim helper (match leading/trailing ws) | `^\s+|\s+$` | Replace with empty, global flag. |
| Collapse runs of spaces | ` {2,}` | Replace with single space. |
| Double-quoted string token | `"[^"\\]*(?:\\.[^"\\]*)*"` | Unrolled loop — safe alternative to `".*?"`; handles escapes. |
| Non-empty, no surrounding ws | `^\S(?:.*\S)?$` | |

## Log lines / CSV
| Need | Pattern | Notes |
|---|---|---|
| Apache common log IP+time | `^(\S+) \S+ \S+ \[([^\]]+)\] "([^"]*)" (\d{3}) (\d+|-)$` | Field-by-field via `[^x]` classes. |
| Simple CSV field (no embedded commas) | `[^,\n]*` | For quoted CSV, use a CSV parser, not regex. |
| Quoted-or-bare CSV field | `(?:"[^"]*"|[^,\n]*)` | Does not handle escaped quotes; prefer a CSV lib. |

## Things you should NOT regex
- HTML/XML structure (nesting) → use an HTML/XML parser.
- Balanced parentheses/brackets (recursive) → PCRE recursion exists but a parser is clearer.
- Full RFC 5322 email → use a validation library / send a confirmation email.
- Arbitrary arithmetic precedence → use a real grammar/parser.

## Safe-design reminders
- Replace `.*` with a negated class (`[^\n]*`, `[^"]*`) whenever the delimiter is known.
- Use the **unrolled loop** idiom `A[^A\\]*(?:\\.[^A\\]*)*A` for quoted strings instead of lazy `.*?`.
- Bound open-ended quantifiers with `{0,n}` when a max length exists.
