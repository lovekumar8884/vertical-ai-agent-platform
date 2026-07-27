# KNOWLEDGE BASE (RAG)

## 1. Objectives

- **High-quality grounding** (answers cite sources, refuse when unsure).
- **Fast retrieval** (p95 < 150 ms).
- **Multi-source** (files, URLs, apps, DBs, streaming).
- **Incremental & idempotent** (only changed content is reprocessed).
- **Multi-tenant** with strict isolation.
- **Multilingual** and **hybrid** (BM25 + vector + reranker).

## 2. Concepts

```
Tenant
 └── Corpus (embedding config, chunking config, ACL tags)
      └── Document (source ref, checksum, status)
           └── Chunk (text, tokens, vector, payload)
```

## 3. Sources & Connectors

| Source | Method |
|--------|--------|
| File upload | Direct multipart to S3 → ingest job |
| URL / sitemap | Playwright crawler with respect for robots.txt |
| Google Drive / Notion / Confluence | OAuth + delta sync |
| Zendesk / Intercom / Freshdesk | API sync (tickets → chunks) |
| Databases (SQL) | Scheduled query → JSONL |
| SharePoint / OneDrive | Graph API + change tokens |
| GitHub / GitLab | Webhook + repo clone (docs/wiki) |
| Streaming | Webhook or Kafka topic subscription |

## 4. Ingestion Pipeline (Temporal Workflow)

```
1. Fetch/receive source blob → S3
2. Detect MIME type
3. Parse:
   - PDF: Unstructured / pdfplumber + OCR fallback (Tesseract, Marker)
   - DOCX/PPTX/XLSX: Unstructured / python-docx
   - HTML: Trafilatura (content extraction)
   - Markdown: python-markdown-it
   - Audio: Whisper transcription → text
   - Images: BLIP-2 captioning + OCR
4. Layout parsing (for PDFs with tables/columns): Marker or LlamaParse
5. Semantic chunking:
   - Default: recursive character (target 1000 tokens, overlap 100)
   - Vertical-specific: header-aware (medical, legal)
   - Table-aware: keep rows together
6. Metadata enrichment: title, author, section path, page number
7. Embedding: batch call to embeddings service
8. Upsert to Qdrant (idempotent by chunk_id)
9. Write chunks to Postgres for source-of-truth + BM25
10. Emit document.indexed event
```

- Every step retried with exponential backoff.
- Failures create a **document error record** visible in console with fix hints.

## 5. Chunking Strategy

- **Default**: Recursive character splitter, 1000 tokens ± 100 overlap.
- **Header-aware**: split on H1/H2 for structured docs.
- **Semantic** (optional): use sentence embeddings + clustering (LlamaIndex's `SemanticSplitterNodeParser`).
- **Table extraction**: tables → markdown → separate chunks + linked to parent.
- **Contextual chunk enrichment** (Anthropic's technique): prepend LLM-generated summary of chunk's position in doc → improves retrieval ~20%.

## 6. Embedding Models

| Tier | Model | Dim | Notes |
|------|-------|-----|-------|
| Shared (SaaS) | `text-embedding-3-large` (OpenAI) | 3072 (project to 1024 via MRL) | Best quality / cost balance |
| SaaS multilingual | `text-embedding-3-large` or Cohere `embed-multilingual-v3` | 1024 | 100+ languages |
| Self-host / on-prem | `BAAI/bge-m3` | 1024 | SOTA open, dense+sparse+colbert |
| Domain-tuned | Fine-tuned BGE per vertical | 1024 | Optional |

- Batch size tuned per provider (128 default).
- **Dimension reduction** via Matryoshka to shrink storage 3x with minimal quality loss.

## 7. Retrieval

- **Hybrid**: BM25 (Postgres `tsvector` or OpenSearch) + dense vector (Qdrant) + optional sparse (SPLADE) → **reciprocal rank fusion (RRF)**.
- **Reranker** (top 30 → top 6): Cohere Rerank v3, or self-host `BAAI/bge-reranker-v2-m3`.
- Multi-query expansion (LLM generates 3–5 paraphrases → union → rerank).
- **HyDE** (Hypothetical Document Embeddings) optional per corpus.
- **Query filters** always include `tenant_id`; optional filters: `corpus_id`, `document_type`, `updated_after`, ACL tags.

## 8. RAG Answer Generation

Prompt strategy:
- Include top-K snippets with **source metadata** (title, URL, page).
- Force **citation format**: `[1]`, `[2]` at sentence level.
- **Grounding check**: post-generation, an LLM-judge verifies each citation-supported claim. Unsupported claims → strip or refuse.
- **Refusal**: if best chunk score < threshold OR grounding fails, respond with "I don't have that information" + optional handoff.

## 9. Freshness

- Delta sync per connector (daily default; hourly for premium).
- Webhook-driven immediate updates where source supports.
- **TTL on chunks** for time-sensitive corpora (news, pricing).
- Recrawl policy: `if-modified-since` + checksum comparison → skip unchanged.

## 10. Isolation

- Per-tenant Qdrant collections for Dedicated tier.
- Payload-filtered shared collections for Shared tier.
- **ACL tags** on chunks (e.g., `dept:finance`, `role:admin`) → query-time filter based on end-user's identity/role (RBAC-aware retrieval).

## 11. Observability

- Per-query trace: latency, retrieved chunks (ids + scores), reranker verdicts, final citations.
- **Retrieval eval** offline suite: gold Q → gold-doc; measure hit@k, MRR, nDCG.
- **Answer eval**: LLM-as-judge for faithfulness, relevance, completeness.

## 12. Governance
- Document status: `pending`, `processing`, `indexed`, `failed`, `stale`, `deleted`.
- Console shows per-document processing timeline + errors.
- **Deletion** removes chunks from Qdrant and Postgres in the same Temporal workflow; verifiable via audit.
- **Redaction**: PII detected during ingestion optionally masked or dropped per policy.

## 13. Advanced Modes (per corpus)
- **GraphRAG** (Microsoft) for entity/relation-heavy corpora (legal, medical guidelines).
- **Agentic RAG** — retrieval as a tool the agent calls iteratively (multi-hop).
- **Structured output RAG** — return typed rows instead of prose (for lookups).

## 14. Anti-Patterns Rejected
- ❌ Chunk-and-pray without reranking.
- ❌ Ignoring metadata (throws away high-signal filters).
- ❌ One giant collection for all tenants (isolation risk).
- ❌ Answer without citations (opaque to reviewers).
- ❌ Recomputing embeddings on every re-ingest (checksum first).

## 15. Assumptions
- Qdrant remains a strong open-source choice; we're OK with the operational lift vs. managed pgvector.
- Reranker cost is worth the ~15–25% quality bump for most verticals.
- Contextual chunk enrichment is worth its ~2x ingestion cost for professional/legal/medical corpora.
