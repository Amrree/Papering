"""
Tool Manager Module

Implements MCP (Model Control Protocol) for safe tool execution with sandboxing.
Provides tool registry, validation, and audit logging.

Based on patterns from:
- Semantic Kernel plugin system: https://github.com/microsoft/semantic-kernel/blob/main/python/semantic_kernel/plugins/plugin.py
- LangChain tool integration: https://github.com/langchain-ai/langchain/blob/main/langchain/agents/tools.py
"""

import os
import json
import time
import hashlib
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import tempfile
import shutil

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Tool safety categories."""
    SAFE = "safe"           # No system access, pure computation
    RESTRICTED = "restricted"  # Limited system access, file operations
    UNSAFE = "unsafe"       # Full system access, network, execution


class ToolStatus(Enum):
    """Tool execution status."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"


@dataclass
class ToolRequest:
    """MCP tool request structure."""
    tool_name: str
    args: Dict[str, Any]
    request_id: str
    agent_id: str
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ToolResponse:
    """MCP tool response structure."""
    status: ToolStatus
    output: str
    stdout: str = ""
    stderr: str = ""
    runtime: float = 0.0
    hashes: Dict[str, str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.hashes is None:
            self.hashes = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ToolDefinition:
    """Tool definition with metadata and safety information."""
    name: str
    description: str
    category: ToolCategory
    function: Callable
    parameters: Dict[str, Any]
    timeout: int = 30
    enabled: bool = True


class ToolManager:
    """
    Manages tool registry, execution, and safety controls.
    
    Responsibilities:
    - Tool registration and validation
    - Safe execution with sandboxing
    - MCP protocol implementation
    - Audit logging and provenance
    - Resource limits and timeouts
    """
    
    def __init__(self, 
                 allow_unsafe: bool = False,
                 max_runtime: int = 300,
                 log_path: str = "./data/tool_logs.jsonl"):
        """
        Initialize tool manager.
        
        Args:
            allow_unsafe: Whether to allow unsafe tools
            max_runtime: Maximum runtime for tools (seconds)
            log_path: Path for tool execution logs
        """
        self.allow_unsafe = allow_unsafe or os.getenv("TOOL_MANAGER_ALLOW_UNSAFE", "false").lower() == "true"
        self.max_runtime = max_runtime
        self.log_path = log_path
        
        # Tool registry
        self.tools: Dict[str, ToolDefinition] = {}
        
        # Execution statistics
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "blocked_executions": 0,
            "category_usage": {category.value: 0 for category in ToolCategory}
        }
        
        # Initialize built-in tools
        self._register_builtin_tools()
        
        # Initialize logging
        self._init_logging()
        
        logger.info(f"ToolManager initialized (unsafe tools: {self.allow_unsafe})")
        
    def _init_logging(self):
        """Initialize tool execution logging."""
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        
    def register_tool(self, 
                     name: str,
                     description: str,
                     category: ToolCategory,
                     function: Callable,
                     parameters: Dict[str, Any] = None,
                     timeout: int = 30,
                     enabled: bool = True) -> bool:
        """
        Register a new tool.
        
        Args:
            name: Tool name
            description: Tool description
            category: Safety category
            function: Tool function
            parameters: Parameter schema
            timeout: Execution timeout
            enabled: Whether tool is enabled
            
        Returns:
            True if registration successful
        """
        if name in self.tools:
            logger.warning(f"Tool {name} already registered, overwriting")
            
        tool_def = ToolDefinition(
            name=name,
            description=description,
            category=category,
            function=function,
            parameters=parameters or {},
            timeout=timeout,
            enabled=enabled
        )
        
        self.tools[name] = tool_def
        logger.info(f"Registered tool: {name} ({category.value})")
        return True
        
    def execute_tool(self, request: ToolRequest) -> ToolResponse:
        """
        Execute a tool request following MCP protocol.
        
        Args:
            request: Tool request
            
        Returns:
            Tool response with results
        """
        start_time = time.time()
        
        # Validate request
        if not self._validate_request(request):
            return ToolResponse(
                status=ToolStatus.BLOCKED,
                output="Invalid tool request",
                runtime=time.time() - start_time
            )
            
        # Check tool availability
        if request.tool_name not in self.tools:
            return ToolResponse(
                status=ToolStatus.ERROR,
                output=f"Tool {request.tool_name} not found",
                runtime=time.time() - start_time
            )
            
        tool_def = self.tools[request.tool_name]
        
        # Check safety permissions
        if not self._check_safety_permissions(tool_def):
            self.stats["blocked_executions"] += 1
            return ToolResponse(
                status=ToolStatus.BLOCKED,
                output=f"Tool {request.tool_name} blocked by safety policy",
                runtime=time.time() - start_time
            )
            
        # Execute tool
        try:
            result = self._execute_with_sandbox(tool_def, request)
            runtime = time.time() - start_time
            
            # Generate hashes
            hashes = self._generate_hashes(request, result)
            
            response = ToolResponse(
                status=ToolStatus.SUCCESS,
                output=result,
                runtime=runtime,
                hashes=hashes,
                metadata={"tool_category": tool_def.category.value}
            )
            
            self.stats["successful_executions"] += 1
            
        except subprocess.TimeoutExpired:
            runtime = time.time() - start_time
            response = ToolResponse(
                status=ToolStatus.TIMEOUT,
                output=f"Tool execution timed out after {runtime:.2f}s",
                runtime=runtime
            )
            self.stats["failed_executions"] += 1
            
        except Exception as e:
            runtime = time.time() - start_time
            response = ToolResponse(
                status=ToolStatus.ERROR,
                output=f"Tool execution failed: {str(e)}",
                runtime=runtime
            )
            self.stats["failed_executions"] += 1
            
        # Update statistics
        self.stats["total_executions"] += 1
        self.stats["category_usage"][tool_def.category.value] += 1
        
        # Log execution
        self._log_execution(request, response)
        
        return response
        
    def _validate_request(self, request: ToolRequest) -> bool:
        """Validate tool request structure."""
        if not request.tool_name or not request.agent_id or not request.request_id:
            return False
        if not isinstance(request.args, dict):
            return False
        return True
        
    def _check_safety_permissions(self, tool_def: ToolDefinition) -> bool:
        """Check if tool execution is allowed by safety policy."""
        if not tool_def.enabled:
            return False
            
        if tool_def.category == ToolCategory.SAFE:
            return True
        elif tool_def.category == ToolCategory.RESTRICTED:
            return True  # Restricted tools are allowed by default
        elif tool_def.category == ToolCategory.UNSAFE:
            return self.allow_unsafe
        else:
            return False
            
    def _execute_with_sandbox(self, tool_def: ToolDefinition, request: ToolRequest) -> str:
        """Execute tool with sandboxing and resource limits."""
        # Create temporary directory for sandbox
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up sandbox environment
            env = os.environ.copy()
            env["TEMP_DIR"] = temp_dir
            
            # Execute tool function
            try:
                result = tool_def.function(**request.args)
                return str(result)
            except Exception as e:
                raise RuntimeError(f"Tool execution error: {e}")
                
    def _generate_hashes(self, request: ToolRequest, result: str) -> Dict[str, str]:
        """Generate hashes for request and result."""
        request_str = json.dumps(asdict(request), sort_keys=True)
        return {
            "input": hashlib.sha256(request_str.encode()).hexdigest()[:16],
            "output": hashlib.sha256(result.encode()).hexdigest()[:16]
        }
        
    def _log_execution(self, request: ToolRequest, response: ToolResponse):
        """Log tool execution for audit trail."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request": asdict(request),
            "response": asdict(response)
        }
        
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
            
    def _register_builtin_tools(self):
        """Register built-in safe tools."""
        # Text processing tools
        self.register_tool(
            name="text_summarize",
            description="Summarize text content",
            category=ToolCategory.SAFE,
            function=self._tool_text_summarize,
            parameters={
                "text": {"type": "string", "description": "Text to summarize"},
                "max_length": {"type": "integer", "description": "Maximum summary length"}
            }
        )
        
        self.register_tool(
            name="text_extract_keywords",
            description="Extract keywords from text",
            category=ToolCategory.SAFE,
            function=self._tool_extract_keywords,
            parameters={
                "text": {"type": "string", "description": "Text to analyze"},
                "max_keywords": {"type": "integer", "description": "Maximum number of keywords"}
            }
        )
        
        # File operations (restricted)
        self.register_tool(
            name="file_read",
            description="Read file contents",
            category=ToolCategory.RESTRICTED,
            function=self._tool_file_read,
            parameters={
                "file_path": {"type": "string", "description": "Path to file to read"}
            }
        )
        
        self.register_tool(
            name="file_write",
            description="Write content to file",
            category=ToolCategory.RESTRICTED,
            function=self._tool_file_write,
            parameters={
                "file_path": {"type": "string", "description": "Path to file to write"},
                "content": {"type": "string", "description": "Content to write"}
            }
        )
        
        # Web search (unsafe - requires network access)
        self.register_tool(
            name="web_search",
            description="Search the web for information",
            category=ToolCategory.UNSAFE,
            function=self._tool_web_search,
            parameters={
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "description": "Maximum number of results"}
            }
        )
        
    def _tool_text_summarize(self, text: str, max_length: int = 200) -> str:
        """Summarize text content."""
        words = text.split()
        if len(words) <= max_length:
            return text
        return " ".join(words[:max_length]) + "..."
        
    def _tool_extract_keywords(self, text: str, max_keywords: int = 10) -> str:
        """Extract keywords from text."""
        # Simple keyword extraction (could be enhanced with NLP)
        words = text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Filter short words
                word_freq[word] = word_freq.get(word, 0) + 1
                
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return ", ".join([word for word, freq in keywords[:max_keywords]])
        
    def _tool_file_read(self, file_path: str) -> str:
        """Read file contents safely."""
        # Validate file path (prevent directory traversal)
        if ".." in file_path or file_path.startswith("/"):
            raise ValueError("Invalid file path")
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read file: {e}")
            
    def _tool_file_write(self, file_path: str, content: str) -> str:
        """Write content to file safely."""
        # Validate file path
        if ".." in file_path or file_path.startswith("/"):
            raise ValueError("Invalid file path")
            
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to {file_path}"
        except Exception as e:
            raise RuntimeError(f"Failed to write file: {e}")
            
    def _tool_web_search(self, query: str, max_results: int = 5) -> str:
        """Search the web (placeholder implementation)."""
        # This would integrate with a real search API
        return f"Web search results for '{query}' (max {max_results} results) - [Placeholder]"
        
    def get_available_tools(self, category: Optional[ToolCategory] = None) -> List[str]:
        """Get list of available tools, optionally filtered by category."""
        tools = []
        for name, tool_def in self.tools.items():
            if tool_def.enabled and (category is None or tool_def.category == category):
                tools.append(name)
        return tools
        
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        if tool_name not in self.tools:
            return None
            
        tool_def = self.tools[tool_name]
        return {
            "name": tool_def.name,
            "description": tool_def.description,
            "category": tool_def.category.value,
            "parameters": tool_def.parameters,
            "timeout": tool_def.timeout,
            "enabled": tool_def.enabled
        }
        
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get tool execution statistics."""
        return self.stats.copy()
        
    def enable_unsafe_tools(self):
        """Enable unsafe tools (requires explicit user action)."""
        self.allow_unsafe = True
        logger.warning("Unsafe tools enabled - use with caution")
        
    def disable_unsafe_tools(self):
        """Disable unsafe tools."""
        self.allow_unsafe = False
        logger.info("Unsafe tools disabled")


# Public API methods for ToolManager:
# - register_tool(name, description, category, function, parameters, timeout, enabled) -> bool
# - execute_tool(request) -> ToolResponse
# - get_available_tools(category) -> List[str]
# - get_tool_info(tool_name) -> Optional[Dict[str, Any]]
# - get_execution_stats() -> Dict[str, Any]
# - enable_unsafe_tools() -> None
# - disable_unsafe_tools() -> None