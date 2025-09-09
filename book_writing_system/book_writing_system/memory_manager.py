"""
Memory Manager Module

Handles vector store integration, persistence, and provenance tracking.
Uses ChromaDB for vector storage with sentence-transformers embeddings.

Based on patterns from:
- AutoGPT memory system: https://github.com/Significant-Gravitas/AutoGPT/blob/main/autogpt/memory/vector/memory_item.py
- LangChain ChromaDB integration: https://github.com/langchain-ai/langchain/blob/main/langchain/vectorstores/chroma.py
- Semantic Kernel memory: https://github.com/microsoft/semantic-kernel/blob/main/python/semantic_kernel/memory/semantic_text_memory.py
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib

# Vector store and embeddings
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import openai

# Document chunks
from .document_ingestor import DocumentChunk

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Represents a memory entry with full provenance metadata."""
    source_id: str
    chunk_id: str
    original_filename: str
    content: str
    embedding: List[float]
    ingestion_timestamp: str
    agent_id: Optional[str] = None
    provenance_notes: str = ""
    tags: List[str] = None
    retrieval_score: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


class MemoryManager:
    """
    Manages vector store operations, persistence, and provenance tracking.
    
    Responsibilities:
    - Vector store initialization and management
    - Embedding generation (local and remote)
    - Memory entry storage and retrieval
    - Provenance tracking and audit logging
    - Metadata management and filtering
    """
    
    def __init__(self, 
                 vector_db_path: str = "./data/vector_db",
                 collection_name: str = "book_memory",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 use_remote_embeddings: bool = False):
        """
        Initialize memory manager.
        
        Args:
            vector_db_path: Path to ChromaDB storage
            collection_name: Name of the collection
            embedding_model: Local embedding model name
            use_remote_embeddings: Whether to use OpenAI embeddings
        """
        self.vector_db_path = Path(vector_db_path)
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        self.use_remote_embeddings = use_remote_embeddings
        
        # Initialize ChromaDB
        self._init_chromadb()
        
        # Initialize embedding models
        self._init_embeddings()
        
        # Initialize provenance logging
        self._init_provenance_logging()
        
    def _init_chromadb(self):
        """Initialize ChromaDB client and collection."""
        # Create directory if it doesn't exist
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.vector_db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(
                name=self.collection_name
            )
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except ValueError:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "AI Book Writing System Memory"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
            
    def _init_embeddings(self):
        """Initialize embedding models."""
        # Local embedding model
        try:
            self.local_embedder = SentenceTransformer(self.embedding_model_name)
            logger.info(f"Loaded local embedding model: {self.embedding_model_name}")
        except Exception as e:
            logger.error(f"Failed to load local embedding model: {e}")
            self.local_embedder = None
            
        # Remote embedding setup
        if self.use_remote_embeddings:
            api_key = os.getenv("EMBEDDING_API_KEY") or os.getenv("LLM_REMOTE_API_KEY")
            if api_key:
                openai.api_key = api_key
                self.remote_embedder = openai
                logger.info("Initialized remote embedding client")
            else:
                logger.warning("No API key found for remote embeddings")
                self.remote_embedder = None
        else:
            self.remote_embedder = None
            
    def _init_provenance_logging(self):
        """Initialize provenance logging system."""
        self.provenance_log_path = self.vector_db_path / "provenance_log.jsonl"
        self.provenance_log_path.parent.mkdir(parents=True, exist_ok=True)
        
    def store_chunks(self, chunks: List[DocumentChunk], agent_id: str = None) -> List[str]:
        """
        Store document chunks in vector database.
        
        Args:
            chunks: List of document chunks to store
            agent_id: ID of agent performing the operation
            
        Returns:
            List of stored chunk IDs
        """
        if not chunks:
            return []
            
        # Generate embeddings
        embeddings = self._generate_embeddings([chunk.content for chunk in chunks])
        
        # Create memory entries
        memory_entries = []
        stored_ids = []
        
        for chunk, embedding in zip(chunks, embeddings):
            memory_entry = MemoryEntry(
                source_id=chunk.source_id,
                chunk_id=chunk.chunk_id,
                original_filename=chunk.original_filename,
                content=chunk.content,
                embedding=embedding,
                ingestion_timestamp=chunk.ingestion_timestamp,
                agent_id=agent_id,
                provenance_notes=f"Ingested from {chunk.original_filename}",
                tags=["document", "ingested"],
                metadata=chunk.metadata
            )
            memory_entries.append(memory_entry)
            stored_ids.append(chunk.chunk_id)
            
        # Store in ChromaDB
        self._store_in_chromadb(memory_entries)
        
        # Log provenance
        self._log_provenance(memory_entries, "store_chunks", agent_id)
        
        logger.info(f"Stored {len(chunks)} chunks in memory")
        return stored_ids
        
    def retrieve_similar(self, 
                        query: str, 
                        top_k: int = 5,
                        filter_metadata: Dict[str, Any] = None,
                        min_score: float = 0.0) -> List[MemoryEntry]:
        """
        Retrieve similar memory entries using semantic search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Metadata filters
            min_score: Minimum similarity score
            
        Returns:
            List of similar memory entries with scores
        """
        # Generate query embedding
        query_embedding = self._generate_embeddings([query])[0]
        
        # Build where clause for filtering
        where_clause = {}
        if filter_metadata:
            where_clause.update(filter_metadata)
            
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause if where_clause else None,
            include=["metadatas", "documents", "distances"]
        )
        
        # Convert to MemoryEntry objects
        memory_entries = []
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                score = 1.0 - distance  # Convert distance to similarity score
                
                if score >= min_score:
                    metadata = results["metadatas"][0][i]
                    content = results["documents"][0][i]
                    
                    memory_entry = MemoryEntry(
                        source_id=metadata.get("source_id", ""),
                        chunk_id=chunk_id,
                        original_filename=metadata.get("original_filename", ""),
                        content=content,
                        embedding=[],  # Not needed for retrieval results
                        ingestion_timestamp=metadata.get("ingestion_timestamp", ""),
                        agent_id=metadata.get("agent_id"),
                        provenance_notes=metadata.get("provenance_notes", ""),
                        tags=metadata.get("tags", []),
                        retrieval_score=score,
                        metadata=metadata
                    )
                    memory_entries.append(memory_entry)
                    
        # Log retrieval
        self._log_retrieval(query, memory_entries, agent_id="retrieval")
        
        logger.info(f"Retrieved {len(memory_entries)} similar entries for query")
        return memory_entries
        
    def store_agent_output(self, 
                          content: str, 
                          agent_id: str, 
                          provenance_notes: str = "",
                          tags: List[str] = None) -> str:
        """
        Store agent-generated content in memory.
        
        Args:
            content: Generated content
            agent_id: ID of generating agent
            provenance_notes: Notes about content generation
            tags: Tags for categorization
            
        Returns:
            Generated chunk ID
        """
        if tags is None:
            tags = ["agent_output", agent_id]
            
        # Generate unique ID
        chunk_id = hashlib.sha256(
            f"{agent_id}:{content}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Generate embedding
        embedding = self._generate_embeddings([content])[0]
        
        # Create memory entry
        memory_entry = MemoryEntry(
            source_id=f"agent_{agent_id}",
            chunk_id=chunk_id,
            original_filename=f"agent_output_{agent_id}",
            content=content,
            embedding=embedding,
            ingestion_timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            provenance_notes=provenance_notes,
            tags=tags,
            metadata={"type": "agent_output", "agent_id": agent_id}
        )
        
        # Store in ChromaDB
        self._store_in_chromadb([memory_entry])
        
        # Log provenance
        self._log_provenance([memory_entry], "store_agent_output", agent_id)
        
        logger.info(f"Stored agent output from {agent_id}")
        return chunk_id
        
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts using local or remote model."""
        if self.use_remote_embeddings and self.remote_embedder:
            return self._generate_remote_embeddings(texts)
        elif self.local_embedder:
            return self._generate_local_embeddings(texts)
        else:
            raise RuntimeError("No embedding model available")
            
    def _generate_local_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local sentence-transformers model."""
        embeddings = self.local_embedder.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()
        
    def _generate_remote_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        try:
            response = self.remote_embedder.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Remote embedding failed: {e}")
            # Fallback to local embeddings
            if self.local_embedder:
                return self._generate_local_embeddings(texts)
            else:
                raise
                
    def _store_in_chromadb(self, memory_entries: List[MemoryEntry]):
        """Store memory entries in ChromaDB."""
        ids = [entry.chunk_id for entry in memory_entries]
        embeddings = [entry.embedding for entry in memory_entries]
        documents = [entry.content for entry in memory_entries]
        metadatas = []
        
        for entry in memory_entries:
            metadata = {
                "source_id": entry.source_id,
                "original_filename": entry.original_filename,
                "ingestion_timestamp": entry.ingestion_timestamp,
                "agent_id": entry.agent_id or "",
                "provenance_notes": entry.provenance_notes,
                "tags": json.dumps(entry.tags),
                **entry.metadata
            }
            metadatas.append(metadata)
            
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
    def _log_provenance(self, memory_entries: List[MemoryEntry], operation: str, agent_id: str = None):
        """Log provenance information to file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "agent_id": agent_id,
            "entries": [
                {
                    "chunk_id": entry.chunk_id,
                    "source_id": entry.source_id,
                    "filename": entry.original_filename,
                    "provenance_notes": entry.provenance_notes,
                    "tags": entry.tags
                }
                for entry in memory_entries
            ]
        }
        
        with open(self.provenance_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
            
    def _log_retrieval(self, query: str, results: List[MemoryEntry], agent_id: str = None):
        """Log retrieval operations."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": "retrieve_similar",
            "agent_id": agent_id,
            "query": query,
            "results": [
                {
                    "chunk_id": entry.chunk_id,
                    "score": entry.retrieval_score,
                    "filename": entry.original_filename
                }
                for entry in results
            ]
        }
        
        with open(self.provenance_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
            
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory collection."""
        count = self.collection.count()
        return {
            "total_entries": count,
            "collection_name": self.collection_name,
            "embedding_model": self.embedding_model_name,
            "use_remote_embeddings": self.use_remote_embeddings,
            "vector_db_path": str(self.vector_db_path)
        }
        
    def clear_collection(self):
        """Clear all entries from the collection."""
        self.chroma_client.delete_collection(self.collection_name)
        self._init_chromadb()
        logger.info("Cleared memory collection")


# Public API methods for MemoryManager:
# - store_chunks(chunks, agent_id) -> List[str]
# - retrieve_similar(query, top_k, filter_metadata, min_score) -> List[MemoryEntry]
# - store_agent_output(content, agent_id, provenance_notes, tags) -> str
# - get_collection_stats() -> Dict[str, Any]
# - clear_collection() -> None