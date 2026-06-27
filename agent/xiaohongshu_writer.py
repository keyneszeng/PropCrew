"""
小红书文案 Agent

负责根据卖点分析结果，创作符合小红书风格的内容。
"""

import logging
from typing import Any, Dict, List, Optional
from core.agent_base import BaseAgent, AgentResult
from core.model_router import ModelRouter

logger = logging.getLogger(__name__)


class XiaohongshuWriterAgent(BaseAgent):
    """
    小红书文案 Agent
    
    职责：
    1. 接收卖点分析结果
    2. 创作小红书风格笔记
    3. 包含标题、正文、标签
    4. 符合平台调性和用户喜好
    """

    def __init__(
        self,
        model_router: ModelRouter,
        model: str = "deepseek-v3",
    ):
        super().__init__(
            agent_id="xiaohongshu_writer",
            name="小红书文案",
            description="创作小红书风格笔记",
            system_prompt=self._build_system_prompt(),
            model=model,
        )
        self.model_router = model_router

    def _build_system_prompt(self) -> str:
        return """你是房地产销售 Agent 智能体的小红书文案专家。

你的职责：
1. 根据卖点分析结果创作小红书笔记
2. 标题吸引人，带 emoji
3. 内容活泼自然，适合小红书年轻用户
4. 结构清晰：开头吸引 + 内容展开 + 结尾互动
5. 字数控制在 300-500 字
6. 结尾附带 5-8 个相关话题标签

小红书风格要点：
- 语气口语化，像朋友聊天
- 多用 emoji 增加亲和力
- 突出痛点，引发共鸣
- 真实感，避免过度营销
- 互动引导（"你们觉得呢？"）

输出格式（JSON）：
{
    "title": "标题（带emoji）",
    "content": "正文内容",
    "tags": ["标签1", "标签2", "标签3"],
    "word_count": 字数,
    "style_notes": "风格说明"
}

请只输出 JSON，不要其他内容。"""

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """执行小红书文案创作任务"""
        try:
            selling_points = input_data.get("selling_points", [])
            property_info = input_data.get("property_info", "")
            context = self.get_context()
            
            # 构建卖点描述
            points_text = "\n".join([
                f"- {p.get('category')}: {p.get('point')}"
                for p in selling_points
            ]) if selling_points else property_info
            
            # 构建消息
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"""房源信息：{property_info}
                
核心卖点：
{points_text}

请创作一篇小红书探房笔记。"""},
            ]
            
            # 调用 LLM
            response = await self.model_router.chat(
                messages=messages,
                model_key=self.model,
                temperature=0.8,  # 高温度，增加创意
            )
            
            # 解析响应
            import json
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                result = {
                    "title": "🏠 探房日记",
                    "content": response,
                    "tags": ["#房产", "#探房", "#买房"],
                    "word_count": len(response),
                    "style_notes": "默认格式",
                }
            
            # 更新上下文
            self.update_context({
                "xiaohongshu_note": result,
                "writer_result": result,
            })
            
            return AgentResult(
                agent_id=self.agent_id,
                content=json.dumps(result, ensure_ascii=False),
                metadata=result,
                success=True,
            )
            
        except Exception as e:
            logger.error(f"XiaohongshuWriterAgent execution failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                content="",
                success=False,
                error=str(e),
            )
