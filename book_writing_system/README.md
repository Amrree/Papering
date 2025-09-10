# AI Book Writing System

A production-capable non-fiction book-writing system with full RAG (retrieval-augmented generation), persistent memory, cooperating agents, and MCP-style tool registry.

## Features

- **RAG Pipeline**: Document ingestion, chunking, embedding, and retrieval
- **Multi-Agent System**: Research, Writer, Editor, and Tool agents
- **Persistent Memory**: Vector store with provenance tracking
- **MCP Tool Registry**: Safe tool execution with sandboxing
- **Export Capabilities**: Markdown, DOCX, PDF with bibliography
- **Dual Interface**: GUI and CLI entrypoints

## Technology Stack

Based on research in `research/RESEARCH.md`:

- **Vector Store**: ChromaDB (local, Python-native)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (local) + OpenAI text-embedding-ada-002 (remote)
- **LLM Backends**: Ollama (local) + OpenAI API (remote)
- **GUI Framework**: CustomTkinter
- **CLI Framework**: Typer
- **Concurrency**: asyncio + concurrent.futures

## Installation

### Prerequisites

- Python 3.9+
- macOS (tested on Apple Silicon)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd book_writing_system
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Ollama (for local LLM):
```bash
# Install Ollama from https://ollama.ai
ollama pull llama2
```

### Environment Variables

Set the following environment variables:

```bash
# Required for remote LLM access
export LLM_REMOTE_API_KEY="your-openai-api-key"

# Optional: Custom Ollama URL (default: http://localhost:11434)
export OLLAMA_LOCAL_URL="http://localhost:11434"

# Optional: Remote embedding API key
export EMBEDDING_API_KEY="your-openai-api-key"

# Vector database path
export VECTOR_DB_PATH="./data/vector_db"

# Tool safety (default: false)
export TOOL_MANAGER_ALLOW_UNSAFE="false"
```

## Usage

### CLI Interface

```bash
# Start CLI
python run.py cli

# Ingest documents
python run.py ingest --path ./documents --format pdf

# Generate book
python run.py generate --topic "Machine Learning Fundamentals" --chapters 5

# Export book
python run.py export --format pdf --output ./output/book.pdf
```

### GUI Interface

```bash
# Start GUI
python run.py gui
```

## Project Structure

```
book_writing_system/
├── README.md
├── requirements.txt
├── run.py
├── book_writing_system/
│   ├── __init__.py
│   ├── document_ingestor.py      # Document parsing and chunking
│   ├── memory_manager.py         # Vector store and persistence
│   ├── llm_client.py            # LLM provider adapters
│   ├── tool_manager.py          # MCP-style tool registry
│   ├── agent_manager.py         # Agent orchestration
│   ├── research_agent.py        # Research and summarization
│   ├── writer_agent.py          # Content generation
│   ├── editor_agent.py          # Revision and consistency
│   ├── tool_agent.py            # Tool execution agent
│   ├── book_builder.py          # Book assembly and export
│   ├── gui.py                   # GUI interface
│   └── cli.py                   # CLI interface
├── tests/
│   ├── __init__.py
│   ├── test_document_ingestor.py
│   ├── test_memory_manager.py
│   ├── test_llm_client.py
│   ├── test_tool_manager.py
│   ├── test_agent_manager.py
│   ├── test_research_agent.py
│   ├── test_writer_agent.py
│   ├── test_editor_agent.py
│   ├── test_tool_agent.py
│   ├── test_book_builder.py
│   ├── test_integration.py
│   └── fixtures/
│       ├── sample_doc.pdf
│       ├── sample_doc.txt
│       └── sample_doc.md
├── research/
│   ├── RESEARCH.md              # Technology stack research
│   └── REPOS.md                 # Repository analysis
└── data/
    └── vector_db/               # Vector database storage
```

## Module Responsibilities

### Core Modules

- **document_ingestor.py**: Parse PDF, MD, TXT, DOCX, EPUB → chunk → extract metadata
- **memory_manager.py**: Vector store operations, persistence, provenance tracking
- **llm_client.py**: Unified interface for local/remote LLM providers
- **tool_manager.py**: MCP protocol implementation, tool registry, safety controls
- **agent_manager.py**: Agent lifecycle, task routing, concurrency management

### Agent Modules

- **research_agent.py**: Document analysis, research synthesis, structured summaries
- **writer_agent.py**: RAG-driven content generation, chapter writing
- **editor_agent.py**: Content revision, consistency checking, quality assurance
- **tool_agent.py**: Tool execution under ToolManager supervision

### Interface Modules

- **book_builder.py**: Book assembly, export to multiple formats, bibliography generation
- **gui.py**: CustomTkinter-based graphical interface
- **cli.py**: Typer-based command-line interface

## RAG Pipeline

1. **Ingest**: Parse documents → extract text → chunk with overlap
2. **Embed**: Generate embeddings using local/remote models
3. **Store**: Save to ChromaDB with metadata and provenance
4. **Retrieve**: Semantic search with scoring and filtering
5. **Context**: Assemble retrieved chunks with token budgeting
6. **Generate**: LLM call with context and instructions
7. **Store**: Save generated content with provenance links

## Agent Workflows

### Research Agent → Writer Agent → Editor Agent

1. **Research**: Analyze topic → retrieve relevant documents → synthesize findings
2. **Writer**: Generate chapter content using research context
3. **Editor**: Review content → check consistency → suggest revisions
4. **Iteration**: Repeat until quality threshold met

## MCP Tool Protocol

```python
# Tool Request
{
    "tool_name": "web_search",
    "args": {"query": "machine learning trends 2024"},
    "request_id": "req_123",
    "agent_id": "research_agent"
}

# Tool Response
{
    "status": "success",
    "output": "Search results...",
    "stdout": "",
    "stderr": "",
    "runtime": 1.23,
    "hashes": {"input": "abc123", "output": "def456"}
}
```

## Testing

```bash
# Run unit tests
python -m pytest tests/

# Run integration test
python -m pytest tests/test_integration.py -v

# Run with coverage
python -m pytest tests/ --cov=book_writing_system
```

## CI/CD

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run integration test
python -m pytest tests/test_integration.py
```

## Extensibility

### Adding New LLM Backends

1. Implement provider interface in `llm_client.py`
2. Add configuration options
3. Update environment variables
4. Add tests

### Adding New Tools

1. Implement tool function with safety checks
2. Register in `tool_manager.py`
3. Add to appropriate agent capabilities
4. Update documentation

### Adding New Vector Stores

1. Implement store interface in `memory_manager.py`
2. Add configuration options
3. Update tests
4. Document migration path

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## Support

- Issues: GitHub Issues
- Documentation: `research/` directory
- Examples: `tests/fixtures/` directory