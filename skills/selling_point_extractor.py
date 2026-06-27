"""
SK-01: 卖点提炼 Skill

从房源资料中提取核心卖点，输出结构化 JSON。
"""

from typing import Any, Dict, List, Optional
from core.skill_base import BaseSkill, SkillResult
import json
import logging

logger = logging.getLogger(__name__)


class SellingPointExtractor(BaseSkill):
    """SK-01: 卖点提炼 Skill"""

    def __init__(self, model_router=None):
        super().__init__(
            skill_id="SK-01",
            name="卖点提炼",
            description="从房源资料中提取核心卖点",
            input_schema={
                "property_info": {"required": True, "type": "str"},
                "community_info": {"required": False, "type": "dict"},
            },
            output_schema={
                "location": {"type": "str"},
                "transportation": {"type": "list"},
                "education": {"type": "list"},
                "layout": {"type": "dict"},
                "price_value": {"type": "dict"},
                "target_audience": {"type": "str"},
                "risk_points": {"type": "list"},
                "compliance_flags": {"type": "list"},
            },
        )
        self.model_router = model_router

    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """执行卖点提炼"""
        try:
            property_info = input_data.get("property_info", "")
            community_info = input_data.get("community_info", {})
            
            # 解析房源信息（简单解析，实际可接入 NLP）
            selling_points = self._extract_selling_points(property_info)
            
            return SkillResult(
                skill_id=self.skill_id,
                output=selling_points,
                success=True,
            )
        except Exception as e:
            logger.error(f"SK-01 execution failed: {e}")
            return SkillResult(
                skill_id=self.skill_id,
                output=None,
                success=False,
                error=str(e),
            )

    def _extract_selling_points(self, property_info: str) -> Dict[str, Any]:
        """提取卖点（简单规则解析）"""
        import re
        
        # 解析地址
        address_match = re.search(r"地址[：:]\s*(.+?)(?:\n|$)", property_info)
        address = address_match.group(1) if address_match else "未知"
        
        # 解析户型
        rooms_match = re.search(r"户型[：:]\s*(.+?)(?:\n|$)", property_info)
        rooms = rooms_match.group(1) if rooms_match else "未知"
        
        # 解析面积
        area_match = re.search(r"面积[：:]\s*(.+?)(?:\n|$)", property_info)
        area = area_match.group(1) if area_match else "未知"
        
        # 解析价格
        price_match = re.search(r"价格[：:]\s*(.+?)(?:\n|$)", property_info)
        price = price_match.group(1) if price_match else "未知"
        
        # 解析特色
        features_match = re.search(r"特色[：:]\s*(.+?)(?:\n|$)", property_info)
        features = features_match.group(1) if features_match else "无"
        
        # 判断目标客群
        target_audience = self._identify_target_audience(rooms, area, price, features)
        
        # 判断风险点
        risk_points = self._identify_risk_points(features)
        
        return {
            "location": address,
            "transportation": ["地铁"] if "地铁" in features else [],
            "education": ["学区房"] if "学区" in features else [],
            "layout": {
                "rooms": rooms,
                "area": area,
                "decoration": "精装修" if "精装" in features else "简装",
            },
            "price_value": {
                "price": price,
                "value_proposition": "性价比高" if "性价比" in features else "待评估",
            },
            "target_audience": target_audience,
            "risk_points": risk_points,
            "compliance_flags": [],
        }

    def _identify_target_audience(self, rooms: str, area: str, price: str, features: str) -> str:
        """识别目标客群"""
        if "刚需" in features or "首套" in features:
            return "刚需首套"
        elif "改善" in features or "换房" in features:
            return "改善换房"
        elif "投资" in features:
            return "投资置业"
        elif "学区" in features:
            return "学区房需求"
        elif "2室" in rooms or "80平米" in area:
            return "刚需首套"
        elif "3室" in rooms or "120平米" in area:
            return "改善换房"
        else:
            return "待分析"

    def _identify_risk_points(self, features: str) -> List[str]:
        """识别风险点"""
        risks = []
        if "学区" in features:
            risks.append("学区政策可能变化")
        if "地铁" in features:
            risks.append("地铁建设进度可能延迟")
        if "投资" in features:
            risks.append("投资回报不确定")
        return risks
