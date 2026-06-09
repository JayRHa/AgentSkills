# Release Notes Style Guide

The goal of every release note: a reader should understand **what changed for them** and **what (if anything) they must do** — in one read, without opening the code.

## Voice
- **Audience-first.** Write for the person using the product, not the person who built it.
- **Benefit before mechanism.** State the outcome, then optionally the cause.
  - Bad: "Refactored the token validation middleware."
  - Good: "Sign-in is now faster and more reliable."
- **Active voice.** "Adds dark mode" not "Dark mode was added."
- **Present tense** for what the release does now. "The dashboard loads…", "You can now export…".

## Person
- **Changelogs / `CHANGELOG.md`:** impersonal or second person. "Adds…", "You can now…". Avoid "we".
- **Announcements / blog / email:** "we" is acceptable and warmer. "We rebuilt search from the ground up."
- Never use engineer names or first-person singular ("I fixed").

## Sentence shape
- One idea per bullet. If a bullet has an "and" joining two unrelated changes, split it.
- Prefer ≤ 20 words. Trim "in order to", "the ability to", "functionality".
- Lead bullets with a strong verb or the noun being changed.

## Terminology
- Pick ONE name per concept and use it everywhere ("workspace" vs "project" vs "org" — choose one).
- Match the UI labels users actually see. If the button says "Export", call it "Export", not "data egress".
- Spell out acronyms on first use unless they are universal (API, URL, CSV).
- Code identifiers (`--out`, `getUser()`, `/v2/users`) in backticks.

## Quantify
Numbers earn trust. Use real, measured figures only.
- "Loads 40% faster", "Reduces memory use by ~120 MB", "Supports up to 10,000 rows".
- Never invent metrics. If you don't have one, describe the qualitative win.

## Emoji / prefix policy
Optional but consistent. Either use them on every category header or none.
- 💥 / **Breaking Changes**
- 🔒 **Security**
- ✨ **Features** (new capability)
- ⚡ **Improvements** (enhancements, performance, UX polish)
- 🐛 **Bug Fixes**
- ⚠️ **Deprecations**

## References & links
- Append `(#1234)` for PR/issue at the end of the line.
- Hyperlink the number in Markdown when a base URL is known: `([#1234](https://github.com/org/repo/pull/1234))`.
- Link migration guides and docs inline where the reader needs them.

## Good vs. bad

| Bad | Why | Good |
|---|---|---|
| Fix bug in parser | Vague, no user impact | Fixed incorrect totals when importing CSV files with quoted commas. (#231) |
| Bumped lodash to 4.17.21 | No user-facing meaning | _(omit — internal dependency bump)_ |
| We have added a new ability for users to be able to filter | Wordy, passive-ish | You can now filter the activity feed by date and author. (#290) |
| Various improvements | Says nothing | Search results now appear as you type, and history loads instantly. (#301, #305) |
| feat!: drop node 14 | Raw commit, no guidance | **Breaking:** Drops support for Node.js 14. Upgrade to Node.js 18 or later before updating. (#310) |

## Highlight summary
Start longer releases with a 1–3 sentence summary of the headline changes, so skimmers get the gist before the categorized list.
