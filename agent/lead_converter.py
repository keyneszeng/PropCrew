"""
💬 线索转化 Agent (Phase 3)

将潜在客户线索转化为有效互动。
支持评论回复、私信跟进、电话邀约、异议处理等场景。
"""

import json
import logging
from typing import Any, Dict, List, Optional
from core.agent_base import BaseAgent, AgentResult
from core.model_router import ModelRouter
from skills.talk_generator import TalkGenerator

logger = logging.getLogger(__name__)


class LeadConverterAgent(BaseAgent):
    """
    线索转化 Agent
    
    职责：
    1. 分析客户线索意图和紧急程度
    2. 生成个性化话术（评论回复/私信/电话/异议处理）
    3. 提供多套话术备选方案
    4. 合规检查话术内容
    """

    def __init__(
        self,
        model_router: ModelRouter,
        talk_generator: Optional[TalkGenerator] = None,
        model: str = "deepseek-v3",
    ):
        super().__init__(
            agent_id="lead_converter",
            name="线索转化顾问",
            description="将潜在客户线索转化为有效互动，生成个性化话术",
            system_prompt=self._build_system_prompt(),
            model=model,
        )
        self.model_router = model_router
        self.talk_generator = talk_generator or TalkGenerator(model_router=model_router)

    def _build_system_prompt(self) -> str:
        return """你是房地产销售 Agent 智能体的线索转化顾问。

你的职责：
1. 分析客户线索的来源、意图和紧急程度
2. 根据客户画像和房源匹配度，生成个性化话术
3. 针对不同场景提供多种话术方案

话术场景类型：
- comment_reply: 评论回复（小红书/抖音评论）
- private_message: 私信跟进
- phone_call: 电话邀约
- visit_invitation: 看房邀请
- objection_handling: 异议处理
- closing: 逼定话术

客户意图分析：
- price_inquiry: 价格咨询
- school_district: 学区咨询
- property_viewing: 看房需求
- investment: 投资意向
- comparison: 比价对比
- general: 一般咨询

输出格式（JSON）：
{
    "intent_analysis": {
        "intent_type": "客户意图类型",
        "intensity": "1-5 的紧急程度/兴趣度",
        "key_concerns": ["客户关注点1", "客户关注点2"],
        "persona": "客户画像描述"
    },
    "options": [
        {
            "id": 1,
            "scenario": "响应场景",
            "style": "话术风格（亲切/专业/促单）",
            "text": "话术正文",
            "key_highlights": ["应答亮点1", "应答亮点2"],
            "call_to_action": "期望用户采取的行动"
        }
    ],
    "recommended_option": 1,
    "compliance_notes": ["合规提示"]
}

请只输出 JSON，不要其他内容。"""

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """执行线索转化任务"""
        try:
            customer_question = input_data.get("customer_question", "")
            customer_profile = input_data.get("customer_profile", {})
            scenario = input_data.get("scenario", "general")
            context = self.get_context()

            # Step 1: 用 LLM 分析客户意图
            intent_messages = [
                {"role": "system", "content": """你是客户意图分析专家。分析以下客户问题，输出JSON：
{
    "intent_type": "price_inquiry | school_district | property_viewing | investment | comparison | general",
    "intensity": 1-5,
    "key_concerns": ["关注点"],
    "persona": "客户画像"
}
只输出JSON。"""},
                {"role": "user", "content": f"客户问题：{customer_question}\n客户画像：{json.dumps(customer_profile, ensure_ascii=False)}"},
            ]

            intent_response = await self.model_router.chat(
                messages=intent_messages,
                model_key=self.model,
                temperature=0.3,
            )

            try:
                intent_analysis = json.loads(intent_response)
            except json.JSONDecodeError:
                intent_analysis = {
                    "intent_type": "general",
                    "intensity": 3,
                    "key_concerns": ["未识别"],
                    "persona": "一般客户",
                }

            # Step 2: 用 TalkGenerator Skill 生成话术
            talk_result = await self.talk_generator.execute({
                "customer_question": customer_question,
                "customer_profile": customer_profile,
                "scenario": scenario,
            })

            talk_options = []
            if talk_result.success and talk_result.output:
                talk_options = talk_result.output.get("options", [])

            # Step 3: 用 LLM 增强话术（个性化定制）
            enhancement_messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": json.dumps({
                    "customer_question": customer_question,
                    "customer_profile": customer_profile,
                    "scenario": scenario,
                    "intent_analysis": intent_analysis,
                    "basic_options": talk_options,
                }, ensure_ascii=False)},
            ]

            enhancement_response = await self.model_router.chat(
                messages=enhancement_messages,
                model_key=self.model,
                temperature=0.7,
            )

            try:
                final_result = json.loads(enhancement_response)
            except json.JSONDecodeError:
                final_result = {
                    "intent_analysis": intent_analysis,
                    "options": talk_options if talk_options else [
                        {
                            "id": 1,
                            "scenario": scenario,
                            "style": "亲切",
                            "text": f"您好！感谢您的咨询。关于您提到的「{customer_question[:50]}」，我可以为您详细介绍一下，方便的话可以进一步沟通～",
                            "key_highlights": ["友好开场", "针对性回复"],
                            "call_to_action": "进一步沟通",
                        }
                    ],
                    "recommended_option": 1,
                    "compliance_notes": ["注意不要承诺具体价格", "避免使用绝对化用语"],
                }

            # 合并 intent_analysis（如果 final_result 没有的话）
            if "intent_analysis" not in final_result:
                final_result["intent_analysis"] = intent_analysis

            # 更新上下文
            self.update_context({
                "lead_conversion_result": final_result,
                "intent_analysis": intent_analysis,
            })

            return AgentResult(
                agent_id=self.agent_id,
                content=json.dumps(final_result, ensure_ascii=False),
                metadata=final_result,
                success=True,
            )

        except Exception as e:
            logger.error(f"LeadConverterAgent execution failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                content="",
                success=False,
                error=str(e),
            )
