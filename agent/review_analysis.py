"""
📊 复盘分析 Agent (Phase 3)

分析历史发布数据、用户反馈，生成复盘报告和下周选题建议。
"""

import json
import logging
from typing import Any, Dict, List, Optional
from core.agent_base import BaseAgent, AgentResult
from core.model_router import ModelRouter
from skills.review_analyzer import ReviewAnalyzer

logger = logging.getLogger(__name__)


class ReviewAnalysisAgent(BaseAgent):
    """
    复盘分析 Agent
    
    职责：
    1. 分析历史发布数据（曝光、互动、转化）
    2. 识别表现最佳和表现最差的内容类型
    3. 生成深度复盘报告
    4. 推荐下周选题和优化方向
    """

    def __init__(
        self,
        model_router: ModelRouter,
        review_analyzer: Optional[ReviewAnalyzer] = None,
        model: str = "deepseek-v3",
    ):
        super().__init__(
            agent_id="review_analyst",
            name="复盘分析师",
            description="分析历史发布数据，生成复盘报告和选题建议",
            system_prompt=self._build_system_prompt(),
            model=model,
        )
        self.model_router = model_router
        self.review_analyzer = review_analyzer or ReviewAnalyzer(model_router=model_router)

    def _build_system_prompt(self) -> str:
        return """你是房地产销售 Agent 智能体的复盘分析师。

你的职责：
1. 分析历史发布数据（各平台的曝光、点赞、评论、转化数据）
2. 发现数据趋势和规律
3. 识别表现最佳的内容类型和风格
4. 生成深度、可落地的复盘报告和下周选题建议

分析维度：
- 内容维度：哪种类型内容表现好（探房/科普/故事/话术）
- 平台维度：哪个平台效果最好（小红书/抖音/朋友圈）
- 时间维度：哪个时间段发布效果最好
- 话题维度：什么话题最受欢迎
- 用户反馈：经纪人评分和采纳率

输出格式（JSON）：
{
    "summary": "整体复盘概要（一段话）",
    "metrics": {
        "total_posts": 总发布数,
        "total_views": 总曝光,
        "total_interactions": 总互动(点赞+评论+转发),
        "avg_views_per_post": 平均曝光/条,
        "avg_interaction_rate": 平均互动率,
        "best_platform": "效果最好平台",
        "best_content_type": "效果最好内容类型"
    },
    "trends": [
        {"dimension": "趋势维度", "finding": "发现", "evidence": "数据证据"}
    ],
    "insights": [
        {"type": "success | improvement | risk", "content": "洞察内容", "impact": "影响评估"}
    ],
    "content_analysis": {
        "best_performers": [{"title": "标题", "views": 曝光, "reason": "成功原因"}],
        "improvement_areas": [{"title": "标题", "issue": "问题", "suggestion": "改进建议"}]
    },
    "recommendations": [
        {"priority": "高|中|低", "action": "行动建议", "expected_impact": "预期效果"}
    ],
    "weekly_plan": {
        "monday": {"theme": "主题", "platform": "平台", "content_type": "类型"},
        "tuesday": {"theme": "主题", "platform": "平台", "content_type": "类型"},
        "wednesday": {"theme": "主题", "platform": "平台", "content_type": "类型"},
        "thursday": {"theme": "主题", "platform": "平台", "content_type": "类型"},
        "friday": {"theme": "主题", "platform": "平台", "content_type": "类型"},
        "saturday": {"theme": "主题", "platform": "平台", "content_type": "类型"},
        "sunday": {"theme": "主题", "platform": "平台", "content_type": "类型"}
    }
}

请只输出 JSON，不要其他内容。"""

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """执行复盘分析任务"""
        try:
            publish_records = input_data.get("publish_records", [])
            engagement_data = input_data.get("engagement_data", {})
            user_feedback = input_data.get("user_feedback", [])
            context = self.get_context()

            # Step 1: 基础指标计算（用 ReviewAnalyzer Skill）
            analyzer_result = await self.review_analyzer.execute({
                "publish_records": publish_records,
                "engagement_data": engagement_data,
            })

            basic_report = {}
            if analyzer_result.success:
                basic_report = analyzer_result.output or {}

            # Step 2: 用 LLM 进行深度分析和周期建议
            analysis_messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": json.dumps({
                    "publish_records": publish_records,
                    "engagement_data": engagement_data,
                    "user_feedback": user_feedback,
                    "basic_report": basic_report,
                }, ensure_ascii=False)},
            ]

            response = await self.model_router.chat(
                messages=analysis_messages,
                model_key=self.model,
                temperature=0.7,
            )

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                result = {
                    "summary": "数据分析完成，生成基础报告",
                    "metrics": {
                        "total_posts": len(publish_records),
                        "total_views": sum(r.get("views", 0) for r in publish_records),
                        "total_interactions": sum(r.get("likes", 0) + r.get("comments", 0) for r in publish_records),
                        "avg_views_per_post": sum(r.get("views", 0) for r in publish_records) / max(len(publish_records), 1),
                        "avg_interaction_rate": 0,
                        "best_platform": "未知",
                        "best_content_type": "未知",
                    },
                    "trends": [],
                    "insights": [{"type": "success", "content": "基础分析完成", "impact": "低"}],
                    "content_analysis": {"best_performers": [], "improvement_areas": []},
                    "recommendations": [{"priority": "中", "action": "继续发布优质内容", "expected_impact": "稳定增长"}],
                    "weekly_plan": {},
                }

            # 合并 basic_report 的 metrics（如果 LLM 结果缺少数据）
            if basic_report and "metrics" not in result:
                result["metrics"] = basic_report.get("metrics", result.get("metrics", {}))

            # 更新上下文
            self.update_context({
                "review_report": result,
                "review_analysis_result": result,
            })

            return AgentResult(
                agent_id=self.agent_id,
                content=json.dumps(result, ensure_ascii=False),
                metadata=result,
                success=True,
            )

        except Exception as e:
            logger.error(f"ReviewAnalysisAgent execution failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                content="",
                success=False,
                error=str(e),
            )
