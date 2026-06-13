# Worked Example: RAG over a Support Knowledge Base

A complete, realistic design produced by following the skill workflow.

## Step 1 — Context

- Corpus: ~8,000 support articles in Markdown, avg ~900 tokens, with headings, code snippets, and error codes (e.g. `0x80070005`).
- Users: customers and agents asking natural-language questions, plus exact error-code lookups.
- Latency budget: < 800 ms p95 (interactive chat widget).
- Cost ceiling: low; prefer open-weight embeddings, small reranker.
- Freshness: articles change weekly; must reflect `updated_at`.

## Step 2 — Gold eval set

60 queries collected from real chat logs + support team, labeled with the article(s) that answer them. `gold.jsonl` excerpt:

```json
{"id": "q1", "query": "how do I reset my password", "relevant_ids": ["art_42"], "ideal_answer": "Open Settings > Security > Reset password and follow the email link."}
{"id": "q2", "query": "error 0x80070005 on install", "relevant_ids": ["art_311"], "ideal_answer": "0x80070005 is an access-denied error; run the installer as administrator."}
{"id": "q3", "query": "is there an API rate limit", "relevant_ids": ["art_77", "art_78"], "ideal_answer": "Yes, 600 requests/min per key; 429 on exceed."}
{"id": "q4", "query": "what is the airspeed of an unladen swallow", "relevant_ids": [], "ideal_answer": "I don't know — that's outside this knowledge base."}
```

Categories covered: paraphrase questions, exact error codes, multi-article answers, and out-of-scope (must refuse).

## Step 3 — Chunking

Header-aware (`scripts/chunk_text.py --strategy markdown --size 500`). Each chunk prefixed with `Article Title > Section`. Metadata attached: `{article_id, title, section, product, updated_at}`.

Inspection caught a problem: code blocks with error codes were being split from their surrounding explanation. Fix: treat fenced code + its preceding paragraph as one unit. Re-ran, chunks looked self-contained.

## Step 4 — Embeddings & index

- Embedding: general-purpose 768-d open-weight model, max seq 512 tokens > our 500-token chunks. Vectors normalized for cosine.
- Index: HNSW (8k vectors would run fine flat, but HNSW future-proofs growth and keeps p95 low).
- Also built a BM25 lexical index over the same chunks — critical for error codes and product names that dense retrieval blurs.

## Step 5 — Retrieval

- Hybrid: dense top 30 + BM25 top 30, fused with RRF (k=60).
- Metadata pre-filter available for `product` when the UI knows it.
- top_k after fusion: 30 candidates.

## Step 6 — Reranking

- Cross-encoder reranker over the 30 candidates, keep top 5.
- Adds ~120 ms; within budget.

## Step 7 — Context & prompt

- Deduplicate near-identical chunks.
- Order top 5 by rerank score; strongest first.
- Each chunk labeled with `[art_id]` for citation.
- System prompt: "Answer only from the context. Cite article ids in brackets. If the context does not contain the answer, say you don't know." Temperature 0.1.

## Step 8 — Evaluation

Retrieval (`scripts/eval_retrieval.py gold.jsonl preds.jsonl --k 5 10 30`):

| Config | recall@30 | nDCG@5 | MRR |
|---|---|---|---|
| Dense only | 0.78 | 0.61 | 0.66 |
| + BM25 hybrid (RRF) | 0.91 | 0.70 | 0.74 |
| + cross-encoder rerank | 0.91 | 0.82 | 0.85 |

Generation (LLM-judge, 0-1):

| Metric | Score |
|---|---|
| Faithfulness | 0.95 |
| Answer relevance | 0.90 |
| Refusal accuracy (out-of-scope) | 0.93 |

## Step 9 — Experiment log / learnings

- Dense-only missed `q2` (error code) entirely — BM25 fixed it. This single change drove recall@30 from 0.78 to 0.91.
- Reranking barely changed recall (expected) but lifted nDCG@5 0.70 -> 0.82: the right chunks were being retrieved but ranked too low for a 5-chunk prompt.
- Raising final k from 5 to 10 did NOT improve answers and slightly hurt faithfulness (more distractors) — kept 5.
- Out-of-scope refusal needed an explicit prompt instruction; without it the model guessed.

## Final architecture (one line)

Markdown header-aware chunks (500 tok, title prefix, metadata) -> 768-d dense (HNSW) + BM25 -> RRF top 30 -> cross-encoder rerank top 5 -> grounded, cite-or-refuse generation at temp 0.1.
