"""
数据库模型

基于 PRD 第 8 章的数据模型定义。
Phase 1 使用 SQLite，生产环境可切换到 PostgreSQL。
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime, JSON, Boolean,
    create_engine, ForeignKey, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


def generate_uuid() -> str:
    """生成 UUID（SQLite 兼容）"""
    return str(uuid.uuid4())


def get_current_time() -> datetime:
    """获取当前时间"""
    return datetime.now()


class Property(Base):
    """房源表"""
    __tablename__ = "property"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    address = Column(Text)
    district = Column(String(50))
    price = Column(Float)
    area = Column(Float)
    rooms = Column(String(20))
    floor = Column(String(20))
    total_floors = Column(Integer)
    decoration = Column(String(50))
    property_type = Column(String(20))  # new, resale, rent
    tags = Column(JSON, default=list)
    images = Column(JSON, default=list)
    selling_points = Column(JSON)
    compliance_flags = Column(JSON, default=list)
    created_at = Column(DateTime, default=get_current_time)
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "address": self.address,
            "district": self.district,
            "price": self.price,
            "area": self.area,
            "rooms": self.rooms,
            "floor": self.floor,
            "total_floors": self.total_floors,
            "decoration": self.decoration,
            "property_type": self.property_type,
            "tags": self.tags,
            "images": self.images,
            "selling_points": self.selling_points,
            "compliance_flags": self.compliance_flags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Community(Base):
    """小区表"""
    __tablename__ = "community"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    address = Column(Text)
    district = Column(String(50))
    avg_price = Column(Float)
    build_year = Column(Integer)
    schools = Column(JSON, default=list)
    transportation = Column(JSON, default=list)
    commercial = Column(JSON, default=list)
    competition = Column(JSON, default=list)
    price_trend = Column(JSON)
    poi_data = Column(JSON)
    last_updated = Column(DateTime, default=get_current_time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "district": self.district,
            "avg_price": self.avg_price,
            "build_year": self.build_year,
            "schools": self.schools,
            "transportation": self.transportation,
            "commercial": self.commercial,
            "competition": self.competition,
            "price_trend": self.price_trend,
            "poi_data": self.poi_data,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


class Policy(Base):
    """政策法规表"""
    __tablename__ = "policy"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(500), nullable=False)
    source = Column(String(100))  # 住建部/央行/地方房管局
    publish_date = Column(DateTime)
    effective_date = Column(DateTime)
    content = Column(Text)
    summary = Column(Text)
    version = Column(Integer, default=1)
    change_log = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=get_current_time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "publish_date": self.publish_date.isoformat() if self.publish_date else None,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "content": self.content,
            "summary": self.summary,
            "version": self.version,
            "change_log": self.change_log,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Post(Base):
    """发布记录表"""
    __tablename__ = "post"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    property_id = Column(String(36), ForeignKey("property.id"))
    agent_id = Column(String(100))
    platform = Column(String(20))  # douyin, xiaohongshu, wechat, weibo
    content_type = Column(String(20))  # script, note, talk_script, popular_science
    content = Column(JSON, nullable=False)
    status = Column(String(20), default="draft")  # draft, pending_review, approved, rejected, published
    compliance_report = Column(JSON)
    publish_time = Column(DateTime)
    engagement_metrics = Column(JSON, default=dict)
    user_feedback = Column(Integer)  # 1-5
    created_at = Column(DateTime, default=get_current_time)

    property = relationship("Property")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "property_id": self.property_id,
            "agent_id": self.agent_id,
            "platform": self.platform,
            "content_type": self.content_type,
            "content": self.content,
            "status": self.status,
            "compliance_report": self.compliance_report,
            "publish_time": self.publish_time.isoformat() if self.publish_time else None,
            "engagement_metrics": self.engagement_metrics,
            "user_feedback": self.user_feedback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Template(Base):
    """素材模板表"""
    __tablename__ = "template"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    template_type = Column(String(50))  # title, cover, talk_script, story, opening
    platform = Column(String(20))
    content_type = Column(String(20))
    template_text = Column(Text, nullable=False)
    variables = Column(JSON, default=list)
    success_score = Column(Float, default=0)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=get_current_time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "template_type": self.template_type,
            "platform": self.platform,
            "content_type": self.content_type,
            "template_text": self.template_text,
            "variables": self.variables,
            "success_score": self.success_score,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class BannedWord(Base):
    """违禁词表"""
    __tablename__ = "banned_word"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    word = Column(String(200), nullable=False)
    severity = Column(String(10))  # high, medium, low
    category = Column(String(50))  # school_district, price, finance, promise, ad_law
    regex_pattern = Column(String(500))
    replacement_suggestion = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_current_time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "word": self.word,
            "severity": self.severity,
            "category": self.category,
            "regex_pattern": self.regex_pattern,
            "replacement_suggestion": self.replacement_suggestion,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Lead(Base):
    """客户线索表"""
    __tablename__ = "lead"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    agent_id = Column(String(100))
    source = Column(String(50))
    customer_info = Column(JSON)
    intention_level = Column(Integer)  # 1-5
    property_match = Column(JSON, default=list)
    conversation_history = Column(JSON, default=list)
    status = Column(String(20), default="pending")  # pending, contacted, invited, visited, closed, lost
    created_at = Column(DateTime, default=get_current_time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "source": self.source,
            "customer_info": self.customer_info,
            "intention_level": self.intention_level,
            "property_match": self.property_match,
            "conversation_history": self.conversation_history,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_url: str = "sqlite:///./real_estate_agent.db"):
        self.db_url = db_url
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """删除所有表"""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()

    def init_sample_data(self):
        """初始化示例数据"""
        from knowledge.banned_words import BannedWords
        
        session = self.get_session()
        try:
            # 初始化违禁词数据
            banned_words = BannedWords()
            all_words = banned_words.get_all_words()
            
            for category, words in all_words.items():
                for word in words:
                    existing = session.query(BannedWord).filter_by(word=word).first()
                    if not existing:
                        session.add(BannedWord(
                            word=word,
                            severity="high" if category in ["absolute_terms", "investment_promises"] else "medium",
                            category=category,
                            active=True,
                        ))
            
            session.commit()
            print(f"Initialized {len(all_words)} banned word categories")
        except Exception as e:
            session.rollback()
            print(f"Failed to init sample data: {e}")
        finally:
            session.close()
