"""
SK-06: 合规检查 Skill

对任意待发布文本进行合规检查，输出合规报告。
"""

from typing import Any, Dict, List, Optional
from core.skill_base import BaseSkill, SkillResult
from compliance.rule_engine import ComplianceRuleEngine, ComplianceResult
import logging

logger = logging.getLogger(__name__)


class ComplianceChecker(BaseSkill):
    """SK-06: 合规检查 Skill"""

    def __init__(self, rule_engine: Optional[ComplianceRuleEngine] = None):
        super().__init__(
            skill_id="SK-06",
            name="合规检查",
            description="对任意待发布文本进行合规检查",
            input_schema={
                "text": {"required": True, "type": "str"},
            },
            output_schema={
                "status": {"type": "str"},
                "rule_matches": {"type": "list"},
                "ai_concerns": {"type": "list"},
                "suggestions": {"type": "list"},
            },
        )
        self.rule_engine = rule_engine or ComplianceRuleEngine()

    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """执行合规检查"""
        try:
            text = input_data.get("text", "")
            
            if not text:
                return SkillResult(
                    skill_id=self.skill_id,
                    output={
                        "status": "compliant",
                        "rule_matches": [],
                        "ai_concerns": [],
                        "suggestions": [],
                        "risk_level": "low",
                    },
                    success=True,
                )
            
            result = self.rule_engine.check(text)
            
            output = {
                "status": "compliant" if result.is_compliant else "violation",
                "rule_matches": result.violations,
                "ai_concerns": [],  # Layer 2 AI 检查（Phase 2）
                "suggestions": result.suggestions,
                "risk_level": result.risk_level,
            }
            
            return SkillResult(
                skill_id=self.skill_id,
                output=output,
                success=True,
            )
        except Exception as e:
            logger.error(f"SK-06 execution failed: {e}")
            return SkillResult(
                skill_id=self.skill_id,
                output=None,
                success=False,
                error=str(e),
            )
