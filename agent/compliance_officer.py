"""
⚖️ 合规质检 Agent (Phase 3)

双层合规检查架构的编排层。
整合规则引擎（Layer 1）和 AI 语义检查（Layer 2），输出统一合规报告。
"""

import json
import logging
from typing import Any, Dict, List, Optional
from core.agent_base import BaseAgent, AgentResult
from core.model_router import ModelRouter
from compliance.rule_engine import ComplianceRuleEngine
from compliance.ai_checker import AIComplianceChecker

logger = logging.getLogger(__name__)


class ComplianceOfficerAgent(BaseAgent):
    """
    合规质检 Agent

    职责：
    1. 接收任意待检查内容
    2. 调用规则引擎（Layer 1）进行检查
    3. 调用 AI 语义检查（Layer 2）辅助判断
    4. 输出统一的合规报告（通过/警告/拦截 + 修改建议）
    5. 提供 AI 检测规避改写建议
    """

    def __init__(
        self,
        model_router: ModelRouter,
        compliance_engine: Optional[ComplianceRuleEngine] = None,
        ai_checker: Optional[AIComplianceChecker] = None,
        model: str = "deepseek-v3",
    ):
        super().__init__(
            agent_id="compliance_officer",
            name="合规质检员",
            description="双层合规检查：规则引擎 + AI 语义判断",
            system_prompt=self._build_system_prompt(),
            model=model,
        )
        self.model_router = model_router
        self.compliance_engine = compliance_engine or ComplianceRuleEngine()
        self.ai_checker = ai_checker or AIComplianceChecker(model_router=model_router, model=model)

    def _build_system_prompt(self) -> str:
        return """你是房地产广告合规质检员，精通《广告法》《房地产广告发布规定》。

你的职责：
1. 接收待检查内容，了解其发布平台和内容类型
2. 整合规则引擎和 AI 检查的结果
3. 输出最终合规报告（通过/警告/拦截）
4. 提供可落地的修改建议和 AI 检测规避改写

输出格式（JSON）：
{
    "status": "pass | warning | blocked",
    "summary": "总体合规评价",
    "layer1_results": {
        "rule_matches": [
            {"rule": "规则名", "match": "匹配内容", "severity": "high|medium|low", "suggestion": "修改建议"}
        ],
        "total_violations": 数量,
        "risk_level": "low|medium|high"
    },
    "layer2_results": {
        "ai_concerns": [
            {"text": "嫌疑文本", "reason": "违规原因", "severity": "high|medium|low", "suggestion": "修改建议"}
        ],
        "risk_level": "low|medium|high"
    },
    "final_risk_level": "pass | warning | blocked",
    "modification_suggestions": [
        {"original": "原始文本", "suggested": "修改后文本", "reason": "修改原因"}
    ],
    "ai_detection_avoidance": [
        {"technique": "改写技巧", "example": "示例"}
    ],
    "compliance_score": 100
}

合规评分规则：
- 0 violations → 100分（通过）
- 1 high → 30分（拦截）
- 2+ medium → 50分（警告）
- 1 medium → 70分（警告）
- 只 low → 80分（警告）

请只输出 JSON，不要其他内容。"""

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """执行合规检查任务"""
        try:
            text = input_data.get("text", "")
            platform = input_data.get("platform", "xiaohongshu")
            content_type = input_data.get("content_type", "note")
            context = self.get_context()

            if not text:
                # 尝试从上下文中获取
                ctx = self.get_context()
                for key in ["xiaohongshu_note", "video_script", "talk_result", "policy_conversion_result"]:
                    item = ctx.get(key)
                    if not item:
                        sub_ctx = ctx.get("context", {})
                        if sub_ctx:
                            item = sub_ctx.get(key)
                    if item and isinstance(item, dict):
                        text = f"{item.get('title', '')} {item.get('content', '')} {item.get('text', '')}"
                        if text.strip():
                            break

            if not text:
                return AgentResult(
                    agent_id=self.agent_id,
                    content=json.dumps({
                        "status": "error",
                        "summary": "没有提供待检查内容",
                        "layer1_results": {},
                        "layer2_results": {},
                        "final_risk_level": "error",
                        "modification_suggestions": [],
                        "compliance_score": 0,
                    }, ensure_ascii=False),
                    success=False,
                    error="没有提供待检查内容",
                )

            # Step 1: Layer 1 - 规则引擎检查（强制）
            rule_result = self.compliance_engine.check(text)
            logger.info(f"Layer 1 完成: {len(rule_result.violations)} 个违规, 风险等级: {rule_result.risk_level}")

            # Step 2: Layer 2 - AI 语义检查（辅助）
            ai_result = await self.ai_checker.check(text)
            logger.info(f"Layer 2 完成: {len(ai_result.concerns)} 个关注点, 风险等级: {ai_result.risk_level}")

            # Step 3: 整合结果并生成最终合规报告
            final_result = await self._generate_final_report(
                text=text,
                platform=platform,
                content_type=content_type,
                rule_result=rule_result,
                ai_result=ai_result,
            )

            # 更新上下文
            self.update_context({
                "compliance_status": final_result,
                "compliance_report": final_result,
            })

            return AgentResult(
                agent_id=self.agent_id,
                content=json.dumps(final_result, ensure_ascii=False),
                metadata=final_result,
                success=True,
            )

        except Exception as e:
            logger.error(f"ComplianceOfficerAgent execution failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                content=json.dumps({
                    "status": "error",
                    "summary": f"合规检查执行失败: {str(e)}",
                    "layer1_results": {},
                    "layer2_results": {},
                    "final_risk_level": "error",
                    "modification_suggestions": [],
                    "compliance_score": 0,
                }, ensure_ascii=False),
                success=False,
                error=str(e),
            )

    async def _generate_final_report(
        self,
        text: str,
        platform: str,
        content_type: str,
        rule_result: Any,
        ai_result: Any,
    ) -> Dict[str, Any]:
        """生成最终合规报告"""
        # 计算合规评分
        high_count = sum(1 for v in rule_result.violations if v.get("severity") == "high")
        medium_count = sum(1 for v in rule_result.violations if v.get("severity") == "medium")
        low_count = sum(1 for v in rule_result.violations if v.get("severity") == "low")

        # AI 检查的违规数
        ai_high = sum(1 for c in ai_result.concerns if c.get("severity") == "high")
        ai_medium = sum(1 for c in ai_result.concerns if c.get("severity") == "medium")

        # 综合评分
        if high_count > 0 or ai_high > 0:
            compliance_score = max(0, 100 - (high_count * 40 + ai_high * 30 + medium_count * 15 + ai_medium * 10))
            status = "blocked"
        elif medium_count > 0 or ai_medium > 0:
            compliance_score = max(30, 100 - (medium_count * 15 + ai_medium * 10 + low_count * 5))
            status = "warning"
        elif low_count > 0:
            compliance_score = max(70, 100 - low_count * 10)
            status = "warning"
        else:
            if ai_result.concerns and any(c.get("severity") == "medium" for c in ai_result.concerns):
                status = "warning"
                compliance_score = 80
            else:
                status = "pass"
                compliance_score = 100

        # 生成最终风险等级
        if high_count > 0 or (status == "blocked"):
            final_risk = "blocked"
        elif medium_count > 0 or ai_medium > 0:
            final_risk = "warning"
        else:
            final_risk = "pass"

        # 用 LLM 生成修改建议和 AI 检测规避建议
        suggestion_messages = [
            {"role": "system", "content": """你是合规修改专家。提供具体的修改建议和 AI 检测规避技巧。
输出JSON：
{
    "modification_suggestions": [
        {"original": "原始文本", "suggested": "修改后文本", "reason": "修改原因"}
    ],
    "ai_detection_avoidance": [
        {"technique": "技巧名称", "example": "示例"}
    ]
}"""},
            {"role": "user", "content": json.dumps({
                "original_text": text,
                "platform": platform,
                "rule_violations": rule_result.violations,
                "ai_concerns": ai_result.concerns,
            }, ensure_ascii=False)},
        ]

        suggestion_response = await self.model_router.chat(
            messages=suggestion_messages,
            model_key=self.model,
            temperature=0.5,
        )

        try:
            suggestions_data = json.loads(suggestion_response)
        except json.JSONDecodeError:
            suggestions_data = {
                "modification_suggestions": [
                    {"original": v.get("match") or v.get("word", ""), "suggested": v.get("suggestion", ""), "reason": "违规用词替换"}
                    for v in rule_result.violations[:3]
                ] if rule_result.violations else [],
                "ai_detection_avoidance": [
                    {"technique": "句式多样化", "example": "避免重复使用相同句式"},
                    {"technique": "加入个人化表达", "example": "添加'我觉得''我个人认为'等主观表达"},
                ],
            }

        return {
            "status": status,
            "summary": self._generate_summary(status, compliance_score, rule_result, ai_result),
            "layer1_results": {
                "rule_matches": rule_result.violations,
                "total_violations": len(rule_result.violations),
                "risk_level": rule_result.risk_level,
            },
            "layer2_results": {
                "ai_concerns": ai_result.concerns,
                "risk_level": ai_result.risk_level,
            },
            "final_risk_level": final_risk,
            "modification_suggestions": suggestions_data.get("modification_suggestions", []),
            "ai_detection_avoidance": suggestions_data.get("ai_detection_avoidance", []),
            "compliance_score": compliance_score,
        }

    def _generate_summary(self, status: str, score: int, rule_result: Any, ai_result: Any) -> str:
        """生成总结"""
        if status == "pass":
            return f"✅ 合规通过，评分 {score} 分，未发现违规内容，可以发布。"
        elif status == "warning":
            details = []
            if rule_result.violations:
                details.append(f"规则引擎发现 {len(rule_result.violations)} 个问题")
            if ai_result.concerns:
                details.append(f"AI 检查发现 {len(ai_result.concerns)} 个潜在风险")
            return f"⚠️ 合规警告，评分 {score} 分。{'，'.join(details)}，建议修改后再发布。"
        else:
            details = []
            if rule_result.violations:
                details.append(f"{len(rule_result.violations)} 个严重违规")
            if ai_result.concerns:
                details.append(f"{len(ai_result.concerns)} 个高风险嫌疑")
            return f"🔴 合规拦截，评分 {score} 分。{'，'.join(details)}，必须修改后才能发布。"
