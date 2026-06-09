# RAG Component Catalog

A decision-oriented catalog of the components at each pipeline stage. Pick by fit, not by hype. Verify current model names, dimensions, and limits against vendor docs at build time — specifics change.

## 1. Document loaders & parsers

| Source | Concern | Approach |
|---|---|---|
| PDF | Layout, tables, multi-column, scanned | Layout-aware parser; OCR for scans; extract tables separately |
| HTML | Boilerplate (nav, ads), structure | Strip boilerplate, keep heading hierarchy |
| Markdown | Already structured | Parse headers for header-aware chunking |
| Office docs | Embedded tables/images | Convert to Markdown/text, preserve headings |
| Code | Syntax, symbols | AST/tree-sitter split by function/class |
| Transcripts | Speaker turns, timestamps | Keep speaker + time metadata |

Parsing quality caps the whole pipeline. Garbage extraction (merged columns, dropped tables) cannot be fixed downstream.

## 2. Chunking strategies

- **Fixed-size (token/char):** simplest; ignores structure; use only as a baseline.
- **Recursive character/token split:** split on a priority list of separators (paragraph, newline, sentence, space). Good general default.
- **Header/structure-aware:** split on Markdown/HTML headings; keep the heading text in each chunk. Best for documentation.
- **Semantic chunking:** split where adjacent sentence embeddings diverge past a threshold. Higher quality, higher cost; good for unstructured prose.
- **Sentence-window / parent-document:** embed small chunks for precise retrieval, but return a larger surrounding window or the parent section to the LLM for context. Excellent recall/precision tradeoff.
- **Proposition / atomic-fact:** decompose into standalone factual statements. Maximum precision; expensive to build.

Parameters to tune: size (tokens), overlap (10-20% typical), and a self-context prefix (title/section).

## 3. Embedding models

Selection criteria, in priority order:
1. **Domain & language match** — general vs code vs biomedical vs multilingual.
2. **Max sequence length** — must exceed your chunk size or chunks get truncated.
3. **Dimension** — higher dims = more storage and slower search; often diminishing returns. Check if the model supports dimension truncation (Matryoshka).
4. **Asymmetric support** — some models have separate query vs document encodings/prefixes; use them.
5. **Cost & latency** — hosted API vs self-hosted open weights.
6. **MTEB / domain benchmark scores** — a starting filter, not a guarantee for your corpus.

Always normalize vectors if using cosine similarity. Re-embed the entire corpus when changing models — never mix embedding spaces.

## 4. Sparse / lexical retrieval

- **BM25 / BM25F:** classic keyword scoring; unbeatable for exact terms, IDs, codes, rare words. Cheap. Pair with dense.
- **Learned sparse (e.g. SPLADE-style):** expands terms via a model; bridges lexical/semantic gap; needs a compatible index.

## 5. Vector indexes

| Index | When | Notes |
|---|---|---|
| Flat (brute force) | < ~100k vectors | Exact, simple, fast enough at small scale |
| HNSW | 100k-10M+ | Great recall/latency; higher memory; default for scale |
| IVF / IVF-PQ | Very large, memory-constrained | Approximate; tune nprobe; PQ compresses at accuracy cost |
| Disk-based ANN | Billions | For corpora that exceed RAM |

Vector stores range from embedded libraries (in-process) to managed services with metadata filtering, hybrid search, and multi-tenancy built in. Choose based on scale, ops appetite, filtering needs, and whether you want hybrid search natively.

## 6. Retrieval enhancers

- **Reciprocal Rank Fusion (RRF):** combine dense + sparse rankings without score calibration. Safe default for hybrid. score = sum 1/(k + rank), k~60.
- **Query rewriting:** LLM rewrites a vague/conversational query into a search-optimized one.
- **HyDE (Hypothetical Document Embeddings):** LLM drafts a hypothetical answer, embed that, search with it. Helps when queries are short and unlike documents.
- **Multi-query expansion:** generate N paraphrases, retrieve for each, union results. Helps recall/multi-hop.
- **Metadata filtering:** restrict by source, date, product, permissions. Apply pre-filter (filter then search) when the index supports it.

## 7. Rerankers

- **Cross-encoder reranker:** jointly encodes (query, chunk) for a relevance score. Much more accurate than the bi-encoder retriever, but O(candidates) model calls — so rerank only the top 20-50. Highest-ROI quality lever after chunking.
- **LLM reranker:** prompt an LLM to score/order candidates. Flexible, slower, costlier.
- **Maximal Marginal Relevance (MMR):** re-rank for relevance + diversity to cut redundant chunks.

## 8. Context assembly

- Deduplicate near-identical chunks (e.g. high cosine similarity).
- Order by relevance; consider placing the strongest chunk first AND last (edge attention / lost-in-the-middle).
- Include per-chunk attribution (source id, title, url) so the model can cite.
- Budget tokens: reserve room for the answer; truncate the lowest-ranked chunks first.

## 9. Generation

- System prompt: "Answer only using the provided context. If the context is insufficient, say you don't know. Cite sources by id."
- Low temperature for factual QA.
- Optional: structured output with a `sources` field; refuse-or-cite enforcement; a verification pass that checks each claim against context.
