# Graceful Shutdown Handling

Both the MCP server and REST API server now support graceful shutdown with proper cleanup.

## Features

### Signal Handling
Both servers handle shutdown signals properly:
- **SIGINT** (Ctrl+C): Keyboard interrupt
- **SIGTERM**: Termination signal (from system/docker/etc.)

### Cleanup on Shutdown

#### MCP Server (`mcp_server_claude.py`)
When shutting down, the server will:
1. Cancel any running ingestion tasks
2. Clean up vector store connections
3. Close all resources properly
4. Print shutdown status messages

#### REST API Server (`mcp_server.py`)
When shutting down, the server will:
1. Complete any in-flight requests
2. Clean up vector store connections
3. Use FastAPI lifespan context manager for proper startup/shutdown
4. Close uvicorn cleanly

## How to Stop the Servers

### MCP Server (for Claude Desktop)
The MCP server runs as a subprocess managed by Claude Desktop. It will automatically stop when:
- Claude Desktop is closed
- The MCP server configuration is removed/changed
- You restart Claude Desktop

**Manual stop** (if running standalone for testing):
```bash
# Press Ctrl+C in the terminal
^C
```

Output:
```
📡 Received signal 2
⌨️  Keyboard interrupt received
🛑 Shutting down MCP server...
✅ Cleanup complete
👋 Server stopped
👋 Goodbye!
```

### REST API Server
**Stop the server:**
```bash
# Press Ctrl+C in the terminal
^C
```

Output:
```
⌨️  Keyboard interrupt received
🛑 Shutting down server...
💾 Closing vector store...
✅ Shutdown complete
👋 Server stopped
👋 Goodbye!
```

## Shutdown Sequence

### MCP Server Shutdown Flow
```
Signal Received (SIGINT/SIGTERM)
    ↓
Set shutdown event
    ↓
Cancel server task
    ↓
cleanup() function
    ↓
├── Cancel ingestion task (if running)
├── Close vector store
└── Print status
    ↓
Exit cleanly
```

### REST API Server Shutdown Flow
```
Keyboard Interrupt (Ctrl+C)
    ↓
FastAPI lifespan shutdown
    ↓
├── Close vector store
└── Print status
    ↓
Uvicorn stops
    ↓
Exit cleanly
```

## Testing Shutdown

### Test MCP Server Shutdown
```bash
# Run the server
python mcp_server_claude.py

# In another terminal, send SIGTERM
pkill -TERM -f mcp_server_claude.py

# Or press Ctrl+C in the running terminal
```

### Test REST API Server Shutdown
```bash
# Run the server
python mcp_server.py

# Press Ctrl+C
^C

# Verify clean shutdown messages appear
```

## Shutdown During Ingestion

If you stop the server while document ingestion is in progress:

**MCP Server:**
```
📡 Received signal 2
🛑 Shutting down MCP server...
⏸️  Cancelling ingestion task...
💾 Closing vector store...
✅ Cleanup complete
👋 Server stopped
```

The ingestion will be cancelled gracefully without corrupting any data.

## Error Handling

If errors occur during shutdown, they are logged but don't prevent clean exit:

```python
try:
    # Cleanup operations
    vectorstore = None
except Exception as e:
    print(f"⚠️  Error closing vector store: {e}")
    # Still continues with shutdown
```

## Best Practices

### For MCP Server (Claude Desktop)
- Let Claude Desktop manage the lifecycle
- No manual intervention needed
- Logs appear in Claude Desktop's logs

### For REST API Server
- Always use Ctrl+C for clean shutdown
- Don't use `kill -9` (force kill) unless necessary
- Wait for "Server stopped" message before restarting

### For Development
- Use Ctrl+C for testing shutdown behavior
- Check that cleanup messages appear
- Verify no zombie processes remain

## Logging

Both servers provide clear shutdown logging:

**Startup:**
```
🚀 Starting Hybrid RAG MCP Server...
✅ RAG system initialized successfully
💡 Press Ctrl+C to stop the server
```

**Shutdown:**
```
📡 Received signal 2
🛑 Shutting down MCP server...
⏸️  Cancelling ingestion task...
💾 Closing vector store...
✅ Cleanup complete
👋 Server stopped
```

## Troubleshooting

### Server doesn't stop cleanly
- Check for hanging background tasks
- Look for error messages in logs
- Use `ps aux | grep python` to find process
- If necessary: `kill -9 <pid>` (last resort)

### Vector store not closing
- Check ChromaDB logs
- Verify no file locks
- May need to clear `chroma_db/` directory

### Zombie processes
```bash
# Find zombie processes
ps aux | grep mcp_server

# Kill if necessary
pkill -9 -f mcp_server
```

## Implementation Details

### MCP Server
Uses asyncio event handling:
```python
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    print(f"\n📡 Received signal {signum}")
    shutdown_event.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

### REST API Server
Uses FastAPI lifespan context manager:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_rag_system()
    yield
    # Shutdown
    cleanup_resources()

app = FastAPI(lifespan=lifespan)
```

## Summary

Both servers now handle shutdown gracefully with:
- ✅ Proper signal handling
- ✅ Resource cleanup
- ✅ Clear status messages
- ✅ Cancellation of background tasks
- ✅ Prevention of data corruption
- ✅ Informative logging

Simply press **Ctrl+C** to stop either server cleanly!
