# BM25 Explained: Keyword Search in the Hybrid RAG System

## What is BM25?

**BM25** (Best Matching 25) is a **ranking algorithm** used for keyword-based search. It's considered the industry standard for lexical (word-based) search and is used by search engines like Elasticsearch and Lucene.

**Key Point:** BM25 finds documents that contain your **exact search terms** and ranks them by relevance.

---

## BM25 vs Vector Search

Your hybrid RAG system uses **both** methods for better results:

### Vector Search (Semantic)
- **What it does:** Understands meaning and context
- **How it works:** Converts text to numerical vectors (embeddings)
- **Example:** Query "television" finds documents about "TV", "display", "screen"
- **Strength:** Finds similar concepts even with different words
- **Weakness:** May miss exact keyword matches

### BM25 Search (Lexical)
- **What it does:** Finds exact keyword matches
- **How it works:** Counts word occurrences and frequencies
- **Example:** Query "OLED-55-001" finds that exact product ID
- **Strength:** Perfect for exact terms, IDs, product codes
- **Weakness:** Doesn't understand synonyms or meaning

### Hybrid = Best of Both
By combining both, you get:
- ✅ Exact matches for specific terms (BM25)
- ✅ Semantic understanding for concepts (Vector)
- ✅ Better overall retrieval accuracy

---

## How BM25 Works (Simple Explanation)

BM25 scores documents based on:

### 1. **Term Frequency (TF)**
*"How often does the search term appear in this document?"*

- Document with "OLED" mentioned 5 times scores higher than one with "OLED" mentioned once
- But there's **diminishing returns** - 10 mentions isn't 10x better than 1 mention

### 2. **Inverse Document Frequency (IDF)**
*"How rare is this search term across all documents?"*

- Rare terms (like "TV-OLED-55-001") are more valuable
- Common terms (like "the", "and") are less valuable
- This helps find **distinctive** matches

### 3. **Document Length Normalization**
*"Account for document size"*

- Longer documents naturally contain more words
- BM25 normalizes scores so shorter, focused documents aren't penalized

---

## BM25 Formula (For Reference)

```
Score(D,Q) = Σ IDF(qi) × (f(qi,D) × (k1 + 1)) / (f(qi,D) + k1 × (1 - b + b × |D|/avgdl))
```

**Don't worry about the math!** Just know:
- **IDF(qi)** = How rare is query term qi?
- **f(qi,D)** = How often does qi appear in document D?
- **|D|/avgdl** = Document length compared to average
- **k1, b** = Tuning parameters (typically k1=1.5, b=0.75)

---

## How BM25 is Used in This Project

### Implementation Location
**File:** `src/hybrid_rag/hybrid_retriever.py`

### Code Snippets

**Creating BM25 Retrievers:**
```python
from langchain_community.retrievers import BM25Retriever

# Create BM25 retriever from documents
text_bm25_retriever = BM25Retriever.from_documents(text_docs)
text_bm25_retriever.k = 5  # Return top 5 results

csv_bm25_retriever = BM25Retriever.from_documents(csv_docs)
csv_bm25_retriever.k = 5
```

**Hybrid Retrieval Process:**
```python
# This project creates SEPARATE BM25 retrievers for:
# 1. Text/Markdown documents
# 2. CSV documents

# Each is combined with its corresponding vector retriever
text_retriever = EnsembleRetriever(
    retrievers=[text_vector_retriever, text_bm25_retriever],
    weights=[0.5, 0.5]  # Equal weighting
)

csv_retriever = EnsembleRetriever(
    retrievers=[csv_vector_retriever, csv_bm25_retriever],
    weights=[0.5, 0.5]  # Equal weighting
)
```

---

## Architecture Flow

```
User Query: "What is product TV-OLED-55-001?"
         ↓
    ┌────────────────────────────────────────┐
    │   Document Type Aware Retriever        │
    └────────────────────────────────────────┘
         ↓                        ↓
    ┌─────────────┐         ┌─────────────┐
    │ TEXT DOCS   │         │  CSV DOCS   │
    └─────────────┘         └─────────────┘
         ↓                        ↓
    ┌─────────────┐         ┌─────────────┐
    │ Vector (50%)│         │ Vector (50%)│
    │ BM25   (50%)│         │ BM25   (50%)│
    └─────────────┘         └─────────────┘
         ↓                        ↓
    ┌─────────────┐         ┌─────────────┐
    │5 text results│        │5 CSV results │
    └─────────────┘         └─────────────┘
         ↓                        ↓
    ┌────────────────────────────────────────┐
    │   Merge with Weighting                 │
    │   Text: 60%, CSV: 40%                  │
    └────────────────────────────────────────┘
         ↓
    Top 10 Final Results
```

---

## Why This Project Uses Separate BM25 Retrievers

### Design Decision: Split by Document Type

