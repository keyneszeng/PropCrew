"""
板块研究员 Agent

负责研究小区所在板块，分析区域优势和发展潜力。
"""

import logging
from typing import Any, Dict, List, Optional
from core.agent_base import BaseAgent, AgentResult
from core.model_router import ModelRouter

logger = logging.getLogger(__name__)


class DistrictResearcherAgent(BaseAgent):
    """
    板块研究员 Agent
    
    职责：
    1. 研究小区所在板块
    2. 分析区域优势（交通、教育、商业、医疗等）
    3. 评估发展潜力
    4. 输出板块研究报告
    """

    def __init__(
        self,
        model_router: ModelRouter,
        model: str = "deepseek-v3",
    ):
        super().__init__(
            agent_id="district_researcher",
            name="板块研究员",
            description="研究小区所在板块，分析区域优势",
            system_prompt=self._build_system_prompt(),
            model=model,
        )
        self.model_router = model_router

    def _build_system_prompt(self) -> str:
        return """你是房地产销售 Agent 智能体的板块研究员。

你的职责：
1. 研究小区所在板块
2. 分析区域优势（交通、教育、商业、医疗等）
3. 评估发展潜力
4. 输出板块研究报告

输出格式（JSON）：
{
    "district_name": "板块名称",
    "summary": "板块概述",
    "advantages": [
        {
            "category": "交通 | 教育 | 商业 | 医疗 | 环境",
            "description": "优势描述"
        }
    ],
    "transportation": ["地铁线路", "公交线路"],
    "education": ["学校名称"],
    "commercial": ["商场名称"],
    "medical": ["医院名称"],
    "development_potential": "发展潜力评估",
    "risk_points": ["风险点"]
}

请只输出 JSON，不要其他内容。"""

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """执行板块研究任务"""
        try:
            district_name = input_data.get("district_name", "")
            community_name = input_data.get("community_name", "")
            context = self.get_context()
            
            # 构建消息
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"""板块名称：{district_name}
小区名称：{community_name}

请研究这个板块，输出研究报告。"""},
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
                    "district_name": district_name,
                    "summary": "板块研究待完善",
                    "advantages": [],
                    "transportation": [],
                    "education": [],
                    "commercial": [],
                    "medical": [],
                    "development_potential": "待评估",
                    "risk_points": [],
                }
            
            # 更新上下文
            self.update_context({
                "district_report": result,
                "researcher_result": result,
            })
            
            return AgentResult(
                agent_id=self.agent_id,
                content=json.dumps(result, ensure_ascii=False),
                metadata=result,
                success=True,
            )
            
        except Exception as e:
            logger.error(f"DistrictResearcherAgent execution failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                content="",
                success=False,
                error=str(e),
            )
