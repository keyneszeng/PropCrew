"""
Task Manager - 任务管理与编排

负责任务的创建、调度、执行和结果管理。
支持任务队列、优先级、依赖关系和状态跟踪。
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Task:
    """任务定义"""
    task_id: str
    name: str
    agent_id: str
    input_data: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "agent_id": self.agent_id,
            "input_data": self.input_data,
            "priority": self.priority.value,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }


class TaskManager:
    """
    任务管理器
    
    功能：
    1. 任务创建和调度
    2. 优先级队列
    3. 依赖关系管理
    4. 状态跟踪
    5. 并发控制
    """

    def __init__(self, max_concurrent: int = 5):
        self._tasks: Dict[str, Task] = {}
        self._task_queue: List[str] = []
        self._max_concurrent = max_concurrent
        self._running_count = 0
        self._lock = asyncio.Lock()
        self._agent_registry: Dict[str, Any] = {}

    def register_agent(self, agent_id: str, agent: Any) -> None:
        """注册 Agent"""
        self._agent_registry[agent_id] = agent
        logger.info(f"[TaskManager] Registered agent: {agent_id}")

    def create_task(
        self,
        name: str,
        agent_id: str,
        input_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """创建任务"""
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            name=name,
            agent_id=agent_id,
            input_data=input_data,
            priority=priority,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )
        self._tasks[task_id] = task
        self._task_queue.append(task_id)
        logger.info(f"[TaskManager] Created task: {task_id} ({name})")
        return task

    async def execute_task(self, task_id: str) -> Task:
        """执行单个任务"""
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")

        agent = self._agent_registry.get(task.agent_id)
        if not agent:
            task.status = TaskStatus.FAILED
            task.error = f"Agent not found: {task.agent_id}"
            return task

        async with self._lock:
            if self._running_count >= self._max_concurrent:
                logger.warning(f"[TaskManager] Max concurrent tasks reached ({self._max_concurrent})")
                return task

            self._running_count += 1
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now().isoformat()

        try:
            result = await agent.execute(task.input_data)
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            logger.info(f"[TaskManager] Task completed: {task_id}")
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now().isoformat()
            logger.error(f"[TaskManager] Task failed: {task_id} - {e}")
        finally:
            async with self._lock:
                self._running_count -= 1

        return task

    async def execute_workflow(
        self,
        workflow_name: str,
        tasks: List[Task],
        context_bus=None,
    ) -> Dict[str, Any]:
        """
        执行工作流
        
        Args:
            workflow_name: 工作流名称
            tasks: 任务列表
            context_bus: 上下文总线
            
        Returns:
            工作流执行结果
        """
        logger.info(f"[TaskManager] Starting workflow: {workflow_name}")
        
        results = {}
        for task in tasks:
            # 检查依赖
            if task.dependencies:
                for dep_id in task.dependencies:
                    if dep_id not in results:
                        raise ValueError(f"Dependency not satisfied: {dep_id}")
            
            # 执行任务
            result_task = await self.execute_task(task.task_id)
            results[task.task_id] = result_task.result
            
            # 更新上下文
            if context_bus and result_task.status == TaskStatus.COMPLETED:
                context_bus.update_context(
                    {f"task_{task.task_id}_result": result_task.result},
                    agent_id=task.agent_id,
                )

        logger.info(f"[TaskManager] Workflow completed: {workflow_name}")
        return {
            "workflow_name": workflow_name,
            "results": results,
            "completed_at": datetime.now().isoformat(),
        }

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self._tasks.get(task_id)

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """按状态获取任务"""
        return [t for t in self._tasks.values() if t.status == status]

    def get_pending_tasks(self) -> List[Task]:
        """获取待执行任务（按优先级排序）"""
        pending = [t for t in self._tasks.values() if t.status == TaskStatus.PENDING]
        return sorted(pending, key=lambda x: x.priority.value, reverse=True)

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            logger.info(f"[TaskManager] Task cancelled: {task_id}")
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """获取任务统计"""
        stats = {
            "total": len(self._tasks),
            "pending": len(self.get_tasks_by_status(TaskStatus.PENDING)),
            "running": len(self.get_tasks_by_status(TaskStatus.RUNNING)),
            "completed": len(self.get_tasks_by_status(TaskStatus.COMPLETED)),
            "failed": len(self.get_tasks_by_status(TaskStatus.FAILED)),
            "cancelled": len(self.get_tasks_by_status(TaskStatus.CANCELLED)),
            "max_concurrent": self._max_concurrent,
            "current_running": self._running_count,
        }
        return stats

    def clear_completed(self) -> int:
        """清理已完成的任务"""
        completed_ids = [t.task_id for t in self._tasks.values() if t.status == TaskStatus.COMPLETED]
        for task_id in completed_ids:
            del self._tasks[task_id]
        logger.info(f"[TaskManager] Cleared {len(completed_ids)} completed tasks")
        return len(completed_ids)
