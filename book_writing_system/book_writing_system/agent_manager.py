"""
Agent Manager Module

Orchestrates multi-agent workflows with task routing, concurrency, and lifecycle management.
Implements agent coordination patterns with audit logging.

Based on patterns from:
- CrewAI agent orchestration: https://github.com/joaomdmoura/crewAI/blob/main/crewai/agent.py
- LangGraph state management: https://github.com/langchain-ai/langgraph/blob/main/langgraph/graph/state.py
- AutoGen conversation patterns: https://github.com/microsoft/autogen/blob/main/autogen/agentchat/conversable_agent.py
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentRole(Enum):
    """Agent roles in the system."""
    RESEARCH = "research"
    WRITER = "writer"
    EDITOR = "editor"
    TOOL = "tool"


@dataclass
class Task:
    """Represents a task in the agent workflow."""
    task_id: str
    agent_role: AgentRole
    description: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowState:
    """State management for agent workflows."""
    workflow_id: str
    current_task: Optional[str] = None
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class AgentManager:
    """
    Manages agent orchestration, task routing, and workflow coordination.
    
    Responsibilities:
    - Agent lifecycle management
    - Task routing and dependency resolution
    - Workflow state management
    - Concurrency control and coordination
    - Audit logging and monitoring
    """
    
    def __init__(self, 
                 max_concurrent_tasks: int = 3,
                 log_path: str = "./data/agent_logs.jsonl"):
        """
        Initialize agent manager.
        
        Args:
            max_concurrent_tasks: Maximum concurrent task execution
            log_path: Path for agent execution logs
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self.log_path = log_path
        
        # Agent registry
        self.agents: Dict[AgentRole, Any] = {}
        
        # Task management
        self.tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Workflow management
        self.workflows: Dict[str, WorkflowState] = {}
        
        # Statistics
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "active_workflows": 0,
            "agent_usage": {role.value: 0 for role in AgentRole}
        }
        
        # Initialize logging
        self._init_logging()
        
        logger.info("AgentManager initialized")
        
    def _init_logging(self):
        """Initialize agent execution logging."""
        import os
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        
    def register_agent(self, role: AgentRole, agent_instance: Any):
        """
        Register an agent instance.
        
        Args:
            role: Agent role
            agent_instance: Agent instance
        """
        self.agents[role] = agent_instance
        logger.info(f"Registered agent: {role.value}")
        
    def create_workflow(self, workflow_id: Optional[str] = None) -> str:
        """
        Create a new workflow.
        
        Args:
            workflow_id: Optional workflow ID
            
        Returns:
            Workflow ID
        """
        if workflow_id is None:
            workflow_id = str(uuid.uuid4())
            
        workflow = WorkflowState(workflow_id=workflow_id)
        self.workflows[workflow_id] = workflow
        self.stats["active_workflows"] += 1
        
        logger.info(f"Created workflow: {workflow_id}")
        return workflow_id
        
    def add_task(self, 
                workflow_id: str,
                agent_role: AgentRole,
                description: str,
                input_data: Dict[str, Any],
                dependencies: List[str] = None,
                metadata: Dict[str, Any] = None) -> str:
        """
        Add a task to a workflow.
        
        Args:
            workflow_id: Workflow ID
            agent_role: Agent role for task
            description: Task description
            input_data: Task input data
            dependencies: Task dependencies
            metadata: Task metadata
            
        Returns:
            Task ID
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
            
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            agent_role=agent_role,
            description=description,
            input_data=input_data,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        
        self.tasks[task_id] = task
        self.stats["total_tasks"] += 1
        
        logger.info(f"Added task {task_id} to workflow {workflow_id}")
        return task_id
        
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow with task orchestration.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow execution results
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
            
        workflow = self.workflows[workflow_id]
        logger.info(f"Starting workflow execution: {workflow_id}")
        
        # Get all tasks for this workflow
        workflow_tasks = [task for task in self.tasks.values() 
                         if task.task_id not in workflow.completed_tasks and 
                         task.task_id not in workflow.failed_tasks]
        
        # Execute tasks with dependency resolution
        results = {}
        while workflow_tasks:
            # Find tasks with satisfied dependencies
            ready_tasks = []
            for task in workflow_tasks:
                if all(dep in workflow.completed_tasks for dep in task.dependencies):
                    ready_tasks.append(task)
                    
            if not ready_tasks:
                # Check for circular dependencies
                remaining_deps = set()
                for task in workflow_tasks:
                    remaining_deps.update(task.dependencies)
                if remaining_deps:
                    logger.error(f"Circular dependency detected in workflow {workflow_id}")
                    break
                    
            # Execute ready tasks concurrently (up to max_concurrent_tasks)
            semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
            task_coroutines = [
                self._execute_task_with_semaphore(semaphore, task, workflow_id)
                for task in ready_tasks
            ]
            
            if task_coroutines:
                task_results = await asyncio.gather(*task_coroutines, return_exceptions=True)
                
                # Process results
                for task, result in zip(ready_tasks, task_results):
                    if isinstance(result, Exception):
                        logger.error(f"Task {task.task_id} failed: {result}")
                        workflow.failed_tasks.append(task.task_id)
                    else:
                        results[task.task_id] = result
                        workflow.completed_tasks.append(task.task_id)
                        
                # Remove completed tasks from workflow_tasks
                workflow_tasks = [task for task in workflow_tasks 
                                if task.task_id not in workflow.completed_tasks and
                                task.task_id not in workflow.failed_tasks]
                
        # Update workflow state
        workflow.updated_at = datetime.now().isoformat()
        
        logger.info(f"Workflow {workflow_id} completed: {len(workflow.completed_tasks)} tasks completed, {len(workflow.failed_tasks)} failed")
        
        return {
            "workflow_id": workflow_id,
            "completed_tasks": workflow.completed_tasks,
            "failed_tasks": workflow.failed_tasks,
            "results": results,
            "context": workflow.context
        }
        
    async def _execute_task_with_semaphore(self, semaphore: asyncio.Semaphore, task: Task, workflow_id: str):
        """Execute a task with semaphore for concurrency control."""
        async with semaphore:
            return await self._execute_task(task, workflow_id)
            
    async def _execute_task(self, task: Task, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a single task.
        
        Args:
            task: Task to execute
            workflow_id: Workflow ID
            
        Returns:
            Task execution results
        """
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now().isoformat()
        
        # Log task start
        self._log_task_event(task, "started", workflow_id)
        
        try:
            # Get agent for task
            if task.agent_role not in self.agents:
                raise ValueError(f"No agent registered for role: {task.agent_role}")
                
            agent = self.agents[task.agent_role]
            
            # Execute task
            if hasattr(agent, 'execute_task'):
                result = await agent.execute_task(task)
            elif hasattr(agent, 'process'):
                result = await agent.process(task.input_data)
            else:
                raise ValueError(f"Agent {task.agent_role} does not support task execution")
                
            # Update task
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            task.output_data = result
            
            # Update statistics
            self.stats["completed_tasks"] += 1
            self.stats["agent_usage"][task.agent_role.value] += 1
            
            # Log task completion
            self._log_task_event(task, "completed", workflow_id)
            
            return result
            
        except Exception as e:
            # Update task
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now().isoformat()
            task.error_message = str(e)
            
            # Update statistics
            self.stats["failed_tasks"] += 1
            
            # Log task failure
            self._log_task_event(task, "failed", workflow_id)
            
            raise
            
    def _log_task_event(self, task: Task, event: str, workflow_id: str):
        """Log task events for audit trail."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "workflow_id": workflow_id,
            "task_id": task.task_id,
            "agent_role": task.agent_role.value,
            "description": task.description,
            "status": task.status.value,
            "error_message": task.error_message
        }
        
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
            
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status and progress."""
        if workflow_id not in self.workflows:
            return None
            
        workflow = self.workflows[workflow_id]
        total_tasks = len([t for t in self.tasks.values() 
                          if t.task_id not in workflow.completed_tasks and 
                          t.task_id not in workflow.failed_tasks])
        
        return {
            "workflow_id": workflow_id,
            "status": "completed" if total_tasks == 0 else "in_progress",
            "completed_tasks": len(workflow.completed_tasks),
            "failed_tasks": len(workflow.failed_tasks),
            "total_tasks": len(workflow.completed_tasks) + len(workflow.failed_tasks) + total_tasks,
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at
        }
        
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and details."""
        if task_id not in self.tasks:
            return None
            
        task = self.tasks[task_id]
        return {
            "task_id": task_id,
            "agent_role": task.agent_role.value,
            "description": task.description,
            "status": task.status.value,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "error_message": task.error_message,
            "dependencies": task.dependencies,
            "metadata": task.metadata
        }
        
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent execution statistics."""
        return self.stats.copy()
        
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        if workflow_id not in self.workflows:
            return False
            
        # Cancel running tasks
        for task_id, running_task in self.running_tasks.items():
            if not running_task.done():
                running_task.cancel()
                
        # Update workflow state
        workflow = self.workflows[workflow_id]
        workflow.updated_at = datetime.now().isoformat()
        
        logger.info(f"Cancelled workflow: {workflow_id}")
        return True
        
    def cleanup_completed_workflows(self):
        """Clean up completed workflows to free memory."""
        completed_workflows = []
        for workflow_id, workflow in self.workflows.items():
            total_tasks = len([t for t in self.tasks.values() 
                              if t.task_id not in workflow.completed_tasks and 
                              t.task_id not in workflow.failed_tasks])
            if total_tasks == 0:
                completed_workflows.append(workflow_id)
                
        for workflow_id in completed_workflows:
            del self.workflows[workflow_id]
            self.stats["active_workflows"] -= 1
            
        logger.info(f"Cleaned up {len(completed_workflows)} completed workflows")


# Public API methods for AgentManager:
# - register_agent(role, agent_instance) -> None
# - create_workflow(workflow_id) -> str
# - add_task(workflow_id, agent_role, description, input_data, dependencies, metadata) -> str
# - execute_workflow(workflow_id) -> Dict[str, Any]
# - get_workflow_status(workflow_id) -> Optional[Dict[str, Any]]
# - get_task_status(task_id) -> Optional[Dict[str, Any]]
# - get_agent_stats() -> Dict[str, Any]
# - cancel_workflow(workflow_id) -> bool
# - cleanup_completed_workflows() -> None