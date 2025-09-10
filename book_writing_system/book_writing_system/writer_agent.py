"""
Writer Agent Module

Implements RAG-driven content generation and chapter writing capabilities.
Uses research context and memory to generate coherent, well-structured content.

Based on patterns from:
- LangChain writing chains: https://github.com/langchain-ai/langchain/blob/main/langchain/chains
- AutoGPT content generation: https://github.com/Significant-Gravitas/AutoGPT/blob/main/autogpt/agents/agent.py
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .memory_manager import MemoryManager, MemoryEntry
from .llm_client import LLMClient, LLMProvider

logger = logging.getLogger(__name__)


@dataclass
class WritingTask:
    """Represents a writing task with context and requirements."""
    task_type: str  # "chapter", "section", "paragraph"
    topic: str
    target_length: int
    style: str = "academic"
    tone: str = "professional"
    context: Dict[str, Any] = None
    requirements: List[str] = None


@dataclass
class WritingResult:
    """Represents the result of a writing task."""
    content: str
    word_count: int
    citations: List[str]
    sources_used: List[str]
    writing_timestamp: str
    agent_id: str = "writer_agent"


class WriterAgent:
    """
    RAG-driven content generation agent for book writing.
    
    Responsibilities:
    - Generate chapter content using research context
    - Maintain writing style and tone consistency
    - Incorporate citations and source references
    - Structure content with proper formatting
    - Adapt content length and complexity
    """
    
    def __init__(self, 
                 memory_manager: MemoryManager,
                 llm_client: LLMClient):
        """
        Initialize writer agent.
        
        Args:
            memory_manager: Memory manager for RAG operations
            llm_client: LLM client for content generation
        """
        self.memory_manager = memory_manager
        self.llm_client = llm_client
        self.agent_id = "writer_agent"
        
        # Writing statistics
        self.stats = {
            "total_writing_tasks": 0,
            "successful_writing_tasks": 0,
            "failed_writing_tasks": 0,
            "total_words_generated": 0,
            "average_word_count": 0
        }
        
        logger.info("WriterAgent initialized")
        
    async def execute_task(self, task) -> Dict[str, Any]:
        """
        Execute a writing task.
        
        Args:
            task: Task object with writing parameters
            
        Returns:
            Writing results
        """
        try:
            writing_task = WritingTask(
                task_type=task.input_data.get("task_type", "chapter"),
                topic=task.input_data.get("topic", ""),
                target_length=task.input_data.get("target_length", 1000),
                style=task.input_data.get("style", "academic"),
                tone=task.input_data.get("tone", "professional"),
                context=task.input_data.get("context", {}),
                requirements=task.input_data.get("requirements", [])
            )
            
            # Generate content
            result = await self.write_content(writing_task)
            
            return {
                "writing_result": result,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Writing task failed: {e}")
            self.stats["failed_writing_tasks"] += 1
            raise
            
    async def write_content(self, writing_task: WritingTask) -> WritingResult:
        """
        Generate content based on writing task requirements.
        
        Args:
            writing_task: Writing task specification
            
        Returns:
            Generated content with metadata
        """
        logger.info(f"Starting writing task: {writing_task.task_type} on {writing_task.topic}")
        self.stats["total_writing_tasks"] += 1
        
        try:
            # Step 1: Retrieve relevant context from memory
            context_sources = await self._retrieve_writing_context(writing_task)
            
            # Step 2: Generate content using RAG
            content = await self._generate_content(writing_task, context_sources)
            
            # Step 3: Post-process and format content
            formatted_content = await self._format_content(content, writing_task)
            
            # Step 4: Extract citations and sources
            citations, sources_used = self._extract_citations(context_sources)
            
            # Step 5: Create writing result
            result = WritingResult(
                content=formatted_content,
                word_count=len(formatted_content.split()),
                citations=citations,
                sources_used=sources_used,
                writing_timestamp=datetime.now().isoformat(),
                agent_id=self.agent_id
            )
            
            # Step 6: Store generated content in memory
            await self._store_generated_content(result, writing_task)
            
            # Update statistics
            self.stats["successful_writing_tasks"] += 1
            self.stats["total_words_generated"] += result.word_count
            self.stats["average_word_count"] = (
                self.stats["total_words_generated"] / self.stats["successful_writing_tasks"]
            )
            
            logger.info(f"Writing completed: {result.word_count} words generated")
            return result
            
        except Exception as e:
            logger.error(f"Writing failed: {e}")
            self.stats["failed_writing_tasks"] += 1
            raise
            
    async def _retrieve_writing_context(self, writing_task: WritingTask) -> List[MemoryEntry]:
        """Retrieve relevant context for writing task."""
        # Build search queries based on topic and context
        search_queries = [writing_task.topic]
        
        # Add context-specific queries
        if writing_task.context:
            for key, value in writing_task.context.items():
                if isinstance(value, str) and len(value) > 10:
                    search_queries.append(f"{key}: {value}")
                    
        # Add requirement-based queries
        if writing_task.requirements:
            search_queries.extend(writing_task.requirements)
            
        # Retrieve context from memory
        all_sources = []
        for query in search_queries[:3]:  # Limit to top 3 queries
            sources = self.memory_manager.retrieve_similar(
                query=query,
                top_k=5,
                min_score=0.6
            )
            all_sources.extend(sources)
            
        # Remove duplicates and sort by relevance
        unique_sources = {}
        for source in all_sources:
            if source.chunk_id not in unique_sources:
                unique_sources[source.chunk_id] = source
                
        context_sources = list(unique_sources.values())
        context_sources.sort(key=lambda x: x.retrieval_score, reverse=True)
        
        logger.info(f"Retrieved {len(context_sources)} context sources")
        return context_sources[:10]  # Limit to top 10 sources
        
    async def _generate_content(self, 
                              writing_task: WritingTask, 
                              context_sources: List[MemoryEntry]) -> str:
        """Generate content using LLM with RAG context."""
        # Prepare context from sources
        context_parts = []
        for i, source in enumerate(context_sources, 1):
            context_parts.append(f"[Source {i}] {source.content}")
            
        context = "\n\n".join(context_parts)
        
        # Build writing prompt based on task type
        if writing_task.task_type == "chapter":
            prompt = self._build_chapter_prompt(writing_task, context)
        elif writing_task.task_type == "section":
            prompt = self._build_section_prompt(writing_task, context)
        else:
            prompt = self._build_general_prompt(writing_task, context)
            
        # Generate content
        response = self.llm_client.generate(
            prompt=prompt,
            max_tokens=min(writing_task.target_length * 2, 4000),  # Estimate tokens
            temperature=0.7
        )
        
        return response.content
        
    def _build_chapter_prompt(self, writing_task: WritingTask, context: str) -> str:
        """Build prompt for chapter writing."""
        return f"""
        Write a comprehensive chapter on "{writing_task.topic}" with the following specifications:
        
        Style: {writing_task.style}
        Tone: {writing_task.tone}
        Target Length: Approximately {writing_task.target_length} words
        
        Requirements:
        {chr(10).join(f"- {req}" for req in writing_task.requirements) if writing_task.requirements else "- Provide comprehensive coverage of the topic"}
        
        Context and Sources:
        {context}
        
        Instructions:
        1. Write a well-structured chapter with clear sections and subsections
        2. Use the provided context to inform your content
        3. Include relevant examples and explanations
        4. Maintain consistency in style and tone
        5. Ensure the content flows logically from one section to the next
        6. Include inline citations where appropriate (e.g., [Source 1], [Source 2])
        
        Chapter Content:
        """
        
    def _build_section_prompt(self, writing_task: WritingTask, context: str) -> str:
        """Build prompt for section writing."""
        return f"""
        Write a detailed section on "{writing_task.topic}" with the following specifications:
        
        Style: {writing_task.style}
        Tone: {writing_task.tone}
        Target Length: Approximately {writing_task.target_length} words
        
        Requirements:
        {chr(10).join(f"- {req}" for req in writing_task.requirements) if writing_task.requirements else "- Provide detailed coverage of the topic"}
        
        Context and Sources:
        {context}
        
        Instructions:
        1. Write a focused section with clear structure
        2. Use the provided context to inform your content
        3. Include relevant examples and explanations
        4. Maintain consistency in style and tone
        5. Include inline citations where appropriate (e.g., [Source 1], [Source 2])
        
        Section Content:
        """
        
    def _build_general_prompt(self, writing_task: WritingTask, context: str) -> str:
        """Build prompt for general content writing."""
        return f"""
        Write content on "{writing_task.topic}" with the following specifications:
        
        Style: {writing_task.style}
        Tone: {writing_task.tone}
        Target Length: Approximately {writing_task.target_length} words
        
        Requirements:
        {chr(10).join(f"- {req}" for req in writing_task.requirements) if writing_task.requirements else "- Provide comprehensive coverage of the topic"}
        
        Context and Sources:
        {context}
        
        Instructions:
        1. Write well-structured content
        2. Use the provided context to inform your content
        3. Include relevant examples and explanations
        4. Maintain consistency in style and tone
        5. Include inline citations where appropriate (e.g., [Source 1], [Source 2])
        
        Content:
        """
        
    async def _format_content(self, content: str, writing_task: WritingTask) -> str:
        """Format and post-process generated content."""
        # Basic formatting
        formatted_content = content.strip()
        
        # Add proper spacing and structure
        if writing_task.task_type == "chapter":
            formatted_content = self._format_chapter_content(formatted_content)
        elif writing_task.task_type == "section":
            formatted_content = self._format_section_content(formatted_content)
            
        return formatted_content
        
    def _format_chapter_content(self, content: str) -> str:
        """Format chapter content with proper structure."""
        # Ensure chapter has a title
        if not content.startswith("# "):
            lines = content.split('\n')
            if lines and not lines[0].startswith('#'):
                content = f"# {lines[0]}\n\n" + '\n'.join(lines[1:])
                
        return content
        
    def _format_section_content(self, content: str) -> str:
        """Format section content with proper structure."""
        # Ensure section has proper heading
        if not content.startswith("## "):
            lines = content.split('\n')
            if lines and not lines[0].startswith('#'):
                content = f"## {lines[0]}\n\n" + '\n'.join(lines[1:])
                
        return content
        
    def _extract_citations(self, context_sources: List[MemoryEntry]) -> tuple:
        """Extract citations and source information."""
        citations = []
        sources_used = []
        
        for i, source in enumerate(context_sources, 1):
            citation = f"[Source {i}] {source.original_filename}"
            citations.append(citation)
            sources_used.append(source.original_filename)
            
        return citations, sources_used
        
    async def _store_generated_content(self, result: WritingResult, writing_task: WritingTask):
        """Store generated content in memory for future reference."""
        # Create comprehensive content summary
        content_summary = f"""
        Generated Content:
        Topic: {writing_task.topic}
        Type: {writing_task.task_type}
        Word Count: {result.word_count}
        Style: {writing_task.style}
        Tone: {writing_task.tone}
        
        Content Preview: {result.content[:500]}...
        
        Sources Used: {', '.join(result.sources_used)}
        Generated: {result.writing_timestamp}
        """
        
        # Store in memory
        chunk_id = self.memory_manager.store_agent_output(
            content=content_summary,
            agent_id=self.agent_id,
            provenance_notes=f"Generated {writing_task.task_type} on {writing_task.topic}",
            tags=["generated", "content", writing_task.task_type, writing_task.topic.lower().replace(" ", "_")]
        )
        
        logger.info(f"Stored generated content with chunk_id: {chunk_id}")
        
    async def revise_content(self, 
                           original_content: str,
                           revision_instructions: List[str]) -> str:
        """
        Revise existing content based on instructions.
        
        Args:
            original_content: Original content to revise
            revision_instructions: List of revision instructions
            
        Returns:
            Revised content
        """
        instructions_text = "\n".join(f"- {instruction}" for instruction in revision_instructions)
        
        prompt = f"""
        Please revise the following content based on the provided instructions:
        
        Original Content:
        {original_content}
        
        Revision Instructions:
        {instructions_text}
        
        Please provide the revised content that addresses all the instructions while maintaining the original style and structure.
        
        Revised Content:
        """
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=len(original_content.split()) * 2,  # Estimate tokens
                temperature=0.5
            )
            
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Content revision failed: {e}")
            return original_content  # Return original if revision fails
            
    def get_writing_stats(self) -> Dict[str, Any]:
        """Get writing agent statistics."""
        return self.stats.copy()


# Public API methods for WriterAgent:
# - execute_task(task) -> Dict[str, Any]
# - write_content(writing_task) -> WritingResult
# - revise_content(original_content, revision_instructions) -> str
# - get_writing_stats() -> Dict[str, Any]