"""
卖点分析师 Agent

负责分析房源信息，提取核心卖点，为后续内容创作提供素材。
"""

import logging
from typing import Any, Dict, List, Optional
from core.agent_base import BaseAgent, AgentResult
from core.model_router import ModelRouter

logger = logging.getLogger(__name__)


class PropertyAnalystAgent(BaseAgent):
    """
    卖点分析师 Agent
    
    职责：
    1. 分析房源基本信息
    2. 提取核心卖点（户型、地段、配套、价格等）
    3. 分析目标客群
    4. 输出结构化卖点数据
    """

    def __init__(
        self,
        model_router: ModelRouter,
        model: str = "deepseek-v3",
    ):
        super().__init__(
            agent_id="selling_point_analyst",
            name="卖点分析师",
            description="分析房源信息，提取核心卖点",
            system_prompt=self._build_system_prompt(),
            model=model,
        )
        self.model_router = model_router

    def _build_system_prompt(self) -> str:
        return """你是房地产销售 Agent 智能体的卖点分析师。

你的职责：
1. 分析房源基本信息（户型、面积、楼层、朝向等）
2. 提取核心卖点（地段优势、配套资源、价格优势等）
3. 分析目标客群（刚需、改善、投资等）
4. 输出结构化的卖点数据

输出格式（JSON）：
{
    "property_summary": "房源简要描述",
    "selling_points": [
        {
            "category": "户型 | 地段 | 配套 | 价格 | 其他",
            "point": "卖点描述",
            "detail": "详细说明"
        }
    ],
    "target_audience": "目标客群描述",
    "key_highlights": ["亮点1", "亮点2", "亮点3"],
    "suggested_angles": ["角度1", "角度2"]
}

请只输出 JSON，不要其他内容。"""

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """执行卖点分析任务"""
        try:
            property_info = input_data.get("property_info", "")
            context = self.get_context()
            
            # 构建消息
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"房源信息：{property_info}\n\n当前上下文：{context}"},
            ]
            
            # 调用 LLM
            response = await self.model_router.chat(
                messages=messages,
                model_key=self.model,
                temperature=0.5,
            )
            
            # 解析响应
            import json
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                result = {
                    "property_summary": property_info,
                    "selling_points": [],
                    "target_audience": "未分析",
                    "key_highlights": [],
                    "suggested_angles": [],
                }
            
            # 更新上下文
            self.update_context({
                "selling_points": result.get("selling_points", []),
                "target_audience": result.get("target_audience"),
                "analyst_result": result,
            })
            
            return AgentResult(
                agent_id=self.agent_id,
                content=json.dumps(result, ensure_ascii=False),
                metadata=result,
                success=True,
            )
            
        except Exception as e:
            logger.error(f"PropertyAnalystAgent execution failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                content="",
                success=False,
                error=str(e),
            )