**Text/Markdown BM25:**
- Searches: `.md`, `.txt`, `.pdf`, `.docx` files
- Good for: Concepts, descriptions, policies, feedback
- Example query: "customer complaints about delivery"

**CSV BM25:**
- Searches: `.csv` files only
- Good for: Exact values, product IDs, numbers, dates
- Example query: "TV-OLED-55-001" or "ORD-12345"

### Why Split?

1. **Different Content Structures:**
   - Text: Natural language, paragraphs
   - CSV: Structured data, tabular format

2. **Different Search Needs:**
   - Text: Semantic understanding matters more
   - CSV: Exact matches matter more

3. **Better Relevance:**
   - Prevents CSV rows from overwhelming text results
   - Prevents verbose text from overwhelming precise data

---

## Configuration

BM25 behavior is controlled in `config/config.yaml`:

```yaml
retrieval:
  vector_search_k: 5      # Top 5 from vector search
  keyword_search_k: 5     # Top 5 from BM25 search

document_processing:
  # Weighting between document types
  csv_retriever_weight: 0.4   # 40% weight to CSV results
  text_retriever_weight: 0.6  # 60% weight to text results
```

**What this means:**
- Each retriever (vector + BM25) returns 5 documents
- BM25 and vector are weighted equally (50/50) within each document type
- But CSV results get 40% overall weight vs 60% for text results
- Final output: Top 10 combined results

---

## Example: BM25 in Action

### Query: "OLED TV prices"

**BM25 Text Search:**
```
Document: product_specifications.txt
Match: "...OLED TV models feature..."
Score: 3.2 (found "OLED" and "TV")

Document: market_analysis_2024.md
Match: "...OLED TV market prices are..."
Score: 4.1 (found "OLED", "TV", "prices")
```

**BM25 CSV Search:**
```
Document: product_catalog.csv row 42
Match: "TV-OLED-55-001, OLED TV 55\", $1299.99"
Score: 5.8 (found "OLED" and "TV", exact product match)

Document: supplier_pricing.csv row 108
Match: "PANEL-OLED-55, OLED panel, $450.00"
Score: 3.9 (found "OLED")
```

**Combined with Vector Search:**
- Vector search finds semantically similar docs (might find "television display" even without exact words)
- BM25 finds exact keyword matches
- Results merged and ranked
- Best of both worlds!

---

## When BM25 Shines

BM25 is **especially good** for:

### ✅ Exact Product IDs
```
Query: "TV-OLED-55-001"
→ BM25 finds exact match immediately
→ Vector search might miss this (no semantic meaning in ID)
```

### ✅ Specific Numbers
```
Query: "order ORD-12345"
→ BM25 finds the exact order number
```

### ✅ Technical Terms
```
Query: "BM25 algorithm"
→ BM25 finds exact technical term
→ Vector might find "ranking algorithm" (close, but not exact)
```

### ✅ Rare/Unique Terms
```
Query: "chromaticity"
→ Rare technical term - BM25's IDF scoring helps
```

---

## When BM25 Struggles

BM25 has **limitations** with:

### ❌ Synonyms
```
Query: "television"
→ BM25 won't find docs that only say "TV"
→ Vector search handles this better
```

### ❌ Typos
```
Query: "OELD TV" (typo: OELD instead of OLED)
→ BM25 misses the match
→ Vector search might still find it (embeddings are typo-tolerant)
```

### ❌ Paraphrasing
```
Query: "cheap displays"
→ BM25 won't find "affordable screens" or "budget monitors"
→ Vector search understands these are similar concepts
```

### ❌ Questions
```
Query: "What products are in stock?"
→ BM25 looks for "what", "products", "stock" - common words, low IDF
→ Vector search understands the intent better
```

**This is why we use BOTH!**

---

## Performance Characteristics

### BM25 Advantages:
- ⚡ **Fast**: No neural network computation needed
- 💾 **Lightweight**: Just word counts and frequencies
- 🎯 **Precise**: Perfect for exact term matching
- 📊 **Interpretable**: You can see exactly why a document matched

### BM25 Limitations:
- 🔤 **Literal**: Only finds exact words
- 🌐 **No Context**: Doesn't understand meaning
- 📝 **Vocabulary Gap**: Misses synonyms and related terms

### Hybrid (BM25 + Vector) Benefits:
- ✅ Best of both worlds
- ✅ Handles both exact matches and semantic queries
- ✅ More robust across different query types
- ✅ Higher overall retrieval accuracy

---

## Reciprocal Rank Fusion (RRF)

When combining BM25 and Vector results, this project uses **RRF**:

### What is RRF?

A method to merge ranked lists from different sources.

**Formula:**
```
RRF_score(doc) = Σ 1 / (k + rank_i(doc))
```

Where:
- `rank_i(doc)` = position of doc in retriever i's results
- `k` = constant (usually 60)

### Example:

**BM25 Results:**
1. Doc A (rank 1)
2. Doc B (rank 2)
3. Doc C (rank 3)

