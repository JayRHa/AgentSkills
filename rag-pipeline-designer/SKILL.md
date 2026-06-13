---
name: rag-pipeline-designer
description: Designs end-to-end retrieval-augmented generation (RAG) systems by making principled choices for chunking, embeddings, vector indexing, retrieval, reranking, prompt assembly, and offline evaluation. Use this skill when the user wants to build or improve a RAG pipeline, asks about chunking strategy, embedding model selection, hybrid search, reranking, "my retrieval is bad / hallucinating / missing context", chunk size tuning, vector database choice, or how to measure retrieval quality (recall@k, MRR, nDCG, faithfulness).
license: MIT
---

# RAG Pipeline Designer

## Overview

Keywords: RAG, retrieval-augmented generation, chunking, embeddings, vector database, hybrid search, BM25, dense retrieval, reranking, cross-encoder, recall@k, MRR, nDCG, faithfulness, context window, query expansion, semantic search.

This skill turns a vague "we want to do RAG over our docs" into a concrete, defensible architecture with tradeoffs made explicit. A RAG pipeline is a sequence of lossy stages — each stage can silently throw away the right answer. The job is to identify which stage is failing (or will fail) and pick components that fit the corpus, query distribution, latency budget, and cost ceiling.

Treat RAG design as five decisions made in order, with evaluation wrapped around all of them:

1. **Ingestion & chunking** — how documents become retrievable units.
2. **Embedding & indexing** — how units become searchable vectors (and/or keyword index).
3. **Retrieval** — how a query fetches candidates.
4. **Reranking & context assembly** — how candidates are ordered and packed into the prompt.
5. **Generation** — how the LLM is grounded and constrained.
6. **Evaluation** — how you prove each stage works, offline, before shipping.

Read `references/component-catalog.md` for concrete component options and `references/evaluation-metrics.md` for the metric definitions. Use `scripts/chunk_text.py` to produce candidate chunkings and `scripts/eval_retrieval.py` to score retrieval against a labeled set. Fill in `templates/rag-design-doc.md` to capture the final design. See `examples/support-kb-rag.md` for a complete worked design.

## Workflow

Follow these steps. Do not skip evaluation — a RAG system without an eval set is undebuggable.

1. **Characterize the corpus and queries.** Before choosing anything, answer: How many documents and total tokens? What format (PDF, HTML, Markdown, code, tables, transcripts)? How long is a typical document? Are answers usually in one place or scattered? What do real user queries look like — keyword lookups, natural questions, multi-hop? What is the latency budget (interactive <1s vs batch) and cost ceiling? Capture answers in the design doc's "Context" section.

2. **Build a tiny gold eval set FIRST.** Collect 30-100 real (or realistic) queries. For each, label the document/chunk(s) that contain the answer, and write the ideal answer. This is the single highest-leverage artifact. Without it every later choice is a guess. Store as JSONL (see `scripts/eval_retrieval.py` for the format).

3. **Design ingestion & chunking.** Pick a chunking strategy from the decision framework below. Generate candidates with `scripts/chunk_text.py` and inspect them by eye — chunks that split mid-sentence, orphan table headers, or merge unrelated sections are red flags. Decide chunk size, overlap, and what metadata to attach (source, title, section, page, timestamps, permissions).

4. **Choose embeddings & index.** Select an embedding model based on domain, language, dimension/cost, and max sequence length (must exceed chunk size). Choose dense-only, sparse-only (BM25), or hybrid. Pick a vector store and index type (flat for <100k vectors, HNSW/IVF for scale). See `references/component-catalog.md`.

5. **Design retrieval.** Set `top_k` for the retriever (retrieve generously, e.g. 20-50, then rerank down). Decide on hybrid fusion (Reciprocal Rank Fusion is the safe default). Add query transformations only if the eval shows they help: query rewriting, HyDE, multi-query expansion, metadata filtering.

6. **Add reranking.** A cross-encoder reranker is the highest-ROI quality lever after chunking. Retrieve 20-50 candidates, rerank, keep top 3-8 for the prompt. Skip only if latency-critical and eval shows it does not help.

7. **Assemble context & prompt.** Order chunks by relevance (or put best first AND last — LLMs attend to edges). Deduplicate near-identical chunks. Always include source attribution. Instruct the model to answer only from context and to say "I don't know" when context is insufficient. Budget tokens: leave headroom for the answer.

8. **Evaluate end to end.** Run `scripts/eval_retrieval.py` for retrieval metrics (recall@k, MRR, nDCG). Then evaluate generation: faithfulness (is the answer grounded?), answer relevance, and context precision. Use an LLM-as-judge with a rubric for the generation metrics. Compare against a no-RAG baseline.

9. **Iterate on the weakest stage.** Use the diagnostic table below to localize failure. Change ONE thing at a time and re-measure. Record each experiment in the design doc.

## Decision Framework: Chunking

