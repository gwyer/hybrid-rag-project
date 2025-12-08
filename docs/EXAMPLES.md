# Example Documents and Queries

This directory contains example documents to test the Hybrid RAG system.

## Sample Files Included

### 1. sample.txt
Basic text file demonstrating the system's features and capabilities.

**Good queries:**
- "What are the key features of the hybrid RAG system?"
- "How do I use the system?"
- "What file formats are supported?"

### 2. test_document.md
Markdown file with structured content about async ingestion.

**Good queries:**
- "How does async ingestion work?"
- "What are the benefits of progress tracking?"
- "What stages are there in the ingestion process?"

### 3. contacts.csv (if you added it)
Structured CSV data with contact information.

**Good structured queries:**
- "List available datasets"
- "Count people named Michael in contacts"
- "Show me all contacts from Microsoft"
- "Get stats for the contacts dataset"

**Good semantic queries:**
- "What companies appear most frequently?"
- "Summarize the types of positions"

## Example Workflows

### Workflow 1: Text Document Analysis

```bash
# Add your documents
cp ~/Documents/reports/*.pdf data/

# Run the system
python hybrid_rag.py
```

Sample queries to ask:
- "Summarize the main topics in these documents"
- "What are the key findings?"
- "Explain [specific concept]"

### Workflow 2: CSV Data Analysis

```bash
# Add CSV files
cp ~/data.csv data/

# Using Claude Desktop MCP
```

In Claude:
1. "List datasets" → See what's available
2. "Get stats for [dataset]" → See columns and sample data
3. "Count rows where [field] equals [value]" → Get exact counts
4. "Show all records where [criteria]" → Filter and retrieve

### Workflow 3: Mixed Document Types

```bash
# Add various formats
cp ~/docs/*.txt data/
cp ~/docs/*.pdf data/
cp ~/data/*.csv data/
```

Use both query types:
- **Semantic**: For PDFs and text files (conceptual questions)
- **Structured**: For CSV files (exact counts, filtering)

## Sample Questions by Document Type

### For Text/PDF/Markdown (Semantic Search)
✅ "What is the main argument of this document?"
✅ "Summarize the key points"
✅ "How does X relate to Y?"
✅ "Explain the methodology described"
✅ "What recommendations are made?"

❌ "How many times is 'algorithm' mentioned?" (Use grep instead)
❌ "Count paragraphs" (Not designed for counting)

### For CSV Files (Structured Queries)
✅ "Count people named John"
✅ "Show all entries from Company X"
✅ "How many rows have Position containing 'Engineer'?"
✅ "List unique company names"
✅ "Get all records where Email contains @gmail.com"

❌ "What do these people typically do?" (Use semantic search)
❌ "Summarize the career paths" (Better with semantic search)

### Hybrid Approach
For complex questions, combine both:

1. **First**, use structured query to filter: "Get all software engineers"
2. **Then**, use semantic search: "What skills do they have?"

Or ask Claude to do both:
"Find all people from Microsoft and summarize their roles"

Claude will:
1. Use `filter_dataset` to find Microsoft employees
2. Use `query_documents` to analyze their positions

## Creating Your Own Test Data

### Simple Text File
```bash
cat > data/my_notes.txt << 'EOF'
Meeting Notes - Q4 Planning

Key Topics:
- Budget allocation for new projects
- Hiring plans for engineering team
- Product roadmap priorities
- Customer feedback review

Action Items:
- Finalize budget by end of month
- Post job descriptions next week
- Schedule roadmap presentation
EOF
```

### Simple CSV File
```bash
cat > data/team.csv << 'EOF'
Name,Role,Department,Start Date
Alice Johnson,Engineer,Development,2023-01-15
Bob Smith,Designer,UX,2023-03-20
Carol Davis,Manager,Product,2022-11-01
David Lee,Engineer,Development,2023-02-10
EOF
```

### Test These
```bash
# Run the system
python hybrid_rag.py

# Or via Claude Desktop:
"List datasets"
"Count how many engineers are in the team"
"What topics were discussed in the meeting notes?"
```

## Tips for Best Results

### Document Preparation
1. **Clear text**: OCR scanned PDFs if needed
2. **Consistent formatting**: Use standard CSV structure
3. **Reasonable size**: Split very large files (>100MB)
4. **UTF-8 encoding**: Ensure text files are UTF-8

### Query Formulation
1. **Be specific**: "What is the PTO policy?" vs "Tell me about time off"
2. **Use semantic search** for concepts and understanding
3. **Use structured queries** for exact data and counts
4. **Iterate**: Refine queries based on results

### Performance
1. **Start small**: Test with a few documents first
2. **Monitor RAM**: Large datasets may need 8GB+
3. **Adjust k values**: Lower k = faster, higher k = more context
4. **Use persistence**: Vector store is cached after first run

## Advanced Examples

### Using Multiple Datasets
```
"List all datasets"
"Count entries in dataset1 where field X is Y"
"Count entries in dataset2 where field A is B"
"Compare the results"
```

### Combining Semantic and Structured
```
"Find all software engineers" → structured query
"What technologies do they use?" → semantic search on their bios/descriptions
```

### Monitoring Large Ingestions
```
"Start ingesting documents"
[wait 10 seconds]
"Check ingestion status"
[wait more]
"Check ingestion status"
[when complete]
"Query the documents about X"
```

## Sample Data Sets to Try

If you don't have data yet, try these public datasets:

1. **Text Documents**:
   - Wikipedia articles (export as text)
   - Project documentation
   - Meeting notes
   - Research papers (PDFs)

2. **CSV Data**:
   - Customer lists
   - Product catalogs
   - Transaction logs
   - Contact databases

3. **Mixed**:
   - Company docs (PDFs) + employee list (CSV)
   - Research papers (PDFs) + experiment data (CSV)
   - Documentation (MD) + user data (CSV)

## Next Steps

1. Add your own documents to `data/`
2. Run the system: `python hybrid_rag.py`
3. Try both semantic and structured queries
4. Integrate with Claude Desktop for conversational access
5. Explore the API for programmatic access

Happy exploring!
