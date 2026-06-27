"""
内容生成接口

提供内容生成、合规检查、线索转化等 API。
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api.models.schemas import (
    ContentGenerationRequest,
    ContentGenerationResponse,
    ComplianceCheckRequest,
    ComplianceCheckResponse,
    LeadConversionRequest,
    LeadConversionResponse,
    LeadCreateRequest,
    LeadUpdateRequest,
    LeadResponse,
    LeadListResponse,
    TopicPlanningRequest,
    TopicPlanningResponse,
)
from core.context_bus import ContextBus
from core.task_manager import TaskManager, TaskPriority
from core.model_router import ModelRouter, ModelConfig
from agent.coordinator import ContentCoordinatorAgent
from agent.property_analyst import PropertyAnalystAgent
from agent.xiaohongshu_writer import XiaohongshuWriterAgent
from agent.lead_converter import LeadConverterAgent
from agent.compliance_officer import ComplianceOfficerAgent
from compliance.rule_engine import ComplianceRuleEngine
from skills.talk_generator import TalkGenerator
from skills.topic_planner import TopicPlanner
from database.models import DatabaseManager, Property, Post, Lead

router = APIRouter(prefix="/api/content", tags=["内容生成"])


# 全局组件（由 main.py 初始化）
_context_bus: Optional[ContextBus] = None
_task_manager: Optional[TaskManager] = None
_model_router: Optional[ModelRouter] = None
_agents: Optional[Dict[str, Any]] = None
_compliance_engine: Optional[ComplianceRuleEngine] = None
_db_manager: Optional[DatabaseManager] = None


def init_components(
    context_bus: ContextBus,
    task_manager: TaskManager,
    model_router: ModelRouter,
    agents: Dict[str, Any],
    compliance_engine: ComplianceRuleEngine,
    db_manager: DatabaseManager,
):
    """初始化全局组件"""
    global _context_bus, _task_manager, _model_router, _agents, _compliance_engine, _db_manager
    _context_bus = context_bus
    _task_manager = task_manager
    _model_router = model_router
    _agents = agents
    _compliance_engine = compliance_engine
    _db_manager = db_manager


# ========== 内容生成 ==========

@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest):
    """
    生成内容
    
    根据房源信息，生成指定平台和内容类型的文案。
    自动执行完整工作流：内容分析 → 卖点提取 → 内容创作 → 合规检查。
    """
    try:
        if not _context_bus or not _agents:
            raise HTTPException(status_code=500, detail="系统未初始化")
        
        # 清空上下文
        _context_bus.clear()
        
        # 构建房源信息文本
        property_text = f"""
        地址：{request.property_info.address or '未知'}
        户型：{request.property_info.rooms or '未知'}
        面积：{request.property_info.area or '未知'}平米
        价格：{request.property_info.price or '未知'}万
        特色：{request.property_info.decoration or '无'}
        """
        
        # 步骤 1: 内容总监分析
        coordinator_result = await _agents["coordinator"].execute({
            "user_request": f"帮我写一条{request.platform}的{request.content_type}：{property_text}",
            "property_info": property_text,
        })
        
        # 步骤 2: 卖点分析师
        analyst_result = await _agents["analyst"].execute({
            "property_info": property_text,
        })
        
        # 步骤 3: 根据平台选择内容 Agent
        content = {}
        if request.platform == "xiaohongshu" or request.content_type == "note":
            writer_result = await _agents["xiaohongshu_writer"].execute({
                "property_info": property_text,
                "selling_points": json.loads(analyst_result.content).get("selling_points", []),
            })
            content = json.loads(writer_result.content)
        elif request.platform in ["douyin", "video"] or request.content_type in ["script", "video"]:
            writer_result = await _agents["video_director"].execute({
                "property_info": property_text,
                "selling_points": json.loads(analyst_result.content).get("selling_points", []),
            })
            content = json.loads(writer_result.content)
        else:
            writer_result = await _agents["xiaohongshu_writer"].execute({
                "property_info": property_text,
                "selling_points": json.loads(analyst_result.content).get("selling_points", []),
            })
            content = json.loads(writer_result.content)
        
        # 步骤 4: 合规检查（双层）
        full_text = f"{content.get('title', '')} {content.get('content', '')} {content.get('text', '')}"
        if "compliance_officer" in _agents:
            compliance_result = await _agents["compliance_officer"].execute({
                "text": full_text,
                "platform": request.platform,
                "content_type": request.content_type,
            })
            compliance_report = json.loads(compliance_result.content)
        else:
            rule_result = _compliance_engine.check(full_text)
            compliance_report = rule_result.to_dict()
        
        # 保存到数据库
        if _db_manager:
            session = _db_manager.get_session()
            try:
                existing_property = session.query(Property).filter_by(
                    address=request.property_info.address
                ).first()
                
                if not existing_property:
                    existing_property = Property(
                        title=request.property_info.title,
                        address=request.property_info.address,
                        district=request.property_info.district,
                        price=request.property_info.price,
                        area=request.property_info.area,
                        rooms=request.property_info.rooms,
                        floor=request.property_info.floor,
                        total_floors=request.property_info.total_floors,
                        decoration=request.property_info.decoration,
                        property_type=request.property_info.property_type,
                        tags=request.property_info.tags,
                    )
                    session.add(existing_property)
                    session.commit()
                
                post = Post(
                    property_id=existing_property.id,
                    agent_id="api",
                    platform=request.platform,
                    content_type=request.content_type,
                    content=content,
                    status="draft",
                    compliance_report=compliance_report,
                )
                session.add(post)
                session.commit()
            finally:
                session.close()
        
        return ContentGenerationResponse(
            success=True,
            content=content,
            compliance_report=compliance_report,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 合规检查 ==========

@router.post("/compliance/check", response_model=ComplianceCheckResponse)
async def check_compliance(request: ComplianceCheckRequest):
    """
    合规检查（双层）
    
    第一层：规则引擎扫描违禁词/绝对化用语/投资承诺等
    第二层：AI 语义检查隐含风险
    """
    try:
        if not _compliance_engine:
            raise HTTPException(status_code=500, detail="合规引擎未初始化")
        
        # Layer 1: 规则引擎
        result = _compliance_engine.check(request.text)
        
        # Layer 2: AI 检查（如果有 compliance_officer）
        comprehensive_report = None
        if _agents and "compliance_officer" in _agents:
            compliance_result = await _agents["compliance_officer"].execute({
                "text": request.text,
                "platform": request.platform or "xiaohongshu",
                "content_type": request.content_type or "note",
            })
            if compliance_result.success:
                comprehensive_report = json.loads(compliance_result.content)
        
        return ComplianceCheckResponse(
            success=True,
            is_compliant=result.is_compliant,
            violations=result.violations,
            suggestions=result.suggestions,
            risk_level=result.risk_level,
            comprehensive_report=comprehensive_report,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 线索转化 ==========

@router.post("/lead/convert", response_model=LeadConversionResponse)
async def convert_lead(request: LeadConversionRequest):
    """
    线索转化
    
    根据客户问题生成回复话术，支持评论回复/私信/电话邀约等场景。
    使用 LeadConverterAgent 进行完整的意图分析和话术生成。
    """
    try:
        if not _agents or "lead_converter" not in _agents:
            # Fallback: 使用 TalkGenerator Skill
            talk_generator = TalkGenerator(model_router=_model_router)
            result = await talk_generator.execute({
                "customer_question": request.customer_question,
                "customer_profile": request.customer_profile,
                "scenario": request.scenario,
            })
            
            if not result.success:
                raise HTTPException(status_code=500, detail=result.error)
            
            return LeadConversionResponse(
                success=True,
                options=result.output.get("options", []),
            )
        
        # 使用 LeadConverterAgent
        converter_result = await _agents["lead_converter"].execute({
            "customer_question": request.customer_question,
            "customer_profile": request.customer_profile,
            "scenario": request.scenario,
            "property_match": request.property_match or [],
        })
        
        if not converter_result.success:
            raise HTTPException(status_code=500, detail=converter_result.error)
        
        result_data = json.loads(converter_result.content)
        
        # 保存到数据库
        if _db_manager:
            session = _db_manager.get_session()
            try:
                lead = Lead(
                    agent_id="api",
                    source=request.scenario or "api",
                    customer_info={
                        "question": request.customer_question,
                        "profile": request.customer_profile,
                    },
                    intention_level=result_data.get("intent_analysis", {}).get("intensity", 3),
                    property_match=request.property_match or [],
                    conversation_history=[{
                        "role": "customer",
                        "content": request.customer_question,
                        "timestamp": str(datetime.now()),
                    }],
                    status="pending",
                )
                session.add(lead)
                session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()
        
        return LeadConversionResponse(
            success=True,
            options=result_data.get("options", []),
            intent_analysis=result_data.get("intent_analysis"),
            recommended_option=result_data.get("recommended_option"),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 线索管理 ==========

@router.post("/lead/create", response_model=LeadResponse)
async def create_lead(request: LeadCreateRequest):
    """创建客户线索记录"""
    try:
        if not _db_manager:
            raise HTTPException(status_code=500, detail="数据库未初始化")
        
        session = _db_manager.get_session()
        try:
            lead = Lead(
                agent_id=request.agent_id,
                source=request.source,
                customer_info=request.customer_info,
                intention_level=request.intention_level,
                property_match=request.property_match or [],
                conversation_history=[],
                status="pending",
            )
            session.add(lead)
            session.commit()
            
            return LeadResponse(
                success=True,
                lead=lead.to_dict(),
            )
        finally:
            session.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads", response_model=LeadListResponse)
async def list_leads(status: Optional[str] = None, limit: int = 20, offset: int = 0):
    """获取客户线索列表"""
    try:
        if not _db_manager:
            raise HTTPException(status_code=500, detail="数据库未初始化")
        
        session = _db_manager.get_session()
        try:
            query = session.query(Lead)
            if status:
                query = query.filter(Lead.status == status)
            
            total = query.count()
            leads = query.order_by(Lead.created_at.desc()).offset(offset).limit(limit).all()
            
            return LeadListResponse(
                success=True,
                leads=[lead.to_dict() for lead in leads],
                total=total,
            )
        finally:
            session.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/lead/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: str, request: LeadUpdateRequest):
    """更新客户线索"""
    try:
        if not _db_manager:
            raise HTTPException(status_code=500, detail="数据库未初始化")
        
        session = _db_manager.get_session()
        try:
            lead = session.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                raise HTTPException(status_code=404, detail="线索不存在")
            
            if request.intention_level is not None:
                lead.intention_level = request.intention_level
            if request.status is not None:
                lead.status = request.status
            if request.conversation_history is not None:
                lead.conversation_history = request.conversation_history
            
            session.commit()
            
            return LeadResponse(
                success=True,
                lead=lead.to_dict(),
            )
        finally:
            session.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from datetime import datetime
