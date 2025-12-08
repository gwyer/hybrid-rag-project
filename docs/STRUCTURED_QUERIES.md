# Structured Data Queries

## Problem Statement

Your hybrid RAG system uses embeddings and semantic search, which is great for conceptual queries but **not ideal for structured data queries** like:
- "Count how many people named Michael"
- "Show me all contacts from Company X"
- "How many rows have field Y = value Z"

These queries require **exact matching and counting**, which LLM-based RAG systems struggle with because:
1. Embeddings approximate meaning, not exact values
2. LLMs can't count accurately from chunked documents
3. CSV rows become separate document chunks, losing structure

## Solution: Dual Query System

The system now has **two complementary query engines**:

### 1. Semantic Search (Original RAG)
**Best for:** Conceptual questions, summarization, understanding
- "What are the main topics?"
- "How do I submit PTO?"
- "Explain the vacation policy"

### 2. Structured Queries (New)
**Best for:** Exact counts, filtering, structured data
- "Count people named Michael"
- "Show all contacts from Microsoft"
- "List rows where Position contains 'Engineer'"

## New Tools Available

### `list_datasets`
List all available CSV files with metadata.

```
Output:
Available Datasets:

📊 contacts
   Rows: 24,697
   Columns (7): First Name, Last Name, URL, Email Address, Company, Position, Connected On
```

### `count_by_field`
Count rows where a field matches a value.

**Parameters:**
- `dataset`: CSV filename without extension (e.g., "contacts")
- `field`: Column name (e.g., "First Name")
- `value`: Value to match (case-insensitive, partial match)

**Example:**
```
count_by_field(dataset="contacts", field="First Name", value="Michael")

Output:
Count: 226 out of 24,697 total rows (0.92%)
Sample Results (5 of 226):
[1] First Name: Michael | Last Name: Randel | URL: https://... | Company: Randel Consulting
```

### `filter_dataset`
Get all rows matching a filter criterion.

**Parameters:**
- `dataset`: Dataset name
- `field`: Column to filter on
- `value`: Value to match
- `limit`: Max results (default: 100)

**Example:**
```
filter_dataset(dataset="contacts", field="Company", value="Microsoft", limit=50)

Output:
Found: 45 rows
Showing: 45 rows

[1] First Name: John | Last Name: Doe | Company: Microsoft | Position: Software Engineer
[2] First Name: Jane | Last Name: Smith | Company: Microsoft | Position: Product Manager
...
```

### `get_dataset_stats`
Get metadata and statistics about a dataset.

**Example:**
```
get_dataset_stats(dataset="contacts")

Output:
Dataset: contacts
Total Rows: 24,697
Total Columns: 7
Memory Usage: 3.21 MB
Columns: First Name, Last Name, URL, Email Address, Company, Position, Connected On
Sample Row:
  First Name: Miguel
  Last Name: Feldens
  URL: https://www.linkedin.com/in/miguelfeldens
  Company: 10x Genomics
  Position: Director of Productivity Engineering
```

## Architecture

```
CSV Files → StructuredQueryEngine (pandas)
          ↓
    Direct DataFrame Queries
          ↓
    Exact Counts & Filters
```

vs.

```
Text Files → Document Loader → Embeddings → Vector DB
                                          ↓
                                   Semantic Search
                                          ↓
                                    LLM Answers
```

## Implementation Details

### StructuredQueryEngine
- Uses **pandas** for efficient data manipulation
- Loads CSV files on startup
- Provides exact matching with `str.contains()` (case-insensitive)
- Returns structured results with counts and samples

### Integration with MCP Server
- Initialized during `initialize_rag_system()`
- Runs queries in background thread (`asyncio.to_thread()`)
- Returns formatted text results for Claude

## Use Cases

### Perfect for Structured Queries:
✅ "Count people named Michael"
✅ "Show all contacts from Google"
✅ "How many engineers are in the dataset?"
✅ "List everyone who connected in 2024"
✅ "Find all emails from domain @company.com"

### Perfect for Semantic Search:
✅ "What are the main topics in these documents?"
✅ "Explain the vacation policy"
✅ "How do I submit a request?"
✅ "Summarize the key points"

### Requires Hybrid Approach:
🔄 "How many people work in AI companies?" (semantic to identify AI companies, then count)
🔄 "What roles do Michaels typically have?" (filter for Michaels, then analyze)

## Testing

The system correctly counts 226 people named "Michael" in the contacts.csv file (24,697 total rows).

```bash
# Test from command line
python -c "
from structured_query import StructuredQueryEngine
engine = StructuredQueryEngine('./data')
result = engine.count_by_field('contacts', 'First Name', 'Michael')
print(f'Found {result[\"count\"]} Michaels')
"
# Output: Found 226 Michaels
```

## Performance

- **CSV Loading**: Fast (24K rows in ~1 second)
- **Queries**: Instant (pandas in-memory operations)
- **Memory**: Efficient (3MB for 24K row dataset)
- **Scalability**: Good for datasets up to millions of rows

## Future Enhancements

Potential additions:
- SQL-like queries with pandas `.query()`
- Aggregate functions (SUM, AVG, GROUP BY)
- Multi-field filters (AND/OR conditions)
- Export filtered results to CSV
- Date range queries
- Fuzzy matching for names

## Summary

The structured query engine solves the fundamental limitation of RAG systems with structured data. Now you can:

1. **Use semantic search** for conceptual understanding
2. **Use structured queries** for exact counts and filtering
3. **Get accurate results** for both types of queries

Claude will automatically choose the right tool based on your question!
