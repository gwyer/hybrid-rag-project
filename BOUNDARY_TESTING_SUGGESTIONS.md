# Boundary Testing Suggestions for Hybrid RAG System

This document outlines comprehensive approaches to test the limits and boundaries of the Hybrid RAG system.

## Current Testing (In Progress)

### 1. **Large-Scale Data Ingestion** ✓ COMPLETE
- **41,000+ records** across 13 files
- CSV files: 41,000 rows
- Markdown files: 2,500+ sections
- Text files: 1,000+ specifications
- **Tests:** Load time, memory usage, chunking performance

### 2. **Vector Embedding Performance** ⏳ RUNNING
- Embedding generation speed
- ChromaDB performance at scale
- Memory consumption during indexing
- Throughput (embeddings/second)

### 3. **Retrieval Performance** ⏳ RUNNING
- Query latency at scale
- Accuracy with large document sets
- Hybrid search effectiveness
- Cross-document query performance

### 4. **End-to-End QA Performance** ⏳ RUNNING
- Response time with large context
- Answer quality at scale
- LLM performance with extensive retrieved context

---

## Additional Boundary Testing Recommendations

### Data Volume & Variety

#### 5. **Maximum Document Count**
```python
# Test with incrementally larger datasets
test_sizes = [1000, 5000, 10000, 50000, 100000, 500000]

for size in test_sizes:
    - Measure load time
    - Measure query performance
    - Track memory usage
    - Identify breaking point
```

**Expected Limits:**
- ChromaDB: Millions of vectors (memory-dependent)
- BM25: Thousands of documents (performance degrades)
- System memory: Primary constraint

#### 6. **Document Size Limits**
```python
# Test individual file sizes
test_cases = [
    "1 KB text file",
    "100 KB CSV",
    "1 MB markdown",
    "10 MB PDF",
    "50 MB combined dataset",
    "100 MB+ dataset"
]
```

**What to Test:**
- Maximum single file size
- Total dataset size limits
- Memory exhaustion points
- Chunking performance degradation

#### 7. **Chunk Count Stress Test**
```python
# Very small chunk sizes to maximize chunk count
chunk_sizes = [100, 250, 500, 1000, 2000]
chunk_overlaps = [0, 50, 100, 200, 400]

# Test combinations
- Measure embedding time
- Measure storage size
- Test retrieval accuracy vs. performance tradeoff
```

---

### Query Complexity

#### 8. **Query Length Limits**
```python
query_lengths = [
    "5 words",
    "50 words",
    "200 words",  # Paragraph
    "1000 words", # Essay
    "5000 words"  # Document-length query
]
```

**Metrics:**
- Embedding time for long queries
- Retrieval accuracy
- Response degradation

#### 9. **Concurrent Query Load**
```python
# Simulate multiple users
concurrent_users = [1, 5, 10, 25, 50, 100]

for users in concurrent_users:
    - Spawn concurrent queries
    - Measure average latency
    - Measure throughput (queries/sec)
    - Identify bottlenecks
```

**Use threading or asyncio:**
```python
import asyncio
import concurrent.futures

async def stress_test_queries(num_concurrent=10):
    tasks = [query_system(test_query) for _ in range(num_concurrent)]
    results = await asyncio.gather(*tasks)
    return analyze_results(results)
```

#### 10. **Retrieval K Parameter Sweep**
```python
k_values = [1, 5, 10, 20, 50, 100, 500]

for k in k_values:
    - Measure retrieval time
    - Measure answer quality
    - Find optimal k value
    - Identify diminishing returns
```

---

### Memory & Resource Limits

#### 11. **Memory Pressure Testing**
```python
# Monitor memory usage
import psutil

def memory_stress_test():
    baseline = psutil.virtual_memory().available

    # Load incrementally larger datasets
    while memory_available():
        load_more_documents()
        current_mem = psutil.virtual_memory().available

        if current_mem < (baseline * 0.1):  # 90% used
            break

    return max_documents_loaded
```

**What to Monitor:**
- RSS (Resident Set Size)
- Peak memory usage
- Memory leaks during repeated operations
- Garbage collection performance

#### 12. **Disk I/O Limits**
```python
# Test ChromaDB persistence performance
test_operations = [
    "Sequential writes",
    "Random writes",
    "Bulk inserts",
    "Index rebuilds",
    "Persistence frequency"
]

# Measure:
- Write throughput (MB/s)
- Read latency
- Index size growth
- Compaction performance
```

