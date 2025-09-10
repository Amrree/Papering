# Research Document: AI Book Writing System

## Executive Summary

This document outlines the research conducted to select the optimal technology stack for a production-capable non-fiction book-writing system with RAG, persistent memory, cooperating agents, and MCP-style tool registry.

## Technology Stack Research

### 1. Vector Store / Retrieval Engine

**Candidates Considered:**
- **ChromaDB**: Lightweight, Python-native, easy setup
- **Pinecone**: Cloud-based, managed service, high performance
- **Weaviate**: Open-source, GraphQL API, hybrid search
- **Qdrant**: Rust-based, high performance, local deployment
- **FAISS**: Facebook's similarity search, memory efficient

**Final Choice: ChromaDB**
**Justification:**
- Python-native with excellent integration
- Minimal setup complexity for macOS
- Built-in persistence and metadata support
- Good performance for RAG workloads
- Active development and community support
- No external dependencies or cloud costs

### 2. Embedding Models/Providers

**Local Candidates:**
- **sentence-transformers/all-MiniLM-L6-v2**: Fast, 384 dimensions
- **sentence-transformers/all-mpnet-base-v2**: High quality, 768 dimensions
- **sentence-transformers/all-distilroberta-v1**: Balanced performance

**Remote Candidates:**
- **OpenAI text-embedding-ada-002**: High quality, 1536 dimensions
- **Cohere embed-english-v2.0**: Good performance, 4096 dimensions

**Final Choice: sentence-transformers/all-MiniLM-L6-v2 (local) + OpenAI text-embedding-ada-002 (remote)**
**Justification:**
- Local model for offline capability and cost efficiency
- Remote model for highest quality when API access available
- 384 dimensions provide good balance of performance and memory usage
- Fast inference suitable for real-time RAG operations

### 3. LLM Backends/Adapters

**Local Options:**
- **Ollama**: Easy local model deployment
- **Transformers (Hugging Face)**: Direct model loading
- **vLLM**: High-performance inference server

**Remote Options:**
- **OpenAI API**: GPT-4, GPT-3.5-turbo
- **Anthropic API**: Claude-3 models
- **Google AI**: Gemini models

**Final Choice: Ollama (local) + OpenAI API (remote)**
**Justification:**
- Ollama provides easy local model management and deployment
- OpenAI API offers state-of-the-art performance for production use
- LangChain adapters provide unified interface
- Cost-effective local option with premium remote fallback

### 4. GUI Framework

**Candidates Considered:**
- **Tkinter**: Built-in, simple, limited styling
- **PyQt6/PySide6**: Professional, feature-rich, complex
- **Streamlit**: Web-based, rapid development, limited customization
- **Gradio**: ML-focused, easy deployment, web-based
- **CustomTkinter**: Modern Tkinter styling, good balance

**Final Choice: CustomTkinter**
**Justification:**
- Modern dark theme suitable for writing applications
- Good balance of features and simplicity
- Cross-platform compatibility including macOS
- Active development and community
- Easy integration with existing Python codebase

### 5. CLI Tooling

**Candidates Considered:**
- **Click**: Feature-rich, decorator-based
- **Typer**: Modern, type-hint based
- **argparse**: Built-in, verbose
- **Fire**: Google's framework, automatic CLI generation

**Final Choice: Typer**
**Justification:**
- Modern Python with type hints
- Excellent developer experience
- Automatic help generation
- Good integration with FastAPI patterns
- Clean, readable code

### 6. Concurrency/Orchestration

**Candidates Considered:**
- **asyncio**: Native Python async support
- **Celery**: Distributed task queue
- **multiprocessing**: Process-based parallelism
- **threading**: Thread-based concurrency
- **Ray**: Distributed computing framework

**Final Choice: asyncio + concurrent.futures**
**Justification:**
- Native Python support, no external dependencies
- Good for I/O-bound operations (API calls, file operations)
- ThreadPoolExecutor for CPU-bound tasks
- Simpler than distributed systems for single-machine deployment
- Excellent for agent orchestration patterns

## macOS Suitability Analysis

### Installation Complexity
- **ChromaDB**: Simple pip install, no system dependencies
- **sentence-transformers**: Requires PyTorch, manageable on macOS
- **Ollama**: Native macOS binary available
- **CustomTkinter**: Pure Python, no system dependencies
- **Overall**: Low complexity, standard Python environment

### Performance Considerations
- **Vector operations**: ChromaDB optimized for local development
- **Embedding inference**: sentence-transformers works well on Apple Silicon
- **LLM inference**: Ollama supports Apple Silicon acceleration
- **Memory usage**: Reasonable for typical development machines

### RAG Support
- **ChromaDB**: Excellent metadata support for provenance
- **Embedding models**: Good semantic similarity for document retrieval
- **Chunking strategies**: Configurable overlap and size parameters
- **Context assembly**: Flexible token budgeting and ranking

## Tradeoff Analysis

### Local vs Remote
- **Local**: Better privacy, no API costs, offline capability
- **Remote**: Higher quality, more models, managed infrastructure
- **Hybrid**: Best of both worlds, graceful degradation

### Performance vs Simplicity
- **ChromaDB**: Good performance with simple setup
- **sentence-transformers**: Fast inference with reasonable quality
- **asyncio**: Efficient concurrency without complexity

### Cost vs Quality
- **Local models**: Free but limited quality
- **Remote APIs**: Cost but high quality
- **Hybrid approach**: Optimal cost/quality balance

## References

1. ChromaDB Documentation: https://docs.trychroma.com/
2. Sentence Transformers: https://www.sbert.net/
3. Ollama: https://ollama.ai/
4. OpenAI API: https://platform.openai.com/
5. CustomTkinter: https://github.com/TomSchimansky/CustomTkinter
6. Typer: https://typer.tiangolo.com/
7. LangChain: https://python.langchain.com/