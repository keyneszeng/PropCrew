"""
SK-02: 脚本生成 Skill

根据卖点分析结果，生成短视频分镜脚本。
"""

from typing import Any, Dict, List, Optional
from core.skill_base import BaseSkill, SkillResult
import json
import logging

logger = logging.getLogger(__name__)


class ScriptGenerator(BaseSkill):
    """SK-02: 脚本生成 Skill"""

    def __init__(self, model_router=None):
        super().__init__(
            skill_id="SK-02",
            name="脚本生成",
            description="根据卖点分析结果，生成短视频分镜脚本",
            input_schema={
                "selling_points": {"required": True, "type": "list"},
                "community_info": {"required": False, "type": "dict"},
                "template": {"required": False, "type": "str"},
            },
            output_schema={
                "scenes": {"type": "list"},
            },
        )
        self.model_router = model_router

    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """执行脚本生成"""
        try:
            selling_points = input_data.get("selling_points", [])
            template = input_data.get("template", "standard")
            
            script = self._generate_script(selling_points, template)
            
            return SkillResult(
                skill_id=self.skill_id,
                output=script,
                success=True,
            )
        except Exception as e:
            logger.error(f"SK-02 execution failed: {e}")
            return SkillResult(
                skill_id=self.skill_id,
                output=None,
                success=False,
                error=str(e),
            )

    def _generate_script(self, selling_points: List[Dict], template: str) -> Dict[str, Any]:
        """生成分镜脚本"""
        scenes = []
        
        # 开场镜头
        scenes.append({
            "scene_number": 1,
            "type": "opening",
            "duration": 3,
            "content": "大家好，今天带大家看一套非常不错的房子！",
            "camera": "自拍",
            "bgm": "轻快",
        })
        
        # 卖点展示镜头
        for i, point in enumerate(selling_points[:3], start=2):
            scenes.append({
                "scene_number": i,
                "type": "selling_point",
                "duration": 5,
                "content": f"这套房子最大的亮点是{point.get('point', '')}，{point.get('detail', '')}",
                "camera": "展示",
                "bgm": "舒缓",
            })
        
        # 结尾镜头
        scenes.append({
            "scene_number": len(scenes) + 1,
            "type": "closing",
            "duration": 3,
            "content": "喜欢的话记得点赞关注，我们下期再见！",
            "camera": "自拍",
            "bgm": "轻快",
        })
        
        return {
            "scenes": scenes,
            "total_duration": sum(s["duration"] for s in scenes),
            "template": template,
        }