#### 13. **CPU Utilization**
```python
# Multi-core performance
import multiprocessing

# Test parallel document processing
num_workers = [1, 2, 4, 8, 16]

for workers in num_workers:
    with multiprocessing.Pool(workers) as pool:
        results = pool.map(process_document, documents)
        measure_speedup()
```

---

### Edge Cases & Error Handling

#### 14. **Malformed Data**
```python
edge_cases = [
    "Empty files",
    "Files with only whitespace",
    "CSV with mismatched columns",
    "Markdown with invalid syntax",
    "Binary data in text files",
    "Files with special characters (emoji, unicode)",
    "Extremely long lines (no line breaks)",
    "Files with BOM markers",
    "Mixed encodings (UTF-8, Latin-1, ASCII)"
]
```

**Expected Behavior:**
- Graceful error handling
- Informative error messages
- System continues with valid files
- No crashes or data corruption

#### 15. **Network Failure Simulation**
```python
# Test Ollama connection failures
test_scenarios = [
    "Ollama server down",
    "Network timeout",
    "Slow network (add latency)",
    "Intermittent connectivity",
    "Model not available"
]

# Implement retry logic
# Test fallback mechanisms
# Measure recovery time
```

#### 16. **Race Conditions**
```python
# Concurrent writes to vector store
async def test_concurrent_writes():
    writers = [
        write_to_vectorstore(docs_batch_1),
        write_to_vectorstore(docs_batch_2),
        write_to_vectorstore(docs_batch_3)
    ]

    # Test data consistency
    # Verify no corruption
    # Check for lock contention
```

---

### Performance Degradation Analysis

#### 17. **Time Complexity Analysis**
```python
# Measure O(n) behavior
dataset_sizes = [100, 500, 1000, 5000, 10000, 50000]

for size in dataset_sizes:
    load_time = measure_load(size)
    query_time = measure_query(size)

    # Plot:
    # - Load time vs dataset size
    # - Query time vs dataset size
    # - Determine complexity class
```

**Expected Results:**
- Document loading: O(n)
- Embedding generation: O(n)
- Vector search: O(log n) or O(√n)
- BM25 search: O(n) but optimized

#### 18. **Cache Performance**
```python
# Test repeated queries (cache hit rate)
queries = generate_test_queries(1000)

# First pass (cold cache)
cold_times = [query(q) for q in queries]

# Second pass (warm cache)
warm_times = [query(q) for q in queries]

cache_speedup = mean(cold_times) / mean(warm_times)
```

---

### Accuracy & Quality Metrics

#### 19. **Retrieval Accuracy at Scale**
```python
# Create ground truth dataset
ground_truth = [
    {"query": "...", "relevant_docs": [...]},
    # ... 100+ test cases
]

# Measure:
metrics = {
    "Precision@k": precision_at_k(results, ground_truth),
    "Recall@k": recall_at_k(results, ground_truth),
    "MRR": mean_reciprocal_rank(results, ground_truth),
    "NDCG": normalized_discounted_cumulative_gain(results, ground_truth)
}
```

#### 20. **Answer Quality vs. Dataset Size**
```python
# Hypothesis: Answer quality may degrade with more irrelevant documents

dataset_sizes = [100, 1000, 10000, 100000]

for size in dataset_sizes:
    answers = query_system(test_questions, dataset_size=size)

    # Measure:
    - Accuracy (human evaluation)
    - Relevance scores
    - Hallucination rate
    - Answer confidence
```

---

### Real-World Scenarios

#### 21. **Continuous Ingestion Simulation**
```python
# Simulate documents being added over time
async def continuous_ingestion():
    while True:
        new_docs = fetch_new_documents()
        add_to_vectorstore(new_docs)
        await asyncio.sleep(60)  # Every minute

        # Test:
        - Query performance degradation
        - Index fragmentation
        - Memory growth
```

#### 22. **Mixed Workload Testing**
```python
# Realistic usage patterns
workload = {
    "60% simple queries": simple_queries,
    "30% complex queries": complex_queries,
    "5% document additions": add_operations,
    "5% document deletions": delete_operations
}

# Run for extended period (hours/days)
# Monitor:
- Average latency
- P50, P95, P99 latency percentiles
- Error rates
- Resource usage trends
```

