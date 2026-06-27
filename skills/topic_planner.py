"""
SK-04: 选题策划 Skill

基于发布记录和热门趋势，推荐下周内容选题。
"""

from typing import Any, Dict, List, Optional
from core.skill_base import BaseSkill, SkillResult
import logging

logger = logging.getLogger(__name__)


class TopicPlanner(BaseSkill):
    """SK-04: 选题策划 Skill"""

    def __init__(self, model_router=None):
        super().__init__(
            skill_id="SK-04",
            name="选题策划",
            description="基于发布记录和热门趋势，推荐下周内容选题",
            input_schema={
                "publish_history": {"required": False, "type": "list"},
                "trends": {"required": False, "type": "list"},
                "customer_questions": {"required": False, "type": "list"},
            },
            output_schema={
                "topics": {"type": "list"},
            },
        )
        self.model_router = model_router

    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """执行选题策划"""
        try:
            publish_history = input_data.get("publish_history", [])
            trends = input_data.get("trends", [])
            customer_questions = input_data.get("customer_questions", [])
            
            topics = self._plan_topics(publish_history, trends, customer_questions)
            
            return SkillResult(
                skill_id=self.skill_id,
                output={"topics": topics},
                success=True,
            )
        except Exception as e:
            logger.error(f"SK-04 execution failed: {e}")
            return SkillResult(
                skill_id=self.skill_id,
                output=None,
                success=False,
                error=str(e),
            )

    def _plan_topics(self, publish_history, trends, customer_questions) -> List[Dict[str, Any]]:
        """策划选题"""
        topics = []
        
        # 基于客户问题生成选题
        for question in customer_questions[:3]:
            topics.append({
                "title": f"解答：{question}",
                "reason": "客户高频问题",
                "expected_effect": "提升信任度",
            })
        
        # 基于趋势生成选题
        for trend in trends[:2]:
            topics.append({
                "title": f"热点解读：{trend}",
                "reason": "热门趋势",
                "expected_effect": "提升曝光",
            })
        
        # 默认选题
        default_topics = [
            "探房日记：XX小区实拍",
            "买房攻略：首次购房必看",
            "政策解读：最新限购政策",
        ]
        
        for topic in default_topics[:3 - len(topics)]:
            topics.append({
                "title": topic,
                "reason": "常规内容",
                "expected_effect": "稳定输出",
            })
        
        return topics
