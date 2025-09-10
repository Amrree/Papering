"""
AI Book Writing System

A production-capable non-fiction book-writing system with full RAG,
persistent memory, cooperating agents, and MCP-style tool registry.

Based on research in research/RESEARCH.md and repository analysis in research/REPOS.md.
"""

__version__ = "1.0.0"
__author__ = "AI Book Writing System Team"

# Core modules
from .document_ingestor import DocumentIngestor
from .memory_manager import MemoryManager
from .llm_client import LLMClient
from .tool_manager import ToolManager
from .agent_manager import AgentManager

# Agent modules
from .research_agent import ResearchAgent
from .writer_agent import WriterAgent
from .editor_agent import EditorAgent
from .tool_agent import ToolAgent

# Interface modules
from .book_builder import BookBuilder

__all__ = [
    "DocumentIngestor",
    "MemoryManager", 
    "LLMClient",
    "ToolManager",
    "AgentManager",
    "ResearchAgent",
    "WriterAgent", 
    "EditorAgent",
    "ToolAgent",
    "BookBuilder",
]