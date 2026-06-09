# Plain-Language Style Guide

Rules for clear technical prose, plus an editing checklist. Apply during drafting and again during the edit pass.

## Word choice

- Use the shortest accurate word. Common swaps:
  - utilize → use; facilitate → help; leverage → use; in order to → to
  - approximately → about; prior to → before; subsequent to → after
  - in the event that → if; due to the fact that → because; at this point in time → now
  - terminate → end/stop; commence → start; demonstrate → show
- Cut filler that adds no meaning: *very, really, actually, basically, simply, just, easily, of course, needless to say, in fact, please note that.*
- Avoid "simply/just/easily" — if it were simple the reader wouldn't be reading. They make readers feel dumb when stuck.
- Define every acronym/term on first use, then use it consistently. One term per concept — don't alternate "function/method/routine" for the same thing.
- Prefer concrete over abstract: "saves 200 ms per request" beats "improves performance."

## Sentences

- One idea per sentence. Target under ~20 words; rewrite anything over ~25.
- Active voice with a named actor: "The server rejects the request" not "The request is rejected." Passive is acceptable only when the actor is unknown or irrelevant.
- Present tense for behavior: "The command returns a token" not "will return."
- Put the main clause first; conditions and qualifiers after: "Restart the service after editing the config" — or lead with the condition only when it gates the whole sentence.
- Parallel structure in lists and series: all items start the same grammatical way.

## Paragraphs and structure

- BLUF: lead with the conclusion or the answer, then support it.
- One topic per paragraph; 2–5 sentences is plenty.
- Use lists for 3+ parallel items. Numbered for sequence, bulleted otherwise.
- Use tables for anything with consistent attributes (params, options, comparisons).
- Descriptive headings that state content: "Configure TLS" not "Configuration."
- Keep heading levels properly nested (no jumping H2 → H4).

## Addressing the reader

- Use "you" for the reader and imperative mood for instructions: "Open the file," "Set the variable."
- Avoid "we" except in explanation/conceptual docs; never use "the user" when you mean "you."
- Don't write "the developer should" — write "do X."

## Formatting conventions

- `code font` for commands, filenames, flags, values, env vars, function names, and literal text the reader types or sees.
- Fenced code blocks with a language tag for multi-line code; include expected output where helpful (in a comment or separate block).
- Bold for UI labels and the first mention of a key term; italics sparingly for emphasis.
- Links: descriptive text ("see the auth guide"), never "click here" or a bare URL.
- Callouts: clearly mark **Warning**, **Note**, **Tip** so they stand out from steps.

## Accessibility

- Alt text for every meaningful image; describe what it shows, not "image."
- Don't rely on color alone to convey meaning.
- Use real heading elements (not bold text) for structure so screen readers and TOCs work.
- Keep tables simple with header rows; avoid merged cells.
- Spell out the meaning, not just the look: "the red Delete button" → "the **Delete** button."

## Numbers, units, and examples

- Use numerals for measurable quantities ("3 retries", "500 ms").
- Include units and ranges. State defaults.
- Examples must be complete and runnable. Avoid `<placeholder>` unless you immediately show a real value too.
- Show input AND expected output so readers can confirm success.

## Editing checklist (run on every draft)

1. Does the doc match its declared purpose and reader? Cut anything off-topic.
2. Is it the right doc type? No tutorial buried in reference, no theory in a how-to.
3. First screen: can the reader tell what this is and whether it's for them?
4. Every step verified by actually doing it on a clean setup?
5. Every command/link/code block correct and runnable?
6. Passive voice converted to active where there's a clear actor?
7. Long sentences (>25 words) broken up?
8. Jargon defined; terminology consistent throughout?
9. Weasel words (simply, just, robust, several, easily) removed or made specific?
10. Headings descriptive and properly nested? Skim-readable?
11. Examples complete with expected output?
12. Dated/versioned if it can go stale?

Run `scripts/readability.py <file>` to automate checks 6, 7, and 9.
