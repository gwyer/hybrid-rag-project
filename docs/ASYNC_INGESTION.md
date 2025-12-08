# Async Ingestion with Progress Tracking

## Overview

The MCP server now supports asynchronous document ingestion with real-time progress tracking. This allows you to monitor the ingestion process as it runs in the background.

## Features

### 1. Asynchronous Processing
- Ingestion runs as a background task
- Non-blocking operation - you can continue other tasks
- Uses Python asyncio for concurrent execution

### 2. Progress Tracking
Track ingestion progress with detailed status information:

- **Progress percentage**: 0-100%
- **Current stage**:
  - `loading_files` (0-80%): Loading and parsing documents
  - `building_index` (80-100%): Creating vector embeddings and search index
  - `completed`: Process finished successfully
- **File-level tracking**:
  - Current file being processed
  - Files processed vs total files
  - Documents created count

### 3. Status States

- **`not_started`**: No ingestion has been initiated
- **`in_progress`**: Currently loading and indexing documents
- **`completed`**: Successfully finished ingestion
- **`failed`**: Error occurred during ingestion

## MCP Tools

### ingest_documents
Starts the asynchronous ingestion process.

**Usage in Claude:**
```
"Start ingesting my documents"
```

**Response:**
```
Ingestion started. Use get_ingestion_status to monitor progress.
```

### get_ingestion_status
Returns the current ingestion status and progress.

**Usage in Claude:**
```
"Check the ingestion status"
```

**Response (in progress):**
```
Ingestion Status: In Progress
Progress: 45%
Stage: loading_files
Files Processed: 9/20
Current File: document.pdf
Documents Loaded: 15
```

**Response (completed):**
```
Ingestion Status: Completed ✅
Progress: 100%
Total Files Processed: 20
Total Documents Loaded: 35

You can now use query_documents to search the documents.
```

## Implementation Details

### Document Loader Updates

The `DocumentLoaderUtility` class now supports:
- **Progress callbacks**: Reports progress after each file
- **File counting**: Pre-counts files for accurate progress
- **Sequential loading**: Processes files in order with progress updates

### MCP Server Updates

New global state tracking:
```python
ingestion_status = {
    "status": "not_started",
    "progress": 0,
    "current_file": "",
    "files_processed": 0,
    "total_files": 0,
    "documents_loaded": 0,
    "error_message": None,
    "stage": ""
}
```

### Progress Calculation

- **File loading**: 0-80% (proportional to files processed)
- **Index building**: 80-100% (creating embeddings and search index)

## Usage Example

### Step 1: Start Ingestion
```
You: "Please ingest my documents"
Claude: [Calls ingest_documents]
Response: "Ingestion started. Use get_ingestion_status to monitor progress."
```

### Step 2: Monitor Progress
```
You: "What's the ingestion status?"
Claude: [Calls get_ingestion_status]
Response: "Progress: 45%, Files: 9/20, Current: report.pdf"
```

### Step 3: Wait for Completion
```
You: "Check status again"
Claude: [Calls get_ingestion_status]
Response: "Completed! 35 documents loaded from 20 files."
```

### Step 4: Query Documents
```
You: "What are the main topics?"
Claude: [Calls query_documents]
Response: "Based on the documents, the main topics are..."
```

## Error Handling

If ingestion fails, the status will show:
```
Ingestion Status: Failed ❌
Error: [error message]
Files Processed: 5/20
```

You can restart ingestion by calling `ingest_documents` again.

## Benefits

1. **Better UX**: See progress instead of waiting blindly
2. **Large datasets**: Monitor long-running ingestion tasks
3. **Debugging**: Identify which files cause issues
4. **Non-blocking**: Continue working while documents load
5. **Transparency**: Understand what the system is doing

## Technical Notes

- Uses `asyncio.create_task()` for background execution
- Progress callback updates global state
- `asyncio.to_thread()` runs blocking operations in thread pool
- Prevents concurrent ingestion (checks if already in progress)
