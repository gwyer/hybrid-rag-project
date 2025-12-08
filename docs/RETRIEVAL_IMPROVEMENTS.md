# Retrieval Performance Improvements

## Problem Identified

The hybrid RAG system was showing **excellent performance for CSV/structured data** but **poor performance for text/markdown documents**. Test results showed:

### ✅ Excellent CSV Retrieval
- Product pricing (product_catalog.csv)
- Inventory levels (inventory_levels.csv)
- Warranty claims (warranty_claims_q4.csv)
- Production schedule (production_schedule_dec2024.csv)
- Sales orders (sales_orders_november.csv)
- Supplier pricing (supplier_pricing.csv)

### ⚠️ Poor Text/Markdown Retrieval
- Customer feedback (customer_feedback_q4_2024.md) - NOT retrieved
- Market analysis (market_analysis_2024.md) - NOT retrieved
- Return policy (return_policy_procedures.md) - NOT retrieved
- Quality control report (quality_control_report_nov2024.md) - PARTIAL retrieval

## Root Causes

1. **Chunking Strategy Mismatch**
   - CSV files were being loaded row-by-row (optimal for structured data)
   - Markdown files were not being chunked, leading to large, diluted semantic relevance

2. **Retrieval Limit Too Low**
   - Only k=2 for both vector and keyword search (4 total results)
   - CSV results dominated due to row-level granularity

3. **No Document Type Awareness**
   - Single ensemble retriever treated all documents equally
   - No weighting between structured vs unstructured data

4. **Embedding Bias**
   - nomic-embed-text may weight structured data patterns higher
   - No balancing mechanism for document types

## Implemented Solutions

### 1. Enhanced Document Chunking (src/hybrid_rag/document_loader.py)

**Text/Markdown Documents:**
```python
# Configuration (config/config.yaml)
document_processing:
  text_chunk_size: 1000      # Characters per chunk
  text_chunk_overlap: 200    # Overlap for context continuity
```

**Benefits:**
- Smaller, focused chunks improve semantic relevance
- Overlap preserves context across chunk boundaries
- Better matching for specific queries

**CSV Documents:**
- Kept as-is (row-level granularity is optimal)
- Tagged with `doc_category: 'structured'`

### 2. Increased Retrieval Limits (config/config.yaml)

**Before:**
```yaml
retrieval:
  vector_search_k: 2
  keyword_search_k: 2
```

**After:**
```yaml
retrieval:
  vector_search_k: 5   # 2.5x increase
  keyword_search_k: 5   # 2.5x increase
```

**Benefits:**
- More diverse results (up to 10 chunks per retriever)
- Higher chance of capturing both CSV and text results
- Better coverage for complex queries

### 3. Document-Type-Aware Retriever (src/hybrid_rag/hybrid_retriever.py)

**New Architecture:**
```
Query
  ├── Text Document Pipeline (60% weight)
  │   ├── Vector Search (text docs only)
  │   └── BM25 Search (text docs only)
  │   └── Ensemble (RRF)
  │
  └── CSV Document Pipeline (40% weight)
      ├── Vector Search (CSV docs only)
      └── BM25 Search (CSV docs only)
      └── Ensemble (RRF)

Final Results: Merge with position-based scoring + weights
```

**Configuration:**
```yaml
document_processing:
  use_separate_retrievers: true  # Enable new retriever
  text_retriever_weight: 0.6     # 60% weight to text results
  csv_retriever_weight: 0.4      # 40% weight to CSV results
```

**Benefits:**
- **Guaranteed diversity**: Both document types represented
- **Balanced results**: 60/40 split ensures text docs aren't drowned out
- **Separate optimization**: Each retriever optimized for its document type
- **Configurable weighting**: Adjust based on your data distribution

### 4. Metadata Enrichment

All documents now tagged with:
```python
doc.metadata['doc_category'] = 'text'       # or 'structured'
doc.metadata['retrieval_score'] = 0.85      # Position + weight
doc.metadata['retrieval_source'] = 'text_retriever'
```

**Benefits:**
- Filter retrievers by document type
- Debug retrieval performance
- Analyze which retriever found each result

## Configuration Guide

### Option 1: Use New Retriever (Recommended)

```yaml
# config/config.yaml
retrieval:
  vector_search_k: 5
  keyword_search_k: 5

document_processing:
  text_chunk_size: 1000
  text_chunk_overlap: 200
  use_separate_retrievers: true
  text_retriever_weight: 0.6
  csv_retriever_weight: 0.4
```

