"""
素材模板库

管理可复用的内容模板，包括标题模板、故事模板、脚本模板等。
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from database.models import DatabaseManager, Template
import json

logger = logging.getLogger(__name__)


@dataclass
class TemplateItem:
    """模板项"""
    id: str
    template_type: str
    platform: str
    content_type: str
    template_text: str
    variables: List[str]
    success_score: float
    tags: List[str]
    created_at: str


class TemplateDB:
    """
    素材模板库
    
    功能：
    1. 模板存储和检索
    2. 按类型/平台/内容类型筛选
    3. 变量替换
    4. 成功率统计
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._templates: Dict[str, TemplateItem] = {}

    def init_default_templates(self):
        """初始化默认模板"""
        session = self.db_manager.get_session()
        try:
            default_templates = [
                # 标题模板
                {
                    "template_type": "title",
                    "platform": "xiaohongshu",
                    "content_type": "note",
                    "template_text": "🏠 {property_name} | {price}成交，{reason}",
                    "variables": ["property_name", "price", "reason"],
                    "success_score": 0.8,
                    "tags": ["成交案例", "标题"],
                },
                {
                    "template_type": "title",
                    "platform": "xiaohongshu",
                    "content_type": "note",
                    "template_text": "✨ {area}平米 {rooms} | {highlights}，{target_audience}必看！",
                    "variables": ["area", "rooms", "highlights", "target_audience"],
                    "success_score": 0.75,
                    "tags": ["探房", "标题"],
                },
                {
                    "template_type": "title",
                    "platform": "douyin",
                    "content_type": "video",
                    "template_text": "【探房】{property_name}，{price}能买到这样的房子？",
                    "variables": ["property_name", "price"],
                    "success_score": 0.85,
                    "tags": ["探房", "标题"],
                },
                # 故事模板
                {
                    "template_type": "story",
                    "platform": "xiaohongshu",
                    "content_type": "note",
                    "template_text": """客户背景：{customer_profile}

成交过程：{process}

成交亮点：{highlights}

经验总结：{insights}""",
                    "variables": ["customer_profile", "process", "highlights", "insights"],
                    "success_score": 0.7,
                    "tags": ["成交案例", "故事"],
                },
                # 脚本模板
                {
                    "template_type": "script",
                    "platform": "douyin",
                    "content_type": "video",
                    "template_text": """开场：{opening}

过程：{process}

结果：{result}

结尾：{closing}""",
                    "variables": ["opening", "process", "result", "closing"],
                    "success_score": 0.75,
                    "tags": ["短视频", "脚本"],
                },
                # 话术模板
                {
                    "template_type": "talk_script",
                    "platform": "wechat",
                    "content_type": "talk",
                    "template_text": """开场白：{opening}

需求挖掘：{needs}

方案推荐：{proposal}

异议处理：{objection}

促成成交：{closing}""",
                    "variables": ["opening", "needs", "proposal", "objection", "closing"],
                    "success_score": 0.8,
                    "tags": ["话术", "销售"],
                },
            ]
            
            for template_data in default_templates:
                existing = session.query(Template).filter_by(
                    template_text=template_data["template_text"]
                ).first()
                
                if not existing:
                    template = Template(
                        template_type=template_data["template_type"],
                        platform=template_data["platform"],
                        content_type=template_data["content_type"],
                        template_text=template_data["template_text"],
                        variables=template_data["variables"],
                        success_score=template_data["success_score"],
                        tags=template_data["tags"],
                    )
                    session.add(template)
            
            session.commit()
            logger.info(f"[TemplateDB] Initialized {len(default_templates)} default templates")
            
        except Exception as e:
            session.rollback()
            logger.error(f"[TemplateDB] Failed to init templates: {e}")
        finally:
            session.close()

    def get_templates(
        self,
        template_type: Optional[str] = None,
        platform: Optional[str] = None,
        content_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[TemplateItem]:
        """获取模板列表"""
        session = self.db_manager.get_session()
        try:
            query = session.query(Template)
            
            if template_type:
                query = query.filter_by(template_type=template_type)
            if platform:
                query = query.filter_by(platform=platform)
            if content_type:
                query = query.filter_by(content_type=content_type)
            if tags:
                for tag in tags:
                    query = query.filter(Template.tags.contains(json.dumps([tag])))
            
            templates = query.order_by(Template.success_score.desc()).limit(limit).all()
            
            return [
                TemplateItem(
                    id=t.id,
                    template_type=t.template_type,
                    platform=t.platform,
                    content_type=t.content_type,
                    template_text=t.template_text,
                    variables=t.variables or [],
                    success_score=t.success_score or 0,
                    tags=t.tags or [],
                    created_at=t.created_at.isoformat() if t.created_at else "",
                )
                for t in templates
            ]
            
        finally:
            session.close()

    def get_template(self, template_id: str) -> Optional[TemplateItem]:
        """获取单个模板"""
        session = self.db_manager.get_session()
        try:
            template = session.query(Template).filter_by(id=template_id).first()
            
            if not template:
                return None
            
            return TemplateItem(
                id=template.id,
                template_type=template.template_type,
                platform=template.platform,
                content_type=template.content_type,
                template_text=template.template_text,
                variables=template.variables or [],
                success_score=template.success_score or 0,
                tags=template.tags or [],
                created_at=template.created_at.isoformat() if template.created_at else "",
            )
            
        finally:
            session.close()

    def add_template(self, template_data: Dict[str, Any]) -> str:
        """添加模板"""
        session = self.db_manager.get_session()
        try:
            template = Template(
                template_type=template_data.get("template_type"),
                platform=template_data.get("platform"),
                content_type=template_data.get("content_type"),
                template_text=template_data.get("template_text"),
                variables=template_data.get("variables", []),
                success_score=template_data.get("success_score", 0),
                tags=template_data.get("tags", []),
            )
            session.add(template)
            session.commit()
            return template.id
            
        finally:
            session.close()

    def update_success_score(self, template_id: str, score: float) -> bool:
        """更新成功率"""
        session = self.db_manager.get_session()
        try:
            template = session.query(Template).filter_by(id=template_id).first()
            if template:
                template.success_score = score
                session.commit()
                return True
            return False
            
        finally:
            session.close()

    def render_template(self, template_id: str, variables: Dict[str, str]) -> str:
        """渲染模板（变量替换）"""
        template = self.get_template(template_id)
        if not template:
            return ""
        
        result = template.template_text
        for var, value in variables.items():
            result = result.replace(f"{{{var}}}", value)
        
        return result

    def get_stats(self) -> Dict[str, Any]:
        """获取模板统计"""
        session = self.db_manager.get_session()
        try:
            total = session.query(Template).count()
            by_type = {}
            for t in session.query(Template.template_type).distinct():
                count = session.query(Template).filter_by(template_type=t.template_type).count()
                by_type[t.template_type] = count
            
            by_platform = {}
            for p in session.query(Template.platform).distinct():
                count = session.query(Template).filter_by(platform=p.platform).count()
                by_platform[p.platform] = count
            
            return {
                "total": total,
                "by_type": by_type,
                "by_platform": by_platform,
            }
            
        finally:
            session.close()
