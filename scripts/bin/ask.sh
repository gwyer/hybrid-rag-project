#!/bin/bash
# Quick launcher for conversational RAG demo
# Usage: ./scripts/bin/ask.sh (or create alias: alias ask='./scripts/bin/ask.sh')
#
# Use conversational mode (with memory) by default
# For simple mode (no memory): ./scripts/bin/ask.sh --simple

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Activate virtual environment
cd "$PROJECT_ROOT"
source .venv/bin/activate

# Check for --simple flag
if [[ "$1" == "--simple" ]]; then
    echo "🔹 Starting simple mode (no conversation memory)"
    python scripts/demos/interactive.py "${@:2}"
else
    echo "💬 Starting conversational mode (with memory)"
    echo "   Type 'help' for commands, 'clear' to reset conversation"
    echo ""
    python scripts/demos/conversational.py "$@"
fi
