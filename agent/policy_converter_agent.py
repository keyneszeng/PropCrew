"""
📋 政策科普转化 Agent (Phase 3)

将政策原文转化为通俗易懂的科普内容，支持多平台输出。
"""

import json
import logging
from typing import Any, Dict, List, Optional
from core.agent_base import BaseAgent, AgentResult
from core.model_router import ModelRouter
from skills.policy_converter import PolicyConverter

logger = logging.getLogger(__name__)


class PolicyConverterAgent(BaseAgent):
    """
    政策科普转化 Agent

    职责：
    1. 从知识库检索相关政策原文
    2. 政策原文 → 通俗解读
    3. 分析政策对购房者/业主的影响
    4. 输出多平台科普内容（小红书笔记/视频脚本/朋友圈文案）
    5. 合规检查确保政策引用准确
    """

    def __init__(
        self,
        model_router: ModelRouter,
        policy_converter: Optional[PolicyConverter] = None,
        model: str = "deepseek-v3",
    ):
        super().__init__(
            agent_id="policy_converter",
            name="政策科普顾问",
            description="将政策原文转化为通俗易懂的科普内容",
            system_prompt=self._build_system_prompt(),
            model=model,
        )
        self.model_router = model_router
        self.policy_converter = policy_converter or PolicyConverter(model_router=model_router)

    def _build_system_prompt(self) -> str:
        return """你是房地产销售 Agent 智能体的政策科普顾问。

你的职责：
1. 从政策法规库检索和分析最新房地产政策
2. 用通俗易懂的语⾔解释政策内容
3. 分析政策对不同人群（购房者/业主/投资者）的影响
4. 输出多平台适配的科普内容方案

政策类型：
- purchase_restriction: 限购政策
- loan_policy: 贷款政策（首付/利率/额度）
- tax_policy: 税收政策（契税/增值税/个税）
- hukou_policy: 落户政策
- housing_fund: 公积金政策
- general: 综合政策

科普内容输出方案：
1. 小红书笔记 - 图文解读，适合年轻群体
2. 短视频脚本 - 口播类，一分钟看懂新政
3. 朋友圈文案 - 短平快，简明扼要
4. 私信话术 - 一对一客户解答

合规要求：
- 所有政策引用必须注明出处和生效日期
- 不得曲解或夸大政策原意
- 解读内容需经合规检查
- 提供官方链接/来源

输出格式（JSON）：
{
    "policy_info": {
        "title": "政策标题",
        "source": "发布机构",
        "publish_date": "发布日期",
        "effective_date": "生效日期",
        "category": "政策分类"
    },
    "plain_explanation": "通俗解读（一句话版）",
    "detailed_explanation": "详细解读（300-500字）",
    "impact_analysis": [
        {"group": "购房者", "impact": "影响描述", "severity": "高|中|低"},
        {"group": "业主", "impact": "影响描述", "severity": "高|中|低"},
        {"group": "投资者", "impact": "影响描述", "severity": "高|中|低"}
    ],
    "output_plans": [
        {
            "id": 1,
            "platform": "xiaohongshu | douyin | wechat | private",
            "content_type": "note | script | article | talk",
            "title": "内容标题",
            "key_points": ["要点1", "要点2"],
            "compliance_notes": ["合规提示1"]
        }
    ],
    "action_guide": ["行动建议1", "行动建议2"],
    "references": {"官方链接": "来源地址"}
}

请只输出 JSON，不要其他内容。"""

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """执行政策科普转化任务"""
        try:
            policy_text = input_data.get("policy_text", "")
            policy_title = input_data.get("policy_title", "")
            target_audience = input_data.get("target_audience", "general")
            context = self.get_context()

            if not policy_text:
                # 如果没有提供政策原文，尝试从上下文或提示中生成科普
                logger.warning("policy_text is empty, using context-based generation")

            # Step 1: 用 PolicyConverter Skill 基础转化
            converter_result = await self.policy_converter.execute({
                "policy_text": policy_text,
                "target_audience": target_audience,
            })

            base_output = {}
            if converter_result.success:
                base_output = converter_result.output or {}

            # Step 2: 用 LLM 进行深度解读和多平台输出方案设计
            llm_messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": json.dumps({
                    "policy_title": policy_title,
                    "policy_text": policy_text,
                    "target_audience": target_audience,
                    "base_conversion": base_output,
                }, ensure_ascii=False)},
            ]

            response = await self.model_router.chat(
                messages=llm_messages,
                model_key=self.model,
                temperature=0.7,
            )

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # Fallback 结果
                result = {
                    "policy_info": {
                        "title": policy_title or "房地产政策",
                        "source": "政策发布机构",
                        "publish_date": "近日",
                        "category": "general",
                    },
                    "plain_explanation": "相关政策调整，对购房者和业主都有一定影响。",
                    "detailed_explanation": f"关于{policy_title or '相关政策'}，简要说明如下：{policy_text[:200] if policy_text else '请提供具体政策内容'}",
                    "impact_analysis": [
                        {"group": "购房者", "impact": "建议关注具体条款", "severity": "中"},
                    ],
                    "output_plans": [
                        {
                            "id": 1,
                            "platform": "xiaohongshu",
                            "content_type": "note",
                            "title": f"📢 {policy_title or '新政'}解读来了！",
                            "key_points": ["通俗解读", "影响分析"],
                            "compliance_notes": ["以官方发布为准"],
                        },
                        {
                            "id": 2,
                            "platform": "douyin",
                            "content_type": "script",
                            "title": f"一分钟看懂{policy_title or '新房政'}",
                            "key_points": ["核心变化", "谁受影响"],
                            "compliance_notes": ["信息来源需注明"],
                        },
                    ],
                    "action_guide": ["关注官方发布", "咨询专业机构"],
                    "references": {},
                }

            # 合并 base_output
            if base_output and "summary" in base_output and "plain_explanation" not in result:
                result["plain_explanation"] = base_output["summary"]

            # 更新上下文
            self.update_context({
                "policy_conversion_result": result,
                "policy_info": result.get("policy_info", {}),
            })

            return AgentResult(
                agent_id=self.agent_id,
                content=json.dumps(result, ensure_ascii=False),
                metadata=result,
                success=True,
            )

        except Exception as e:
            logger.error(f"PolicyConverterAgent execution failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                content="",
                success=False,
                error=str(e),
            )
