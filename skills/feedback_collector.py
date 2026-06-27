"""
SK-12: 用户反馈收集 Skill

收集经纪人评分和采纳率，自动优化 Agent Prompt。
实现用户反馈闭环。
"""

from typing import Any, Dict, List, Optional
from core.skill_base import BaseSkill, SkillResult
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class FeedbackCollector(BaseSkill):
    """SK-12: 用户反馈收集 Skill"""

    def __init__(self, model_router=None):
        super().__init__(
            skill_id="SK-12",
            name="用户反馈收集",
            description="收集经纪人评分和采纳率，自动优化 Agent Prompt",
            input_schema={
                "feedback_data": {"required": True, "type": "dict"},
            },
            output_schema={
                "feedback_id": {"type": "str"},
                "optimization_suggestions": {"type": "list"},
            },
        )
        self.model_router = model_router
        self._feedback_store: List[Dict] = []

    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """执行反馈收集"""
        try:
            feedback = input_data.get("feedback_data", {})
            feedback["timestamp"] = datetime.now().isoformat()
            feedback["feedback_id"] = f"fb_{len(self._feedback_store) + 1}"

            self._feedback_store.append(feedback)

            optimization = self._analyze_feedback(feedback)

            return SkillResult(
                skill_id=self.skill_id,
                output={
                    "feedback_id": feedback["feedback_id"],
                    "recorded": True,
                    "total_feedback": len(self._feedback_store),
                    "optimization_suggestions": optimization,
                },
                success=True,
            )

        except Exception as e:
            logger.error(f"SK-12 execution failed: {e}")
            return SkillResult(
                skill_id=self.skill_id,
                output=None,
                success=False,
                error=str(e),
            )

    def _analyze_feedback(self, feedback: Dict) -> List[str]:
        """分析反馈，生成 Prompt 优化建议"""
        suggestions = []
        score = feedback.get("score", 3)

        if score <= 2:
            suggestions.append(f"用户对 '{feedback.get('agent_name','?')}' 的满意度较低({score}/5)，建议调整该 Agent 的 Prompt 温度参数")
        if feedback.get("needs_improvement"):
            for item in feedback.get("needs_improvement", []):
                suggestions.append(f"改进点: {item}")
        if feedback.get("good_points"):
            suggestions.append(f"保持: {'、'.join(feedback['good_points'][:3])}")

        return suggestions

    def get_stats(self) -> Dict:
        """获取反馈统计"""
        if not self._feedback_store:
            return {"total": 0, "avg_score": 0}

        scores = [fb.get("score", 3) for fb in self._feedback_store]
        return {
            "total": len(self._feedback_store),
            "avg_score": sum(scores) / len(scores),
            "high_scores": sum(1 for s in scores if s >= 4),
            "low_scores": sum(1 for s in scores if s <= 2),
        }
