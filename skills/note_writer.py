"""
SK-03: 笔记撰写 Skill

根据卖点分析结果，生成小红书风格笔记。
"""

from typing import Any, Dict, List, Optional
from core.skill_base import BaseSkill, SkillResult
import json
import logging

logger = logging.getLogger(__name__)


class NoteWriter(BaseSkill):
    """SK-03: 笔记撰写 Skill"""

    def __init__(self, model_router=None):
        super().__init__(
            skill_id="SK-03",
            name="笔记撰写",
            description="根据卖点分析结果，生成小红书风格笔记",
            input_schema={
                "selling_points": {"required": True, "type": "list"},
                "community_info": {"required": False, "type": "dict"},
                "note_type": {"required": False, "type": "str"},
            },
            output_schema={
                "title": {"type": "str"},
                "content": {"type": "str"},
                "tags": {"type": "list"},
                "emoji_strategy": {"type": "str"},
            },
        )
        self.model_router = model_router

    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """执行笔记撰写"""
        try:
            selling_points = input_data.get("selling_points", [])
            note_type = input_data.get("note_type", "standard")
            
            note = self._generate_note(selling_points, note_type)
            
            return SkillResult(
                skill_id=self.skill_id,
                output=note,
                success=True,
            )
        except Exception as e:
            logger.error(f"SK-03 execution failed: {e}")
            return SkillResult(
                skill_id=self.skill_id,
                output=None,
                success=False,
                error=str(e),
            )

    def _generate_note(self, selling_points: List[Dict], note_type: str) -> Dict[str, Any]:
        """生成小红书笔记"""
        # 生成标题
        title = self._generate_title(selling_points)
        
        # 生成正文
        content = self._generate_content(selling_points)
        
        # 生成标签
        tags = self._generate_tags(selling_points)
        
        return {
            "title": title,
            "content": content,
            "tags": tags,
            "emoji_strategy": "活泼亲切",
            "word_count": len(content),
        }

    def _generate_title(self, selling_points: List[Dict]) -> str:
        """生成标题"""
        if selling_points:
            first_point = selling_points[0].get("point", "")
            return f"🏠 {first_point} | 这套房子真的绝了！"
        return "🏠 探房日记 | 发现一套好房子"

    def _generate_content(self, selling_points: List[Dict]) -> str:
        """生成正文"""
        lines = [
            "姐妹们！今天发现一套超棒的房子，必须分享给你们～",
            "",
        ]
        
        for i, point in enumerate(selling_points[:3], 1):
            lines.append(f"✨ 亮点{i}：{point.get('point', '')}")
            if point.get("detail"):
                lines.append(f"   {point.get('detail', '')}")
            lines.append("")
        
        lines.extend([
            "整体感觉非常棒，性价比很高！",
            "喜欢的话记得点赞收藏哦～",
            "",
            "你们觉得怎么样？评论区聊聊吧💬",
        ])
        
        return "\n".join(lines)

    def _generate_tags(self, selling_points: List[Dict]) -> List[str]:
        """生成标签"""
        base_tags = ["#房产", "#探房", "#买房"]
        
        for point in selling_points:
            category = point.get("category", "")
            if category == "学区":
                base_tags.append("#学区房")
            elif category == "地铁":
                base_tags.append("#地铁房")
            elif category == "投资":
                base_tags.append("#投资")
        
        return base_tags[:8]
