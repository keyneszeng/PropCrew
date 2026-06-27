"""
SK-08: 政策科普转化 Skill

将政策原文转化为通俗易懂的科普内容。
"""

from typing import Any, Dict, List, Optional
from core.skill_base import BaseSkill, SkillResult
import logging

logger = logging.getLogger(__name__)


class PolicyConverter(BaseSkill):
    """SK-08: 政策科普转化 Skill"""

    def __init__(self, model_router=None):
        super().__init__(
            skill_id="SK-08",
            name="政策科普转化",
            description="将政策原文转化为通俗易懂的科普内容",
            input_schema={
                "policy_text": {"required": True, "type": "str"},
                "target_audience": {"required": False, "type": "str"},
            },
            output_schema={
                "summary": {"type": "str"},
                "impact_analysis": {"type": "list"},
                "action_guide": {"type": "list"},
                "output_plans": {"type": "list"},
            },
        )
        self.model_router = model_router

    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """执行政策科普转化"""
        try:
            policy_text = input_data.get("policy_text", "")
            target_audience = input_data.get("target_audience", "general")
            
            if not policy_text:
                return SkillResult(
                    skill_id=self.skill_id,
                    output=None,
                    success=False,
                    error="政策原文不能为空",
                )
            
            result = self._convert_policy(policy_text, target_audience)
            
            return SkillResult(
                skill_id=self.skill_id,
                output=result,
                success=True,
            )
        except Exception as e:
            logger.error(f"SK-08 execution failed: {e}")
            return SkillResult(
                skill_id=self.skill_id,
                output=None,
                success=False,
                error=str(e),
            )

    def _convert_policy(self, policy_text: str, audience: str) -> Dict[str, Any]:
        """转化政策为科普内容"""
        # 简单解析政策文本（实际可接入 NLP）
        summary = self._generate_summary(policy_text)
        impact_analysis = self._analyze_impact(policy_text)
        action_guide = self._generate_action_guide(policy_text, audience)
        output_plans = self._generate_output_plans(policy_text)
        
        return {
            "summary": summary,
            "impact_analysis": impact_analysis,
            "action_guide": action_guide,
            "output_plans": output_plans,
        }

    def _generate_summary(self, policy_text: str) -> str:
        """生成政策摘要"""
        # 简单提取关键信息
        if "限购" in policy_text:
            return "本次政策主要涉及限购调整，对购房资格和套数进行了明确规定。"
        elif "贷款" in policy_text:
            return "本次政策主要涉及贷款政策调整，对首付比例和利率进行了优化。"
        elif "税收" in policy_text:
            return "本次政策主要涉及税收优惠，对购房税费进行了减免。"
        else:
            return "本次政策涉及房地产相关调整，建议关注具体条款。"

    def _analyze_impact(self, policy_text: str) -> List[str]:
        """分析政策影响"""
        impacts = []
        
        if "限购" in policy_text:
            impacts.extend([
                "购房资格可能收紧，部分人群无法购房",
                "房价可能趋于稳定，投机需求减少",
            ])
        if "贷款" in policy_text:
            impacts.extend([
                "首付比例可能调整，购房门槛变化",
                "贷款利率可能变化，月供压力变化",
            ])
        if "税收" in policy_text:
            impacts.extend([
                "购房成本可能降低，税费减免",
                "二手房交易可能更活跃",
            ])
        
        return impacts if impacts else ["政策影响待进一步分析"]

    def _generate_action_guide(self, policy_text: str, audience: str) -> List[str]:
        """生成行动指南"""
        guides = []
        
        if audience == "buyer":
            guides.extend([
                "确认自身购房资格",
                "了解最新贷款政策",
                "选择合适的购房时机",
            ])
        elif audience == "seller":
            guides.extend([
                "关注政策对房价的影响",
                "评估是否继续持有",
                "了解税费变化",
            ])
        else:
            guides.extend([
                "关注政策官方解读",
                "咨询专业机构",
                "根据自身情况做决策",
            ])
        
        return guides

    def _generate_output_plans(self, policy_text: str) -> List[Dict[str, str]]:
        """生成内容输出计划"""
        return [
            {
                "platform": "xiaohongshu",
                "content_type": "note",
                "title": "政策解读：最新房地产政策来了！",
            },
            {
                "platform": "douyin",
                "content_type": "video",
                "title": "一分钟看懂新政策",
            },
            {
                "platform": "wechat",
                "content_type": "article",
                "title": "深度解读：新政策对您的影响",
            },
        ]
