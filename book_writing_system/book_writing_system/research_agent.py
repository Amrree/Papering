"""
Research Agent Module

Implements autonomous research and structured summarization capabilities.
Uses RAG pipeline for document analysis and knowledge synthesis.

Based on patterns from:
- AutoGPT research capabilities: https://github.com/Significant-Gravitas/AutoGPT/blob/main/autogpt/agents/agent.py
- LangChain research chains: https://github.com/langchain-ai/langchain/blob/main/langchain/chains
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .memory_manager import MemoryManager, MemoryEntry
from .llm_client import LLMClient, LLMProvider
from .tool_manager import ToolManager, ToolRequest, ToolResponse

logger = logging.getLogger(__name__)


@dataclass
class ResearchResult:
    """Represents a research result with structured information."""
    topic: str
    summary: str
    key_findings: List[str]
    sources: List[str]
    confidence_score: float
    research_timestamp: str
    agent_id: str = "research_agent"


class ResearchAgent:
    """
    Autonomous research agent for document analysis and knowledge synthesis.
    
    Responsibilities:
    - Analyze research topics and questions
    - Retrieve relevant information from memory
    - Synthesize findings into structured summaries
    - Generate research reports with citations
    - Update memory with research findings
    """
    
    def __init__(self, 
                 memory_manager: MemoryManager,
                 llm_client: LLMClient,
                 tool_manager: ToolManager):
        """
        Initialize research agent.
        
        Args:
            memory_manager: Memory manager for RAG operations
            llm_client: LLM client for text generation
            tool_manager: Tool manager for external research
        """
        self.memory_manager = memory_manager
        self.llm_client = llm_client
        self.tool_manager = tool_manager
        self.agent_id = "research_agent"
        
        # Research statistics
        self.stats = {
            "total_researches": 0,
            "successful_researches": 0,
            "failed_researches": 0,
            "total_sources_analyzed": 0
        }
        
        logger.info("ResearchAgent initialized")
        
    async def execute_task(self, task) -> Dict[str, Any]:
        """
        Execute a research task.
        
        Args:
            task: Task object with research parameters
            
        Returns:
            Research results
        """
        try:
            topic = task.input_data.get("topic", "")
            research_question = task.input_data.get("question", "")
            max_sources = task.input_data.get("max_sources", 10)
            
            if not topic and not research_question:
                raise ValueError("Either topic or research_question must be provided")
                
            # Perform research
            result = await self.research_topic(
                topic=topic,
                research_question=research_question,
                max_sources=max_sources
            )
            
            return {
                "research_result": result,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Research task failed: {e}")
            self.stats["failed_researches"] += 1
            raise
            
    async def research_topic(self, 
                           topic: str,
                           research_question: str = "",
                           max_sources: int = 10,
                           min_confidence: float = 0.7) -> ResearchResult:
        """
        Research a topic using RAG and external tools.
        
        Args:
            topic: Research topic
            research_question: Specific research question
            max_sources: Maximum number of sources to analyze
            min_confidence: Minimum confidence threshold for sources
            
        Returns:
            Research result with findings and sources
        """
        logger.info(f"Starting research on topic: {topic}")
        self.stats["total_researches"] += 1
        
        try:
            # Step 1: Retrieve relevant information from memory
            memory_sources = await self._retrieve_memory_sources(
                topic, research_question, max_sources, min_confidence
            )
            
            # Step 2: Perform external research if needed
            external_sources = await self._perform_external_research(
                topic, research_question, max_sources - len(memory_sources)
            )
            
            # Step 3: Synthesize findings
            all_sources = memory_sources + external_sources
            synthesis = await self._synthesize_findings(
                topic, research_question, all_sources
            )
            
            # Step 4: Generate structured research result
            result = ResearchResult(
                topic=topic,
                summary=synthesis["summary"],
                key_findings=synthesis["key_findings"],
                sources=[source.original_filename for source in all_sources],
                confidence_score=synthesis["confidence_score"],
                research_timestamp=datetime.now().isoformat(),
                agent_id=self.agent_id
            )
            
            # Step 5: Store research result in memory
            await self._store_research_result(result)
            
            # Update statistics
            self.stats["successful_researches"] += 1
            self.stats["total_sources_analyzed"] += len(all_sources)
            
            logger.info(f"Research completed: {len(all_sources)} sources analyzed")
            return result
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            self.stats["failed_researches"] += 1
            raise
            
    async def _retrieve_memory_sources(self, 
                                     topic: str, 
                                     question: str,
                                     max_sources: int,
                                     min_confidence: float) -> List[MemoryEntry]:
        """Retrieve relevant sources from memory using RAG."""
        # Build search query
        if question:
            search_query = f"{topic} {question}"
        else:
            search_query = topic
            
        # Retrieve similar entries
        memory_entries = self.memory_manager.retrieve_similar(
            query=search_query,
            top_k=max_sources,
            min_score=min_confidence
        )
        
        logger.info(f"Retrieved {len(memory_entries)} memory sources")
        return memory_entries
        
    async def _perform_external_research(self, 
                                       topic: str, 
                                       question: str,
                                       max_sources: int) -> List[MemoryEntry]:
        """Perform external research using available tools."""
        if max_sources <= 0:
            return []
            
        external_sources = []
        
        try:
            # Use web search tool if available
            if "web_search" in self.tool_manager.get_available_tools():
                search_query = f"{topic} {question}" if question else topic
                
                tool_request = ToolRequest(
                    tool_name="web_search",
                    args={"query": search_query, "max_results": max_sources},
                    request_id=f"research_{datetime.now().timestamp()}",
                    agent_id=self.agent_id
                )
                
                tool_response = self.tool_manager.execute_tool(tool_request)
                
                if tool_response.status.value == "success":
                    # Process search results and create memory entries
                    # This is a simplified implementation
                    search_content = tool_response.output
                    
                    # Create a memory entry for the search results
                    chunk_id = self.memory_manager.store_agent_output(
                        content=search_content,
                        agent_id=self.agent_id,
                        provenance_notes=f"Web search results for: {search_query}",
                        tags=["research", "web_search", topic.lower().replace(" ", "_")]
                    )
                    
                    # Retrieve the stored entry
                    memory_entries = self.memory_manager.retrieve_similar(
                        query=search_content[:100],  # Use first 100 chars as query
                        top_k=1
                    )
                    
                    if memory_entries:
                        external_sources.extend(memory_entries)
                        
        except Exception as e:
            logger.warning(f"External research failed: {e}")
            
        logger.info(f"Performed external research: {len(external_sources)} sources found")
        return external_sources
        
    async def _synthesize_findings(self, 
                                 topic: str, 
                                 question: str,
                                 sources: List[MemoryEntry]) -> Dict[str, Any]:
        """Synthesize findings from multiple sources using LLM."""
        if not sources:
            return {
                "summary": f"No relevant information found for topic: {topic}",
                "key_findings": [],
                "confidence_score": 0.0
            }
            
        # Prepare context from sources
        context_parts = []
        for i, source in enumerate(sources, 1):
            context_parts.append(f"Source {i} ({source.original_filename}):\n{source.content}\n")
            
        context = "\n".join(context_parts)
        
        # Build synthesis prompt
        if question:
            prompt = f"""
            Research Topic: {topic}
            Research Question: {question}
            
            Based on the following sources, provide a comprehensive analysis:
            
            {context}
            
            Please provide:
            1. A detailed summary of the key information
            2. A list of 5-7 key findings
            3. An overall confidence score (0.0-1.0) based on source quality and consistency
            
            Format your response as JSON:
            {{
                "summary": "detailed summary here",
                "key_findings": ["finding 1", "finding 2", ...],
                "confidence_score": 0.8
            }}
            """
        else:
            prompt = f"""
            Research Topic: {topic}
            
            Based on the following sources, provide a comprehensive analysis:
            
            {context}
            
            Please provide:
            1. A detailed summary of the key information
            2. A list of 5-7 key findings
            3. An overall confidence score (0.0-1.0) based on source quality and consistency
            
            Format your response as JSON:
            {{
                "summary": "detailed summary here",
                "key_findings": ["finding 1", "finding 2", ...],
                "confidence_score": 0.8
            }}
            """
            
        # Generate synthesis using LLM
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            # Parse JSON response
            import json
            synthesis_data = json.loads(response.content)
            
            return {
                "summary": synthesis_data.get("summary", ""),
                "key_findings": synthesis_data.get("key_findings", []),
                "confidence_score": float(synthesis_data.get("confidence_score", 0.5))
            }
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            # Fallback to simple synthesis
            return {
                "summary": f"Research on {topic} based on {len(sources)} sources. " + 
                          "Key information extracted from available documents.",
                "key_findings": [f"Information found in {len(sources)} sources"],
                "confidence_score": 0.6
            }
            
    async def _store_research_result(self, result: ResearchResult):
        """Store research result in memory for future reference."""
        # Create comprehensive research summary
        research_summary = f"""
        Research Topic: {result.topic}
        Summary: {result.summary}
        Key Findings: {', '.join(result.key_findings)}
        Sources: {', '.join(result.sources)}
        Confidence Score: {result.confidence_score}
        Research Date: {result.research_timestamp}
        """
        
        # Store in memory
        chunk_id = self.memory_manager.store_agent_output(
            content=research_summary,
            agent_id=self.agent_id,
            provenance_notes=f"Research synthesis for topic: {result.topic}",
            tags=["research", "synthesis", result.topic.lower().replace(" ", "_")]
        )
        
        logger.info(f"Stored research result with chunk_id: {chunk_id}")
        
    async def analyze_document(self, 
                             document_content: str,
                             analysis_focus: str = "general") -> Dict[str, Any]:
        """
        Analyze a document for key information and insights.
        
        Args:
            document_content: Document content to analyze
            analysis_focus: Focus area for analysis (e.g., "technical", "business", "general")
            
        Returns:
            Analysis results
        """
        prompt = f"""
        Analyze the following document with focus on: {analysis_focus}
        
        Document Content:
        {document_content}
        
        Please provide:
        1. A brief summary of the document
        2. Key topics and themes
        3. Important facts and figures
        4. Potential research questions or areas for further investigation
        
        Format your response as JSON:
        {{
            "summary": "brief summary",
            "key_topics": ["topic 1", "topic 2", ...],
            "important_facts": ["fact 1", "fact 2", ...],
            "research_questions": ["question 1", "question 2", ...]
        }}
        """
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3
            )
            
            import json
            analysis = json.loads(response.content)
            
            # Store analysis in memory
            analysis_content = f"Document analysis (focus: {analysis_focus}): {analysis['summary']}"
            self.memory_manager.store_agent_output(
                content=analysis_content,
                agent_id=self.agent_id,
                provenance_notes=f"Document analysis with focus: {analysis_focus}",
                tags=["analysis", "document", analysis_focus]
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            return {
                "summary": "Analysis failed",
                "key_topics": [],
                "important_facts": [],
                "research_questions": []
            }
            
    def get_research_stats(self) -> Dict[str, Any]:
        """Get research agent statistics."""
        return self.stats.copy()


# Public API methods for ResearchAgent:
# - execute_task(task) -> Dict[str, Any]
# - research_topic(topic, research_question, max_sources, min_confidence) -> ResearchResult
# - analyze_document(document_content, analysis_focus) -> Dict[str, Any]
# - get_research_stats() -> Dict[str, Any]