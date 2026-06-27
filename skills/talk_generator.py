"""
SK-05: 话术生成 Skill

根据客户问题和场景，生成回复话术。
"""

from typing import Any, Dict, List, Optional
from core.skill_base import BaseSkill, SkillResult
import logging

logger = logging.getLogger(__name__)


class TalkGenerator(BaseSkill):
    """SK-05: 话术生成 Skill"""

    def __init__(self, model_router=None):
        super().__init__(
            skill_id="SK-05",
            name="话术生成",
            description="根据客户问题和场景，生成回复话术",
            input_schema={
                "customer_question": {"required": True, "type": "str"},
                "customer_profile": {"required": False, "type": "dict"},
                "scenario": {"required": False, "type": "str"},
                "template": {"required": False, "type": "str"},
            },
            output_schema={
                "options": {"type": "list"},
            },
        )
        self.model_router = model_router

    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """执行话术生成"""
        try:
            customer_question = input_data.get("customer_question", "")
            customer_profile = input_data.get("customer_profile", {})
            scenario = input_data.get("scenario", "general")
            
            talks = self._generate_talks(customer_question, customer_profile, scenario)
            
            return SkillResult(
                skill_id=self.skill_id,
                output={"options": talks},
                success=True,
            )
        except Exception as e:
            logger.error(f"SK-05 execution failed: {e}")
            return SkillResult(
                skill_id=self.skill_id,
                output=None,
                success=False,
                error=str(e),
            )

    def _generate_talks(self, question: str, profile: Dict, scenario: str) -> List[Dict[str, Any]]:
        """生成话术选项"""
        options = []
        
        # 根据问题类型生成话术
        if "价格" in question or "多少钱" in question:
            options = [
                {
                    "text": "您好！这套房子总价XX万，首付约XX万，月供约XX元。具体价格可以根据您的预算和需求进一步沟通哦～",
                    "reason": "价格咨询标准回复",
                    "suitability": "适合初次咨询",
                },
                {
                    "text": "价格方面我们有多种付款方式可以选择，您可以先了解一下房子的具体情况，我们再详细谈价格。",
                    "reason": "引导深入了解",
                    "suitability": "适合价格敏感客户",
                },
            ]
        elif "学区" in question or "学校" in question:
            options = [
                {
                    "text": "您好！这套房子对口XX学校，是XX区的优质教育资源。具体学区政策建议您咨询当地教育局确认哦～",
                    "reason": "学区咨询标准回复",
                    "suitability": "适合学区需求客户",
                },
            ]
        elif "地铁" in question or "交通" in question:
            options = [
                {
                    "text": "您好！这套房子距离XX地铁站约XX米，步行约XX分钟，交通非常便利。周边还有多条公交线路，出行很方便哦～",
                    "reason": "交通咨询标准回复",
                    "suitability": "适合通勤需求客户",
                },
            ]
        else:
            options = [
                {
                    "text": "您好！感谢您的咨询。关于您提到的问题，我这边可以为您详细介绍。请问您方便留个联系方式吗？我安排专员为您一对一服务～",
                    "reason": "通用引导回复",
                    "suitability": "适合各类咨询",
                },
            ]
        
        return options
