"""
Document Ingestor Module

Handles document parsing, chunking, and metadata extraction for various formats.
Supports PDF, MD, TXT, DOCX, EPUB with configurable chunking strategies.

Based on patterns from:
- LangChain document loaders: https://github.com/langchain-ai/langchain/blob/main/langchain/document_loaders
- LlamaIndex ingestion pipeline: https://github.com/run-llama/llama_index/blob/main/llama_index/ingestion/ingestion_pipeline.py
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import logging

# Document processing libraries
import pypdf2
from docx import Document
import markdown
import epub2txt

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a chunk of document content with metadata."""
    content: str
    chunk_id: str
    source_id: str
    original_filename: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any]
    ingestion_timestamp: str


class DocumentIngestor:
    """
    Handles document ingestion with format-specific parsing and chunking.
    
    Responsibilities:
    - Parse various document formats (PDF, MD, TXT, DOCX, EPUB)
    - Chunk documents with configurable overlap
    - Extract metadata and provenance information
    - Generate unique identifiers for chunks
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize document ingestor.
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.supported_formats = {'.pdf', '.md', '.txt', '.docx', '.epub'}
        
    def ingest_document(self, file_path: Union[str, Path]) -> List[DocumentChunk]:
        """
        Ingest a single document and return chunks.
        
        Args:
            file_path: Path to document file
            
        Returns:
            List of document chunks with metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
            
        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported format: {file_path.suffix}")
            
        # Generate source ID
        source_id = self._generate_source_id(file_path)
        
        # Parse document based on format
        content = self._parse_document(file_path)
        
        # Chunk the content
        chunks = self._chunk_content(
            content=content,
            source_id=source_id,
            filename=file_path.name
        )
        
        logger.info(f"Ingested {len(chunks)} chunks from {file_path.name}")
        return chunks
        
    def ingest_directory(self, directory_path: Union[str, Path]) -> List[DocumentChunk]:
        """
        Ingest all supported documents in a directory.
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            List of all document chunks from directory
        """
        directory_path = Path(directory_path)
        all_chunks = []
        
        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    chunks = self.ingest_document(file_path)
                    all_chunks.extend(chunks)
                except Exception as e:
                    logger.error(f"Failed to ingest {file_path}: {e}")
                    
        logger.info(f"Ingested {len(all_chunks)} total chunks from {directory_path}")
        return all_chunks
        
    def _parse_document(self, file_path: Path) -> str:
        """Parse document content based on file format."""
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return self._parse_pdf(file_path)
        elif suffix == '.md':
            return self._parse_markdown(file_path)
        elif suffix == '.txt':
            return self._parse_text(file_path)
        elif suffix == '.docx':
            return self._parse_docx(file_path)
        elif suffix == '.epub':
            return self._parse_epub(file_path)
        else:
            raise ValueError(f"Unsupported format: {suffix}")
            
    def _parse_pdf(self, file_path: Path) -> str:
        """Parse PDF document content."""
        content = ""
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf2.PdfReader(file)
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        return content.strip()
        
    def _parse_markdown(self, file_path: Path) -> str:
        """Parse Markdown document content."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        # Convert markdown to plain text
        html = markdown.markdown(content)
        # Simple HTML tag removal (could use BeautifulSoup for better parsing)
        import re
        text = re.sub(r'<[^>]+>', '', html)
        return text.strip()
        
    def _parse_text(self, file_path: Path) -> str:
        """Parse plain text document content."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
            
    def _parse_docx(self, file_path: Path) -> str:
        """Parse DOCX document content."""
        doc = Document(file_path)
        content = ""
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        return content.strip()
        
    def _parse_epub(self, file_path: Path) -> str:
        """Parse EPUB document content."""
        return epub2txt.epub2txt(str(file_path))
        
    def _chunk_content(self, content: str, source_id: str, filename: str) -> List[DocumentChunk]:
        """
        Chunk content with overlap and generate metadata.
        
        Based on LangChain text splitter patterns:
        https://github.com/langchain-ai/langchain/blob/main/langchain/text_splitter.py
        """
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(content):
            # Calculate chunk end position
            end = min(start + self.chunk_size, len(content))
            
            # Adjust end to avoid splitting words
            if end < len(content):
                # Find last space before end
                last_space = content.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
                    
            # Extract chunk content
            chunk_content = content[start:end].strip()
            
            if chunk_content:  # Only create non-empty chunks
                chunk_id = self._generate_chunk_id(source_id, chunk_index)
                
                chunk = DocumentChunk(
                    content=chunk_content,
                    chunk_id=chunk_id,
                    source_id=source_id,
                    original_filename=filename,
                    chunk_index=chunk_index,
                    start_char=start,
                    end_char=end,
                    metadata={
                        'chunk_size': len(chunk_content),
                        'word_count': len(chunk_content.split()),
                        'has_overlap': chunk_index > 0
                    },
                    ingestion_timestamp=datetime.now().isoformat()
                )
                chunks.append(chunk)
                chunk_index += 1
                
            # Move start position with overlap
            start = max(start + self.chunk_size - self.chunk_overlap, end)
            
        return chunks
        
    def _generate_source_id(self, file_path: Path) -> str:
        """Generate unique source ID for document."""
        # Use file path and modification time for uniqueness
        stat = file_path.stat()
        content = f"{file_path.absolute()}:{stat.st_mtime}:{stat.st_size}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
        
    def _generate_chunk_id(self, source_id: str, chunk_index: int) -> str:
        """Generate unique chunk ID."""
        content = f"{source_id}:{chunk_index}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
        
    def get_supported_formats(self) -> set:
        """Get list of supported file formats."""
        return self.supported_formats.copy()
        
    def update_chunking_params(self, chunk_size: int, chunk_overlap: int):
        """Update chunking parameters."""
        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        if chunk_overlap < 0:
            raise ValueError("Chunk overlap must be non-negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("Chunk overlap must be less than chunk size")
            
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(f"Updated chunking params: size={chunk_size}, overlap={chunk_overlap}")


# Public API methods for DocumentIngestor:
# - ingest_document(file_path) -> List[DocumentChunk]
# - ingest_directory(directory_path) -> List[DocumentChunk]  
# - get_supported_formats() -> set
# - update_chunking_params(chunk_size, chunk_overlap) -> None