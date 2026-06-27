"""
短视频编导 Agent

负责根据卖点分析结果，创作短视频分镜脚本。
"""

import logging
from typing import Any, Dict, List, Optional
from core.agent_base import BaseAgent, AgentResult
from core.model_router import ModelRouter

logger = logging.getLogger(__name__)


class VideoDirectorAgent(BaseAgent):
    """
    短视频编导 Agent
    
    职责：
    1. 接收卖点分析结果
    2. 创作短视频分镜脚本
    3. 包含口播文案、拍摄建议、BGM 推荐
    4. 符合抖音/视频号等平台调性
    """

    def __init__(
        self,
        model_router: ModelRouter,
        model: str = "deepseek-v3",
    ):
        super().__init__(
            agent_id="video_director",
            name="短视频编导",
            description="创作短视频分镜脚本",
            system_prompt=self._build_system_prompt(),
            model=model,
        )
        self.model_router = model_router

    def _build_system_prompt(self) -> str:
        return """你是房地产销售 Agent 智能体的短视频编导。

你的职责：
1. 根据卖点分析结果，创作短视频脚本
2. 包含分镜、口播文案、拍摄建议
3. 符合抖音/视频号等平台调性
4. 时长控制在 30-60 秒

输出格式（JSON）：
{
    "title": "视频标题",
    "scenes": [
        {
            "scene_number": 1,
            "type": "opening | selling_point | closing",
            "duration": 3,
            "content": "口播文案",
            "camera": "拍摄手法",
            "bgm": "背景音乐建议"
        }
    ],
    "total_duration": 总时长,
    "shooting_tips": ["拍摄建议1", "拍摄建议2"]
}

请只输出 JSON，不要其他内容。"""

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """执行短视频编导任务"""
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

请创作一个短视频脚本。"""},
            ]
            
            # 调用 LLM
            response = await self.model_router.chat(
                messages=messages,
                model_key=self.model,
                temperature=0.7,
            )
            
            # 解析响应
            import json
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                result = {
                    "title": "🏠 探房视频",
                    "scenes": [],
                    "total_duration": 0,
                    "shooting_tips": [],
                }
            
            # 更新上下文
            self.update_context({
                "video_script": result,
                "director_result": result,
            })
            
            return AgentResult(
                agent_id=self.agent_id,
                content=json.dumps(result, ensure_ascii=False),
                metadata=result,
                success=True,
            )
            
        except Exception as e:
            logger.error(f"VideoDirectorAgent execution failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                content="",
                success=False,
                error=str(e),
            )