#### 23. **Multi-Tenant Simulation**
```python
# Separate vector stores per tenant
num_tenants = [10, 50, 100, 500]

for tenants in num_tenants:
    # Create isolated environments
    # Test resource isolation
    # Measure overhead
    # Test cross-tenant query prevention
```

---

### Failure & Recovery Testing

#### 24. **Crash Recovery**
```python
# Test scenarios:
test_cases = [
    "Crash during embedding generation",
    "Crash during vector store write",
    "Crash during query processing",
    "Disk full during persistence",
    "OOM kill during large batch"
]

# Verify:
- Data consistency after recovery
- No corrupted indices
- Ability to resume operations
```

#### 25. **Data Consistency Verification**
```python
def verify_consistency():
    # Count documents
    expected_docs = count_source_documents()
    indexed_chunks = count_vectorstore_chunks()

    # Verify all documents retrievable
    for doc_id in all_document_ids:
        results = query_by_id(doc_id)
        assert len(results) > 0, f"Document {doc_id} not retrievable"

    # Verify no duplicates
    all_ids = get_all_chunk_ids()
    assert len(all_ids) == len(set(all_ids)), "Duplicate chunks detected"
```

---

## Automated Testing Framework

### Test Suite Structure

```python
class BoundaryTestSuite:
    def __init__(self):
        self.results = {}

    def run_all_tests(self):
        # Data volume tests
        self.test_max_documents()
        self.test_max_file_size()
        self.test_max_chunks()

        # Performance tests
        self.test_concurrent_queries()
        self.test_query_complexity()
        self.test_memory_limits()

        # Quality tests
        self.test_retrieval_accuracy()
        self.test_answer_quality()

        # Failure tests
        self.test_error_handling()
        self.test_crash_recovery()

        # Generate report
        self.generate_comprehensive_report()
```

---

## Recommended Tools

### Performance Monitoring
- **psutil**: CPU, memory, disk I/O monitoring
- **py-spy**: Python profiling
- **memory_profiler**: Line-by-line memory usage
- **cProfile**: Function-level performance profiling

### Load Testing
- **locust**: Distributed load testing
- **pytest-benchmark**: Microbenchmarking
- **asyncio**: Concurrent operation testing

### Metrics & Visualization
- **matplotlib/plotly**: Performance graphs
- **pandas**: Data analysis
- **Jupyter**: Interactive analysis notebooks

---

## Success Criteria

### Performance Targets
- **Load time**: < 1 second per 1000 documents
- **Query latency**: < 500ms for 95th percentile
- **Throughput**: > 10 queries/second
- **Memory efficiency**: < 1 GB per 10,000 documents

### Scalability Targets
- **Support 100,000+ documents**
- **Handle 50+ concurrent users**
- **Process 1 GB+ of text data**
- **Maintain <5% error rate under load**

### Quality Targets
- **Retrieval Precision@10**: > 80%
- **Answer Relevance**: > 90%
- **Zero crashes under normal load**
- **<1% data loss during failures**

---

## Next Steps

1. ✓ Run current boundary test suite (41K records)
2. Implement concurrent query testing
3. Add memory pressure tests
4. Create continuous ingestion simulation
5. Build automated regression test suite
6. Document performance baselines
7. Create performance tuning guide

---

## Additional Test Scenarios to Consider

### 26. **Different Document Distributions**
```python
# Test with skewed data
distributions = [
    "All CSV (structured only)",
    "All Markdown (unstructured only)",
    "Mixed (current)",
    "Heavy text (95% markdown)",
    "Heavy CSV (95% structured)"
]
```

### 27. **Query Pattern Analysis**
```python
# Real user behavior
patterns = [
    "Bursty traffic (peak hours)",
    "Sustained high load",
    "Gradual ramp-up",
    "Query diversity analysis",
    "Repeat query percentage"
]
```

### 28. **Storage Efficiency**
```python
# Measure compression and deduplication
metrics = {
    "Raw data size": measure_source_size(),
    "Indexed size": measure_vectorstore_size(),
    "Compression ratio": calculate_ratio(),
    "Duplicate chunk percentage": find_duplicates()
}
```

---

## Conclusion

This comprehensive boundary testing approach will help you:

1. **Identify system limits** before production deployment
2. **Optimize performance** for real-world workloads
3. **Ensure reliability** under stress conditions
4. **Document capacity planning** requirements
5. **Build confidence** in scalability

The current test with 41,000+ records is an excellent start. Consider implementing the additional tests above to fully understand your system's capabilities and limitations.
