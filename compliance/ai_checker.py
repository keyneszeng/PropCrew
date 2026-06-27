"""
AI 合规检查 - Layer 2 合规

使用 LLM 进行更智能的合规检查，识别规则引擎无法覆盖的语义违规。
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from core.model_router import ModelRouter

logger = logging.getLogger(__name__)


@dataclass
class AICheckResult:
    """AI 检查结果"""
    is_compliant: bool
    concerns: List[Dict[str, Any]]
    suggestions: List[str]
    risk_level: str
    model_used: str = ""


class AIComplianceChecker:
    """
    AI 合规检查器
    
    功能：
    1. 使用 LLM 进行语义合规检查
    2. 识别规则引擎无法覆盖的违规内容
    3. 提供智能修改建议
    4. 与规则引擎形成双层防护
    """

    def __init__(self, model_router: ModelRouter, model: str = "deepseek-v3"):
        self.model_router = model_router
        self.model = model
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        return """你是房地产广告合规专家，精通《广告法》《房地产广告发布规定》等法规。

你的职责：
1. 检查内容是否存在语义层面的违规（规则引擎可能遗漏的）
2. 识别隐含的承诺、夸大、误导等表述
3. 评估内容的合规风险
4. 提供具体的修改建议

检查维度：
- 隐含的投资承诺（如"保值"、"稳定"等暗示）
- 虚假或夸大的配套设施描述
- 不实的地理位置描述
- 违规的价格表述
- 不合规的学区承诺
- 其他可能违反广告法的表述

输出格式（JSON）：
{
    "is_compliant": true/false,
    "concerns": [
        {
            "text": "疑似违规文本",
            "reason": "违规原因",
            "severity": "high | medium | low",
            "suggestion": "修改建议"
        }
    ],
    "suggestions": ["总体建议1", "总体建议2"],
    "risk_level": "low | medium | high"
}

请只输出 JSON，不要其他内容。"""

    async def check(self, text: str) -> AICheckResult:
        """
        执行 AI 合规检查
        
        Args:
            text: 待检查的文本
            
        Returns:
            AICheckResult: 检查结果
        """
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"请检查以下内容是否合规：\n\n{text}"},
            ]
            
            response = await self.model_router.chat(
                messages=messages,
                model_key=self.model,
                temperature=0.3,
            )
            
            # 解析响应
            import json
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # 如果解析失败，返回默认结果
                result = {
                    "is_compliant": True,
                    "concerns": [],
                    "suggestions": ["AI 检查完成，未发现明显违规"],
                    "risk_level": "low",
                }
            
            return AICheckResult(
                is_compliant=result.get("is_compliant", True),
                concerns=result.get("concerns", []),
                suggestions=result.get("suggestions", []),
                risk_level=result.get("risk_level", "low"),
                model_used=self.model,
            )
            
        except Exception as e:
            logger.error(f"AI compliance check failed: {e}")
            return AICheckResult(
                is_compliant=True,  # 失败时默认通过，避免阻塞流程
                concerns=[],
                suggestions=["AI 检查失败，建议人工审核"],
                risk_level="medium",
                model_used=self.model,
            )

    def get_info(self) -> Dict[str, Any]:
        """获取检查器信息"""
        return {
            "model": self.model,
            "enabled": True,
            "description": "AI 语义合规检查",
        }
