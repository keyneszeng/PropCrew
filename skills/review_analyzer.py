"""
SK-07: 复盘分析 Skill

分析历史发布数据，生成复盘报告。
"""

from typing import Any, Dict, List, Optional
from core.skill_base import BaseSkill, SkillResult
import logging

logger = logging.getLogger(__name__)


class ReviewAnalyzer(BaseSkill):
    """SK-07: 复盘分析 Skill"""

    def __init__(self, model_router=None):
        super().__init__(
            skill_id="SK-07",
            name="复盘分析",
            description="分析历史发布数据，生成复盘报告",
            input_schema={
                "publish_records": {"required": True, "type": "list"},
                "engagement_data": {"required": False, "type": "dict"},
            },
            output_schema={
                "summary": {"type": "str"},
                "metrics": {"type": "dict"},
                "insights": {"type": "list"},
                "recommendations": {"type": "list"},
            },
        )
        self.model_router = model_router

    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """执行复盘分析"""
        try:
            publish_records = input_data.get("publish_records", [])
            engagement_data = input_data.get("engagement_data", {})
            
            report = self._analyze(publish_records, engagement_data)
            
            return SkillResult(
                skill_id=self.skill_id,
                output=report,
                success=True,
            )
        except Exception as e:
            logger.error(f"SK-07 execution failed: {e}")
            return SkillResult(
                skill_id=self.skill_id,
                output=None,
                success=False,
                error=str(e),
            )

    def _analyze(self, records: List, engagement: Dict) -> Dict[str, Any]:
        """生成复盘报告"""
        total_posts = len(records)
        total_views = sum(r.get("views", 0) for r in records)
        total_likes = sum(r.get("likes", 0) for r in records)
        total_comments = sum(r.get("comments", 0) for r in records)
        
        avg_views = total_views / total_posts if total_posts > 0 else 0
        avg_likes = total_likes / total_posts if total_posts > 0 else 0
        
        # 找出表现最好的内容
        best_post = max(records, key=lambda x: x.get("views", 0)) if records else None
        
        return {
            "summary": f"本周共发布 {total_posts} 条内容，总曝光 {total_views}，平均曝光 {avg_views:.0f}",
            "metrics": {
                "total_posts": total_posts,
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "avg_views": avg_views,
                "avg_likes": avg_likes,
                "engagement_rate": (total_likes + total_comments) / total_views if total_views > 0 else 0,
            },
            "insights": [
                f"表现最好的内容：{best_post.get('title', 'N/A')}（曝光 {best_post.get('views', 0)}）" if best_post else "暂无数据",
                "建议增加互动引导，提升评论率",
                "建议优化发布时间，选择用户活跃时段",
            ],
            "recommendations": [
                "继续发布探房类内容，用户反馈较好",
                "增加政策解读类内容，提升专业度",
                "尝试短视频形式，提升传播效果",
            ],
        }
