"""
SK-09: 成交案例素材化 Skill

将成交案例转化为可复用的内容模板。
"""

from typing import Any, Dict, List, Optional
from core.skill_base import BaseSkill, SkillResult
import logging

logger = logging.getLogger(__name__)


class CaseToTemplate(BaseSkill):
    """SK-09: 成交案例素材化 Skill"""

    def __init__(self, model_router=None):
        super().__init__(
            skill_id="SK-09",
            name="成交案例素材化",
            description="将成交案例转化为可复用的内容模板",
            input_schema={
                "case_data": {"required": True, "type": "dict"},
            },
            output_schema={
                "reusable_formats": {"type": "list"},
            },
        )
        self.model_router = model_router

    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """执行案例素材化"""
        try:
            case_data = input_data.get("case_data", {})
            
            if not case_data:
                return SkillResult(
                    skill_id=self.skill_id,
                    output=None,
                    success=False,
                    error="案例数据不能为空",
                )
            
            templates = self._extract_templates(case_data)
            
            return SkillResult(
                skill_id=self.skill_id,
                output={"reusable_formats": templates},
                success=True,
            )
        except Exception as e:
            logger.error(f"SK-09 execution failed: {e}")
            return SkillResult(
                skill_id=self.skill_id,
                output=None,
                success=False,
                error=str(e),
            )

    def _extract_templates(self, case_data: Dict) -> List[Dict[str, Any]]:
        """提取可复用模板"""
        templates = []
        
        # 标题模板
        title_template = {
            "type": "title_template",
            "template": "【成交案例】{property_name} | {price}成交，{reason}",
            "variables": ["property_name", "price", "reason"],
            "example": "【成交案例】XX小区 | 800万成交，业主急售",
        }
        templates.append(title_template)
        
        # 故事模板
        story_template = {
            "type": "story_template",
            "template": "客户背景：{customer_profile}\n\n成交过程：{process}\n\n成交亮点：{highlights}\n\n经验总结：{insights}",
            "variables": ["customer_profile", "process", "highlights", "insights"],
            "example": "客户背景：首次购房，预算800万\n\n成交过程：带看5次，最终选定\n\n成交亮点：价格合适，户型满意\n\n经验总结：耐心沟通是关键",
        }
        templates.append(story_template)
        
        # 脚本模板
        script_template = {
            "type": "script_template",
            "template": "开场：{opening}\n\n过程：{process}\n\n结果：{result}\n\n结尾：{closing}",
            "variables": ["opening", "process", "result", "closing"],
            "example": "开场：今天分享一个成交案例\n\n过程：客户从看房到成交的过程\n\n结果：成功签约\n\n结尾：感谢信任",
        }
        templates.append(script_template)
        
        # 话术模板
        talk_template = {
            "type": "talk_template",
            "template": "开场白：{opening}\n\n需求挖掘：{needs}\n\n方案推荐：{proposal}\n\n异议处理：{objection}\n\n促成成交：{closing}",
            "variables": ["opening", "needs", "proposal", "objection", "closing"],
            "example": "开场白：您好，我是XX\n\n需求挖掘：了解购房需求\n\n方案推荐：推荐合适房源\n\n异议处理：解答疑虑\n\n促成成交：签约",
        }
        templates.append(talk_template)
        
        return templates