### Option 2: Traditional Retriever (Backward Compatible)

```yaml
# config/config.yaml
retrieval:
  vector_search_k: 5
  keyword_search_k: 5

document_processing:
  text_chunk_size: 1000
  text_chunk_overlap: 200
  use_separate_retrievers: false  # Disable new retriever
```

## Tuning Recommendations

### If CSV Results Still Dominate

Increase text weight:
```yaml
text_retriever_weight: 0.7
csv_retriever_weight: 0.3
```

### If Text Results Dominate

Increase CSV weight:
```yaml
text_retriever_weight: 0.5
csv_retriever_weight: 0.5
```

### For Very Long Documents

Increase chunk size:
```yaml
text_chunk_size: 1500
text_chunk_overlap: 300
```

### For More Results

Increase k values:
```yaml
vector_search_k: 8
keyword_search_k: 8
```

### For Mostly CSV Data

```yaml
text_retriever_weight: 0.3
csv_retriever_weight: 0.7
```

### For Mostly Text Data

```yaml
text_retriever_weight: 0.8
csv_retriever_weight: 0.2
```

## Testing the Improvements

### 1. Restart Claude Desktop

After changing config:
```bash
# Kill and restart Claude Desktop
# On macOS: Cmd+Q then reopen
```

### 2. Re-ingest Documents

```python
# In Claude Desktop
"Use the ingest_documents tool to reload the data with new chunking"
```

### 3. Test Queries

Try the same queries that failed before:
- "What does the customer feedback say about quality?"
- "Summarize the market analysis findings"
- "What is our return policy procedure?"
- "Show quality control issues from November"

### 4. Analyze Results

Check the retrieved context:
- Look for markdown file sources
- Verify both CSV and text results appear
- Check `retrieval_source` metadata

## Expected Improvements

### Before Changes
- **CSV queries**: ✅ Excellent (6/6 success)
- **Text queries**: ⚠️ Poor (1/4 partial success)
- **Overall**: 70% success rate

### After Changes (Expected)
- **CSV queries**: ✅ Excellent (maintained)
- **Text queries**: ✅ Good to Excellent (4/4 success expected)
- **Overall**: 95%+ success rate

## Performance Metrics

### Chunk Statistics
```
Text Documents:
  - Before: 1 chunk per file (large, unfocused)
  - After: ~3-10 chunks per file (focused, relevant)

CSV Documents:
  - Before: N rows as N chunks (optimal)
  - After: Same (no change needed)
```

### Retrieval Coverage
```
Before:
  - Max results: 4 (2 vector + 2 keyword)
  - Typical: 60-80% CSV, 20-40% text

After:
  - Max results: 10 (5 vector + 5 keyword per retriever)
  - Guaranteed: 60% text, 40% CSV (with weighting)
```

## Troubleshooting

### Still Not Retrieving Text Documents?

1. **Verify chunking is enabled:**
   ```bash
   # Check document count increased after chunking
   # Before: 10 documents
   # After: 50+ documents (includes chunks)
   ```

2. **Check metadata:**
   ```python
   # In query results, verify:
   doc.metadata['doc_category'] == 'text'
   ```

3. **Increase text weight:**
   ```yaml
   text_retriever_weight: 0.8
   csv_retriever_weight: 0.2
   ```

### CSV Results Disappeared?

1. **Verify CSV weight:**
   ```yaml
   csv_retriever_weight: 0.4  # At least 0.3
   ```

2. **Check CSV documents exist:**
   ```python
   # Should see:
   doc.metadata['doc_category'] == 'structured'
   ```

### Query Performance Slow?

1. **Reduce k values:**
   ```yaml
   vector_search_k: 3
   keyword_search_k: 3
   ```

2. **Disable separate retrievers temporarily:**
   ```yaml
   use_separate_retrievers: false
   ```

## Version History

- **v2.1.0** (Current)
  - Added document-type-aware retriever
  - Implemented text chunking
  - Increased default k values
  - Added configurable weighting

- **v2.0.0**
  - Original hybrid RAG implementation
  - Single ensemble retriever
  - No chunking for text documents

## References

- Document Loader: `src/hybrid_rag/document_loader.py`
- Hybrid Retriever: `src/hybrid_rag/hybrid_retriever.py`
- Configuration: `config/config.yaml`
- MCP Server: `scripts/mcp_server_claude.py`
- Demo Script: `scripts/run_demo.py`
