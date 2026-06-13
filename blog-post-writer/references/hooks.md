# Hook Patterns

The hook is the first 2-4 sentences. Its only job: make the reader want sentence five. It must create tension or promise a concrete payoff, fast. If a reader can guess the whole post from the hook, rewrite it.

## The seven reliable patterns

### 1. The sharp question
Ask the exact question already in the reader's head.
> Why does your CI pipeline take 22 minutes when the test suite runs in 90 seconds locally?

Works because it names a real pain. Avoid rhetorical questions with obvious answers.

### 2. The surprising number
Lead with a stat that breaks an assumption.
> We deleted 40% of our test suite and our bug-escape rate went *down*.

The number must be true and specific. Round numbers feel invented; "73%" beats "about three quarters."

### 3. The relatable failure
Open on a mistake the reader has made or fears.
> At 2am the on-call pager went off. The dashboard was green. Everything was, technically, fine — and that was the problem.

Vulnerability builds trust and curiosity.

### 4. The bold claim (you then prove)
State a thesis that invites disagreement.
> Most retries make outages worse, not better.

Only use if the body actually delivers the proof. A claim you can't support reads as clickbait.

### 5. The tiny story
A 2-3 sentence scene with a character and a problem.
> A junior engineer asked me why we cache the result of a function that's only called once. I started to explain, then realized I didn't actually know.

### 6. The before/after
Contrast the old painful way with the new way.
> Last quarter, shipping a config change meant a 30-minute deploy and a held breath. Now it's a checkbox.

### 7. The contrarian reframe
Take conventional wisdom and flip it.
> "Don't repeat yourself" is good advice that has caused some of the worst code I've ever maintained.

## Hook → payoff bridge
After the hook, in the same paragraph or the next, tell the reader what they'll get:
> In this post I'll show the three changes that cut our pipeline from 22 to 4 minutes, with the exact config.

## Anti-patterns (delete on sight)
- "In today's fast-paced world / ever-evolving landscape…"
- "As we all know…" / "It is widely known that…"
- Dictionary definitions: "Webster defines latency as…"
- A history lesson before the point ("First introduced in 2009…").
- Apologizing: "This might be obvious, but…"
- Burying the topic: three paragraphs before the reader learns what the post is about.

## Quick test
Read only your first two sentences. Would *you* keep reading if you were skimming a feed? If not, pick a different pattern.
