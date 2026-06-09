# RAG Design Doc: <System Name>

> Fill every section. Empty sections are unmade decisions. Keep the experiment log updated.

## 1. Context

- **Goal / use case:**
- **Corpus:** count, total tokens, formats, avg doc length
- **Answer locality:** single-passage / multi-passage / multi-hop
- **Query distribution:** keyword / NL questions / mixed; examples:
- **Latency budget:** p50 ___ / p95 ___
- **Cost ceiling:** per query / per month
- **Freshness & access control needs:**
- **No-RAG baseline performance:**

## 2. Evaluation set

- **Location:** `gold.jsonl`
- **Size:** ___ queries
- **Categories & counts:** paraphrase ___, exact-term/ID ___, multi-hop ___, out-of-scope ___
- **Held-out slice:** ___
- **Generation metrics & judge:** faithfulness / relevance / refusal; judge = ___

## 3. Ingestion & chunking

- **Parser(s):**
- **Strategy:** fixed / recursive / header-aware / semantic / parent-document
- **Chunk size / overlap:** ___ tokens / ___%
- **Self-context prefix:** (e.g. title > section)
- **Metadata captured:** {___}
- **Known parsing risks:** (tables, code, scans)

## 4. Embedding & index

- **Embedding model:** name, dim, max seq len, language/domain
- **Asymmetric query/doc encoding:** yes / no
- **Normalization & similarity:** cosine / dot / L2
- **Sparse index:** BM25 / learned-sparse / none
- **Vector index:** flat / HNSW / IVF(-PQ); params
- **Store:**

## 5. Retrieval

- **Mode:** dense / sparse / hybrid (fusion = RRF / weighted)
- **Retriever top_k:** ___
- **Query transforms:** rewrite / HyDE / multi-query / none (justify with eval)
- **Metadata filters:**

## 6. Reranking & context assembly

- **Reranker:** cross-encoder / LLM / MMR / none; candidates in ___ -> keep ___
- **Dedup:** how
- **Ordering:** relevance / edge-placement
- **Attribution format:**
- **Token budget for context vs answer:**

## 7. Generation

- **Model & temperature:**
- **Grounding instructions (verbatim):**
- **Citation / refusal policy:**
- **Output format:**

## 8. Results

| Config | recall@(retriever k) | nDCG@(final k) | MRR | faithfulness | refusal acc | p95 ms | cost/q |
|---|---|---|---|---|---|---|---|
| baseline | | | | | | | |
| current | | | | | | | |

## 9. Experiment log

| Date | Change (one variable) | Metric delta | Keep? | Notes |
|---|---|---|---|---|
| | | | | |

## 10. Open risks & next steps

- 
