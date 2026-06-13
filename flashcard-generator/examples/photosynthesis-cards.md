# Worked Example: Flashcards from a Paragraph

**Source paragraph**
> Photosynthesis occurs in the chloroplasts of plant cells. It converts carbon dioxide and water into glucose and oxygen, using energy from sunlight captured by the pigment chlorophyll. The process has two stages: the light-dependent reactions and the Calvin cycle.

**Generated cards** (atomic, recall-oriented)

```
Q: In which organelle does photosynthesis occur?  | Chloroplasts
Q: What two inputs does photosynthesis consume?    | Carbon dioxide and water
Q: What two products does photosynthesis produce?  | Glucose and oxygen
Q: What pigment captures light energy in photosynthesis? | Chlorophyll
Q: What are the two stages of photosynthesis?      | Light-dependent reactions and the Calvin cycle
The pigment that captures sunlight for photosynthesis is {{c1::chlorophyll}}.
Photosynthesis turns CO2 and water into {{c1::glucose}} and {{c2::oxygen}}.
```

**Notes on the choices**
- The "two inputs / two products" cards are borderline sets — kept as pairs because they're tightly coupled and short; could split further if confused.
- Cloze cards reinforce the same facts in context for interleaving.

Run `python3 ../scripts/to_anki_csv.py photosynthesis-cards.txt` after saving the card lines to a `.txt` to get an importable deck.
