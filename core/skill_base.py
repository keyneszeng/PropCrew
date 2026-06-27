"""
Skill 基类

定义所有 Skill 的通用接口和行为。
Skill 是可复用的功能模块，可以被多个 Agent 共享使用。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class SkillResult:
    """Skill 执行结果"""
    skill_id: str
    output: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "output": self.output,
            "metadata": self.metadata,
            "success": self.success,
            "error": self.error,
        }


class BaseSkill(ABC):
    """
    Skill 基类
    
    所有 Skill 必须继承此类并实现 execute() 方法。
    Skill 是独立的功能模块，可以被多个 Agent 复用。
    """

    def __init__(
        self,
        skill_id: str,
        name: str,
        description: str,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
    ):
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """
        执行 Skill
        
        Args:
            input_data: 输入数据，必须符合 input_schema
            
        Returns:
            SkillResult: 执行结果
        """
        pass

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据是否符合 schema"""
        # 简单的 schema 验证
        for field_name, field_schema in self.input_schema.items():
            if field_schema.get("required", False) and field_name not in input_data:
                return False
        return True

    def get_info(self) -> Dict[str, Any]:
        """获取 Skill 信息"""
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }

    def __repr__(self):
        return f"<Skill: {self.name} ({self.skill_id})>"
