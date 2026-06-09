# RAG Evaluation Metrics

Evaluate retrieval and generation **separately** — they fail for different reasons and need different fixes. Always compare against a no-RAG baseline and a previous-version baseline.

## The gold eval set

A JSONL file, one query per line. Minimum fields:

```json
{"id": "q1", "query": "How do I reset my password?", "relevant_ids": ["art_42", "art_99"], "ideal_answer": "Go to Settings > Security > Reset password ..."}
```

- `relevant_ids`: ground-truth chunk/document ids that contain the answer.
- `ideal_answer`: reference answer for generation scoring (optional but valuable).
- Aim for 50-200 queries covering the real query distribution: easy lookups, paraphrases, multi-hop, out-of-scope (should refuse), and exact-term/ID queries.
- Keep a held-out slice you never tune on.

## Retrieval metrics (need `relevant_ids`)

Let the retriever return a ranked list of ids.

- **Recall@k** = (relevant ids found in top k) / (total relevant ids). "Did we fetch the answer at all?" The most important upstream metric — if it is low, nothing downstream can recover.
- **Precision@k** = (relevant in top k) / k. How much of the context is signal vs distractor.
- **MRR (Mean Reciprocal Rank)** = mean of 1/rank_of_first_relevant. Rewards putting a relevant result high. Good when one hit is enough.
- **nDCG@k (normalized Discounted Cumulative Gain)** = rank-aware, handles graded relevance; the standard ranking-quality metric. Use to judge reranker impact.
- **Hit@k** = 1 if any relevant id in top k, else 0; averaged. Coarse but intuitive.

Measure recall at the retriever's wide k (e.g. recall@30) AND nDCG/MRR at the post-rerank k (e.g. nDCG@5). High recall@30 + low nDCG@5 → reranking problem. Low recall@30 → chunking/embedding problem.

`scripts/eval_retrieval.py` computes recall@k, precision@k, MRR, hit@k, and nDCG@k from a predictions file.

## Generation metrics (need the answer; some need `ideal_answer`)

These are typically scored by an LLM-as-judge with a rubric, or by humans for a sample.

- **Faithfulness / groundedness:** is every claim in the answer supported by the retrieved context? Catches hallucination. The most important generation metric. Judge by decomposing the answer into claims and checking each against context.
- **Answer relevance:** does the answer actually address the query (vs being on-topic but evasive)?
- **Context precision:** of the retrieved chunks, how many were actually used/relevant — measures distractor load.
- **Context recall:** does the retrieved context contain everything needed to produce the ideal answer?
- **Answer correctness:** semantic match to `ideal_answer` (LLM-judge or embedding similarity). Use cautiously — multiple correct phrasings exist.
- **Refusal accuracy:** for out-of-scope queries, did it correctly say "I don't know"?

## LLM-as-judge guidance

- Give the judge a clear rubric and a small integer scale (e.g. 0-1 or 1-5), not vague "rate quality".
- Provide the context, the query, the answer, and (for correctness) the ideal answer.
- Ask for a short justification before the score to improve reliability.
- Calibrate against ~20 human-labeled examples; spot-check periodically.
- Average over the full eval set; report per-category breakdowns (paraphrase vs ID vs multi-hop).

## What good looks like (rough targets, corpus-dependent)

| Metric | Concerning | Decent | Strong |
|---|---|---|---|
| Recall@(retriever k) | < 0.7 | 0.8-0.9 | > 0.9 |
| nDCG@(final k) | < 0.5 | 0.6-0.75 | > 0.8 |
| Faithfulness | < 0.85 | 0.9 | > 0.95 |
| Refusal accuracy (out-of-scope) | < 0.7 | 0.85 | > 0.95 |

These are guides for relative improvement, not absolute pass marks. Always trend against your own baseline.

## Experiment discipline

- Change one variable per run.
- Re-run the full eval, not a cherry-picked subset.
- Record: config diff, every metric, latency p50/p95, cost/query.
- Keep a table in the design doc so regressions are visible.
