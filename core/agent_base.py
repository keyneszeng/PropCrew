"""
Agent 基类

定义所有 Agent 的通用接口和行为。
参考 LangGraph 的 StateGraph 节点模式。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Agent 执行结果"""
    agent_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "content": self.content,
            "metadata": self.metadata,
            "success": self.success,
            "error": self.error,
        }


class BaseAgent(ABC):
    """
    Agent 基类
    
    所有 Agent 必须继承此类并实现 execute() 方法。
    Agent 通过 Context Bus 共享上下文，通过 Task Manager 进行编排。
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        system_prompt: str,
        model: str = "deepseek-v3",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.skills: List[Any] = []
        self._context_bus = None

    def set_context_bus(self, context_bus):
        """设置 Context Bus 引用"""
        self._context_bus = context_bus

    def add_skill(self, skill):
        """添加 Skill"""
        self.skills.append(skill)

    def get_context(self) -> Dict[str, Any]:
        """获取当前上下文"""
        if self._context_bus:
            return self._context_bus.get_context()
        return {}

    def update_context(self, updates: Dict[str, Any]):
        """更新上下文"""
        if self._context_bus:
            self._context_bus.update_context(updates)

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        执行 Agent 任务
        
        Args:
            input_data: 输入数据，包含任务相关的所有信息
            
        Returns:
            AgentResult: 执行结果
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """获取 Agent 信息"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "skills": [s.skill_id for s in self.skills if hasattr(s, 'skill_id')],
        }

    def __repr__(self):
        return f"<Agent: {self.name} ({self.agent_id})>"