| Corpus characteristic | Recommended strategy | Typical size | Overlap |
|---|---|---|---|
| Prose, articles, docs | Recursive split on paragraph→sentence boundaries | 300-600 tokens | 10-15% |
| Markdown / HTML with headers | Header-aware (split on sections, keep header in chunk) | section-sized, cap ~800 | small |
| Q&A, FAQ, support tickets | One chunk per Q&A pair (semantic unit) | natural | none |
| Code | By function/class via AST, keep imports/signature | function-sized | none |
| Tables / spreadsheets | Row-group + serialized header per chunk; or summarize | per logical group | none |
| Transcripts / chat | By speaker turn or time window | 200-400 tokens | by turn |
| Long reports, multi-hop | Small chunks for retrieval + parent-document expansion | child 200 / parent 1500 | n/a |

Rules of thumb: smaller chunks = higher precision, more chunks, risk of missing surrounding context; larger chunks = more recall per chunk, but dilute the embedding and waste prompt tokens. Start at ~400 tokens with 15% overlap and tune via eval. Always preserve enough context that a chunk is self-explanatory (include section title as a prefix).

## Decision Framework: Retrieval Strategy

| Query / corpus signal | Strategy |
|---|---|
| Natural-language questions, paraphrases | Dense embeddings |
| Exact terms, IDs, codes, names, rare jargon | Add BM25 / sparse (dense alone misses exact tokens) |
| Mixed (most real systems) | **Hybrid: dense + BM25, fused with RRF** |
| Queries shorter/vaguer than documents | Query rewriting or HyDE before retrieval |
| Answers span multiple docs (multi-hop) | Multi-query expansion + higher top_k |
| Has access control / freshness needs | Metadata filtering pre- or post-retrieval |
| Quality matters more than 50ms latency | Add cross-encoder reranking (almost always worth it) |

## Diagnostic Table: Localizing Failure

Run retrieval eval and generation eval separately to find the broken stage.

| Symptom | Likely stage | Fix |
|---|---|---|
| Correct chunk not in top_k (low recall@k) | Chunking or embedding | Re-chunk; try better/domain embedding; add BM25 for exact terms; raise top_k |
| Correct chunk retrieved but ranked low | Reranking | Add/improve cross-encoder reranker |
| Right chunks retrieved, answer still wrong | Generation / prompt | Tighten grounding instructions; reorder context; reduce distractor chunks |
| Answer invents facts not in context | Faithfulness | Stronger "answer only from context" prompt; lower temperature; cite-or-refuse |
| Answer says "I don't know" when info exists | Recall or context packing | Raise top_k; check chunk was indexed; check filters not over-restrictive |
| Good offline, bad in production | Query distribution drift | Expand eval set with real logged queries |
| Slow | Index / reranker | Switch flat→HNSW; cap rerank candidates; cache embeddings |

## Worked Example (abbreviated)

Corpus: 8k support articles, Markdown, natural-language user questions, <800ms budget.
- Chunking: header-aware, ~500 tokens, title prefix, metadata {article_id, section, product, updated_at}.
- Embedding: general-purpose 768-d model; index HNSW (8k → flat would also work, HNSW future-proofs).
- Retrieval: hybrid dense+BM25, RRF, top_k=30 (BM25 catches error codes like "0x80070005").
- Rerank: cross-encoder → top 5.
- Generation: answer-only-from-context, cite article_id, refuse if unsupported.
- Eval: 60 labeled queries; recall@30 0.91, after rerank nDCG@5 0.82, faithfulness 0.95.

See `examples/support-kb-rag.md` for the full version with experiment log.

## Best Practices

- **Eval set before architecture.** 50 labeled queries beat any amount of intuition. Grow it with production logs.
- **Retrieve wide, rerank narrow.** top_k 20-50 into a cross-encoder, then 3-8 into the prompt.
- **Hybrid by default.** Pure dense retrieval silently fails on exact terms, IDs, and rare jargon.
- **Make chunks self-contained.** Prefix the section/document title so an isolated chunk still makes sense.
- **Attach metadata at ingestion.** You cannot filter on or attribute what you did not store.
- **Always cite sources** and instruct the model to refuse when context is insufficient.
- **Change one variable at a time** and re-measure; log every experiment.
- **Track cost and latency as first-class metrics**, not afterthoughts.
- **Re-embed when you change the embedding model** — never mix vector spaces in one index.

## Common Pitfalls

- **No evaluation set.** The cardinal sin; makes every decision unfalsifiable.
- **Chunks too large.** Embeddings become averaged mush; relevant signal is diluted and recall drops.
- **Chunks too small / no overlap.** Answer gets split across a boundary and is never wholly retrieved.
- **Dense-only retrieval** on corpora full of identifiers, SKUs, or names that must match exactly.
- **Skipping reranking** to save latency, then fighting precision problems for weeks.
- **Stuffing too many chunks** into the prompt — distractors degrade the answer and the "lost in the middle" effect buries the relevant one.
- **Forgetting freshness/permissions** — stale or unauthorized chunks leak into answers.
- **Mismatched chunk size vs embedding max tokens** — silent truncation loses the chunk's tail.
- **Optimizing retrieval metrics while ignoring faithfulness** — perfect recall with an ungrounded generator still hallucinates.
- **Testing on the same examples you tuned on** — keep a held-out slice.
