"""
Utility functions for the Hybrid RAG system
"""
import logging
import warnings
import os


def configure_logging():
    """
    Configure logging to suppress unnecessary warnings from libraries.
    """
    # Suppress warnings
    warnings.filterwarnings('ignore')

    # Set environment variable to reduce Ollama verbosity
    os.environ['OLLAMA_DEBUG'] = '0'

    # Configure logging levels for various libraries
    logging.getLogger('chromadb').setLevel(logging.ERROR)
    logging.getLogger('httpx').setLevel(logging.ERROR)
    logging.getLogger('httpcore').setLevel(logging.ERROR)
    logging.getLogger('ollama').setLevel(logging.ERROR)
    logging.getLogger('langchain').setLevel(logging.ERROR)
    logging.getLogger('langchain_community').setLevel(logging.ERROR)
    logging.getLogger('langchain_ollama').setLevel(logging.ERROR)
    logging.getLogger('opentelemetry').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.ERROR)

    # Suppress stderr output from llamacpp (the init: embeddings warnings)
    # These come from the underlying C++ library
    import sys
    if not hasattr(sys.stderr, '_original_stderr'):
        sys.stderr._original_stderr = sys.stderr

    class FilteredStderr:
        def __init__(self, original_stderr):
            self.original_stderr = original_stderr
            self.buffer = ""

        def write(self, message):
            # Filter out specific warning messages
            filter_patterns = [
                "init: embeddings required but some input tokens were not marked as outputs",
                "level=WARN source=types.go",
                "invalid option provided",
                "[GIN]",
                "msg=\"invalid option provided\"",
                "option=tfs_z",
                "option=mirostat",
                "option=mirostat_eta",
                "option=mirostat_tau"
            ]

            should_filter = any(pattern in message for pattern in filter_patterns)

            if not should_filter:
                self.original_stderr.write(message)

        def flush(self):
            self.original_stderr.flush()

        def isatty(self):
            return self.original_stderr.isatty()

    # Only apply stderr filtering if not already applied
    if not isinstance(sys.stderr, FilteredStderr):
        sys.stderr = FilteredStderr(sys.stderr)
