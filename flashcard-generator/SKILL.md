---
name: flashcard-generator
description: Turns notes, articles, or a topic into high-quality spaced-repetition flashcards that follow proven formulation principles — atomic, minimum-information, cloze deletions, and active recall — ready to import into Anki or any SRS. Use this skill when the user asks to "make flashcards", "create Anki cards", "turn these notes into flashcards", "help me memorize X", "generate study cards", or "make cloze deletions". Produces clean Q/A pairs and can export to Anki-importable CSV.
license: MIT
---

# Flashcard Generator

## Overview

Convert material into flashcards that are actually effective for long-term memory: each card tests **one** atomic fact, is phrased for **active recall**, and is unambiguous. Follow the formulation principles in `references/card-principles.md` (based on SuperMemo's "20 rules" and spaced-repetition research).

Keywords: flashcards, Anki, spaced repetition, SRS, active recall, cloze deletion, memorization, study cards, Q&A, mnemonics, learning.

## Workflow

1. **Identify the learning goal.** What must the user be able to recall or do? Cards should serve that goal, not just restate text.
2. **Extract atomic facts.** Break the material into the smallest meaningful units. One card = one fact. Split any "and"/list-laden card.
3. **Choose a card type per fact** (see `references/card-principles.md`):
   - **Basic Q/A** — for a single fact ("What year…?", "What does X do?").
   - **Cloze deletion** — for facts embedded in a sentence (`The {{c1::mitochondria}} is the powerhouse of the cell`).
   - **Reversed** — when recall is needed both directions (term↔definition).
   - **Image/application** — for procedures or visual recall.
4. **Formulate for recall, not recognition.** Questions must have a specific, unambiguous answer. Avoid yes/no and "list everything about X" cards.
5. **Apply the minimum information principle.** Simple, short cards review faster and stick better than dense ones.
6. **Add context only when needed** to disambiguate (e.g. tag the subject) — but keep cues out of the answer.
7. **Review for interference** — cards that are too similar cause mix-ups. Differentiate them.
8. **Export.** Produce a clean list and/or run `scripts/to_anki_csv.py` to generate an Anki-importable file (Basic and Cloze note types).

## Decision Framework

| Fact shape | Card type |
| --- | --- |
| Single discrete fact | Basic Q→A |
| Fact inside a sentence/definition | Cloze |
| Term you must recall both ways | Basic + reverse |
| Enumeration/list | Split into N cards, or cloze each item, or use a mnemonic card |
| Procedure/steps | One card per step, or "what comes after step N?" |

## Worked Example

**Source:** "The TCP three-way handshake establishes a connection using SYN, SYN-ACK, and ACK."

Bad (not atomic, recognition-only):
> Q: Describe the TCP handshake. → A: It uses SYN, SYN-ACK, ACK to set up a connection.

Good (atomic, recall):
```
Q: How many steps are in the TCP connection handshake?  → A: Three
Q: What does the client send first to open a TCP connection?  → A: SYN
Q: What does the server reply with after receiving a SYN?  → A: SYN-ACK
Q: What does the client send to complete the TCP handshake?  → A: ACK
Cloze: The TCP handshake is {{c1::SYN}} → {{c2::SYN-ACK}} → {{c3::ACK}}.
```

See `examples/photosynthesis-cards.md` for a full set.

## Best Practices

- **One fact per card** — atomic and minimal.
- **Active recall**: the question forces retrieval, not recognition.
- **Unambiguous answers** — exactly one correct response.
- **Cloze for context-bound facts**; basic Q/A for discrete facts.
- Keep cards **short**; brevity speeds reviews and aids retention.
- **Understand before memorizing** — never make cards for things you don't understand.

## Common Pitfalls

- **Sets/lists on one card** ("name all 8 planets") — split them.
- **Recognition cards** (yes/no, multiple-choice phrased as recall).
- **Ambiguous questions** with several valid answers.
- **Cards that leak the answer** in the question's wording.
- **Interference** from near-identical cards.
- **Memorizing without understanding** — leads to brittle, useless recall.
