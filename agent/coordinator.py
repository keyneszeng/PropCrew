"""
内容总监 Agent

负责接收用户需求，分析任务类型，编排后续 Agent 执行流程。
是用户与系统交互的入口点。
"""

import logging
from typing import Any, Dict, List, Optional
from core.agent_base import BaseAgent, AgentResult
from core.model_router import ModelRouter

logger = logging.getLogger(__name__)


class ContentCoordinatorAgent(BaseAgent):
    """
    内容总监 Agent
    
    职责：
    1. 接收用户需求
    2. 分析任务类型（小红书笔记/短视频脚本/客户话术等）
    3. 编排后续 Agent 执行流程
    4. 汇总结果返回给用户
    """

    def __init__(
        self,
        model_router: ModelRouter,
        model: str = "deepseek-v3",
    ):
        super().__init__(
            agent_id="content_director",
            name="内容总监",
            description="负责接收用户需求，分析任务类型，编排后续 Agent 执行流程",
            system_prompt=self._build_system_prompt(),
            model=model,
        )
        self.model_router = model_router

    def _build_system_prompt(self) -> str:
        return """你是房地产销售 Agent 智能体的内容总监。

你的职责：
1. 接收用户的需求（如"帮我写一条小红书探房笔记"）
2. 分析任务类型和所需信息
3. 决定需要调用哪些 Agent 来完成
4. 编排执行流程
5. 汇总结果

任务类型识别：
- 小红书笔记：需要卖点分析 + 文案创作
- 短视频脚本：需要卖点分析 + 脚本创作
- 客户话术：需要直接生成话术
- 政策科普：需要政策解读 + 科普文案

输出格式（JSON）：
{
    "task_type": "xiaohongshu_note | video_script | customer_talk | policy_explain",
    "required_agents": ["agent_id1", "agent_id2"],
    "execution_order": ["agent_id1", "agent_id2"],
    "input_for_next_agent": {...},
    "notes": "备注说明"
}

请只输出 JSON，不要其他内容。"""

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """执行内容总监任务"""
        try:
            user_request = input_data.get("user_request", "")
            context = self.get_context()
            
            # 构建消息
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"用户需求：{user_request}\n\n当前上下文：{context}"},
            ]
            
            # 调用 LLM
            response = await self.model_router.chat(
                messages=messages,
                model_key=self.model,
                temperature=0.3,  # 低温度，确保输出稳定
            )
            
            # 解析响应
            import json
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # 如果解析失败，返回默认结果
                result = {
                    "task_type": "xiaohongshu_note",
                    "required_agents": ["selling_point_analyst", "xiaohongshu_writer"],
                    "execution_order": ["selling_point_analyst", "xiaohongshu_writer"],
                    "input_for_next_agent": {"property_info": input_data.get("property_info", "")},
                    "notes": "默认流程",
                }
            
            # 更新上下文
            self.update_context({
                "task_type": result.get("task_type"),
                "execution_plan": result.get("execution_order"),
                "coordinator_result": result,
            })
            
            return AgentResult(
                agent_id=self.agent_id,
                content=json.dumps(result, ensure_ascii=False),
                metadata=result,
                success=True,
            )
            
        except Exception as e:
            logger.error(f"ContentCoordinatorAgent execution failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                content="",
                success=False,
                error=str(e),
            )
