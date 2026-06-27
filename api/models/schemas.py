"""
Pydantic 模型定义

用于 API 请求和响应的数据验证。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ========== 基础模型 ==========

class PropertyInfo(BaseModel):
    """房源信息"""
    title: str = Field(..., description="房源标题")
    address: Optional[str] = None
    district: Optional[str] = None
    price: Optional[float] = None
    area: Optional[float] = None
    rooms: Optional[str] = None
    floor: Optional[str] = None
    total_floors: Optional[int] = None
    decoration: Optional[str] = None
    property_type: Optional[str] = None
    tags: Optional[List[str]] = None


# ========== 内容生成 ==========

class ContentGenerationRequest(BaseModel):
    """内容生成请求"""
    property_info: PropertyInfo
    platform: str = Field("xiaohongshu", description="发布平台")
    content_type: str = Field("note", description="内容类型")
    tone: Optional[str] = None
    word_count: Optional[int] = 400


class ContentGenerationResponse(BaseModel):
    """内容生成响应"""
    success: bool
    content: Optional[Dict[str, Any]] = None
    compliance_report: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ========== 合规检查 ==========

class ComplianceCheckRequest(BaseModel):
    """合规检查请求"""
    text: str = Field(..., description="待检查文本")
    platform: Optional[str] = Field("xiaohongshu", description="发布平台")
    content_type: Optional[str] = Field("note", description="内容类型")


class ComplianceCheckResponse(BaseModel):
    """合规检查响应"""
    success: bool
    is_compliant: bool
    violations: List[Dict[str, Any]]
    suggestions: List[str]
    risk_level: str
    comprehensive_report: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ========== 线索转化 ==========

class LeadConversionRequest(BaseModel):
    """线索转化请求"""
    customer_question: str = Field(..., description="客户问题")
    customer_profile: Optional[Dict[str, Any]] = None
    scenario: Optional[str] = "general"
    property_match: Optional[List[Dict[str, Any]]] = None


class LeadConversionResponse(BaseModel):
    """线索转化响应"""
    success: bool
    options: List[Dict[str, Any]]
    intent_analysis: Optional[Dict[str, Any]] = None
    recommended_option: Optional[int] = None
    error: Optional[str] = None


# ========== 选题策划 ==========

class TopicPlanningRequest(BaseModel):
    """选题策划请求"""
    publish_history: Optional[List[Dict[str, Any]]] = None
    trends: Optional[List[str]] = None
    customer_questions: Optional[List[str]] = None


class TopicPlanningResponse(BaseModel):
    """选题策划响应"""
    success: bool
    topics: List[Dict[str, Any]]
    error: Optional[str] = None


# ========== 复盘分析 ==========

class ReviewAnalysisRequest(BaseModel):
    """复盘分析请求"""
    publish_records: List[Dict[str, Any]] = Field(..., description="发布记录列表")
    engagement_data: Optional[Dict[str, Any]] = None
    user_feedback: Optional[List[Dict[str, Any]]] = None


class ReviewAnalysisResponse(BaseModel):
    """复盘分析响应"""
    success: bool
    report: Optional[Dict[str, Any]] = None
    weekly_plan: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ========== 政策科普转化 ==========

class PolicyConversionRequest(BaseModel):
    """政策科普转化请求"""
    policy_text: str = Field(..., description="政策原文")
    policy_title: Optional[str] = Field("", description="政策标题")
    target_audience: Optional[str] = Field("general", description="目标受众")
    platform: Optional[str] = Field("all", description="输出平台偏好")


class PolicyConversionResponse(BaseModel):
    """政策科普转化响应"""
    success: bool
    plain_explanation: Optional[str] = None
    detailed_explanation: Optional[str] = None
    impact_analysis: Optional[List[Dict[str, Any]]] = None
    output_plans: Optional[List[Dict[str, Any]]] = None
    action_guide: Optional[List[str]] = None
    error: Optional[str] = None


# ========== 线索管理 ==========

class LeadCreateRequest(BaseModel):
    """创建线索请求"""
    agent_id: str
    source: str
    customer_info: Dict[str, Any]
    intention_level: Optional[int] = None
    property_match: Optional[List[Dict[str, Any]]] = None


class LeadUpdateRequest(BaseModel):
    """更新线索请求"""
    intention_level: Optional[int] = None
    status: Optional[str] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None


class LeadResponse(BaseModel):
    """线索响应"""
    success: bool
    lead: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class LeadListResponse(BaseModel):
    """线索列表响应"""
    success: bool
    leads: List[Dict[str, Any]]
    total: int
    error: Optional[str] = None


# ========== 系统状态 ==========

class SystemStatusResponse(BaseModel):
    """系统状态响应"""
    agents: int
    skills: int
    history_count: int
    banned_words_count: int
    task_stats: Dict[str, Any]
    agent_info: Optional[List[Dict[str, Any]]] = None


# ========== 数据库创建模型 ==========

class PropertyCreate(BaseModel):
    """创建房源"""
    title: str
    address: Optional[str] = None
    district: Optional[str] = None
    price: Optional[float] = None
    area: Optional[float] = None
    rooms: Optional[str] = None
    floor: Optional[str] = None
    total_floors: Optional[int] = None
    decoration: Optional[str] = None
    property_type: Optional[str] = None
    tags: Optional[List[str]] = None


class PostCreate(BaseModel):
    """创建发布记录"""
    property_id: Optional[str] = None
    agent_id: str
    platform: str
    content_type: str
    content: Dict[str, Any]
    status: str = "draft"


class LeadCreate(BaseModel):
    """创建线索"""
    agent_id: str
    source: str
    customer_info: Dict[str, Any]
    intention_level: Optional[int] = None
    property_match: Optional[List[Dict[str, Any]]] = None