**Vector Results:**
1. Doc C (rank 1)
2. Doc A (rank 2)
3. Doc D (rank 3)

**RRF Scores:**
- Doc A: 1/(60+1) + 1/(60+2) = 0.0164 + 0.0161 = **0.0325**
- Doc B: 1/(60+2) = **0.0161**
- Doc C: 1/(60+3) + 1/(60+1) = 0.0159 + 0.0164 = **0.0323**
- Doc D: 1/(60+3) = **0.0159**

**Final Ranking:** A, C, B, D

RRF is implemented automatically by LangChain's `EnsembleRetriever`.

---

## Code Reference: Where BM25 is Used

### 1. Initialization
**File:** `src/hybrid_rag/hybrid_retriever.py:152-165`

```python
# Create BM25 retrievers for each document type
if text_docs:
    text_bm25_retriever = BM25Retriever.from_documents(text_docs)
    text_bm25_retriever.k = keyword_k

if csv_docs:
    csv_bm25_retriever = BM25Retriever.from_documents(csv_docs)
    csv_bm25_retriever.k = keyword_k
```

### 2. Ensemble Creation
**File:** `src/hybrid_rag/hybrid_retriever.py:46-55`

```python
# Create ensemble retrievers for each document type
text_retriever = EnsembleRetriever(
    retrievers=[text_vector_retriever, text_bm25_retriever],
    weights=[0.5, 0.5]  # 50% vector, 50% BM25
)

csv_retriever = EnsembleRetriever(
    retrievers=[csv_vector_retriever, csv_bm25_retriever],
    weights=[0.5, 0.5]
)
```

### 3. Demo Usage
**File:** `scripts/demos/basic.py:96-103`

```python
# Traditional ensemble (when not using document-type-aware)
keyword_retriever = BM25Retriever.from_documents(documents)
keyword_k = config['retrieval']['keyword_search_k']
keyword_retriever.k = keyword_k

hybrid_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, keyword_retriever]
)
```

---

## Tuning BM25 Performance

### Adjusting k (Number of Results)

**In `config/config.yaml`:**
```yaml
retrieval:
  keyword_search_k: 5  # Change this
```

**Effect:**
- **Higher k** (e.g., 10): More BM25 results, better recall, may include less relevant docs
- **Lower k** (e.g., 3): Fewer BM25 results, higher precision, might miss some relevant docs

### Adjusting Ensemble Weights

**In `src/hybrid_rag/hybrid_retriever.py`:**
```python
# Current: Equal weighting
EnsembleRetriever(
    retrievers=[text_vector_retriever, text_bm25_retriever],
    weights=[0.5, 0.5]  # Modify these
)
```

**Options:**
- **[0.7, 0.3]**: Favor vector search (better for semantic queries)
- **[0.3, 0.7]**: Favor BM25 search (better for exact term matching)
- **[0.5, 0.5]**: Balanced (current default)

### When to Favor BM25 More

Increase BM25 weight (e.g., [0.4, 0.6]) if:
- Your queries are often exact product IDs
- Users search for specific numbers or codes
- Exact keyword matching is more important than semantic understanding
- Your documents contain a lot of technical jargon

### When to Favor Vector More

Increase vector weight (e.g., [0.6, 0.4]) if:
- Users ask natural language questions
- Synonyms and related concepts are common
- Semantic understanding is more important
- Users might misspell terms

---

## Summary

### BM25 in One Sentence:
**BM25 is a keyword-based search algorithm that finds documents containing your exact search terms and ranks them by how important those terms are.**

### Why This Project Uses BM25:
1. ✅ **Exact matching** for product IDs, order numbers, specific terms
2. ✅ **Complements vector search** for better overall accuracy
3. ✅ **Fast and lightweight** compared to neural approaches
4. ✅ **Industry standard** - proven and reliable
5. ✅ **Interpretable** - easy to understand why documents matched

### Key Takeaways:
- BM25 = Keyword search (exact words)
- Vector = Semantic search (meaning)
- Hybrid = Best of both
- This project uses **separate BM25 retrievers** for text vs CSV documents
- Results are merged using RRF (Reciprocal Rank Fusion)
- You can tune BM25 behavior via `config/config.yaml`

---

## Further Reading

- **Wikipedia:** [Okapi BM25](https://en.wikipedia.org/wiki/Okapi_BM25)
- **Original Paper:** Robertson & Walker (1994) - "Some simple effective approximations to the 2-Poisson model"
- **LangChain Docs:** [BM25Retriever](https://python.langchain.com/docs/integrations/retrievers/bm25)
- **This Project's Architecture:** `docs/architecture/system-design.md`

---

## Related Documentation

- **[System Design](../architecture/system-design.md)** - Full architecture details
- **[Testing Strategy](testing-strategy.md)** - How to validate retrieval
- **[Quick Start](../getting-started/quick-start.md)** - Get started using the system
