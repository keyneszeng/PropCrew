"""
数据分析接口

提供复盘分析、选题策划、政策科普转化等数据分析 API。
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.models.schemas import (
    TopicPlanningRequest,
    TopicPlanningResponse,
    ReviewAnalysisRequest,
    ReviewAnalysisResponse,
    PolicyConversionRequest,
    PolicyConversionResponse,
)
from skills.review_analyzer import ReviewAnalyzer
from skills.topic_planner import TopicPlanner
from agent.review_analysis import ReviewAnalysisAgent
from agent.policy_converter_agent import PolicyConverterAgent
from core.model_router import ModelRouter

router = APIRouter(prefix="/api/analysis", tags=["数据分析"])


# 全局组件（由 main.py 初始化）
_model_router: Optional[ModelRouter] = None
_agents: Optional[Dict[str, Any]] = None


def init_components(model_router: ModelRouter, agents: Optional[Dict[str, Any]] = None):
    """初始化全局组件"""
    global _model_router, _agents
    _model_router = model_router
    _agents = agents


# ========== 选题策划 ==========

@router.post("/topic/plan", response_model=TopicPlanningResponse)
async def plan_topics(request: TopicPlanningRequest):
    """
    选题策划
    
    基于发布记录和趋势，推荐下周选题。
    """
    try:
        if not _model_router:
            raise HTTPException(status_code=500, detail="模型路由器未初始化")
        
        topic_planner = TopicPlanner(model_router=_model_router)
        result = await topic_planner.execute({
            "publish_history": request.publish_history or [],
            "trends": request.trends or [],
            "customer_questions": request.customer_questions or [],
        })
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        return TopicPlanningResponse(
            success=True,
            topics=result.output.get("topics", []),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 复盘分析 ==========

@router.post("/review/analyze", response_model=ReviewAnalysisResponse)
async def analyze_review(request: ReviewAnalysisRequest):
    """
    复盘分析
    
    分析历史发布数据，生成复盘报告和下周选题建议。
    使用 ReviewAnalysisAgent 进行深度分析。
    """
    try:
        if not _model_router:
            raise HTTPException(status_code=500, detail="模型路由器未初始化")
        
        # 优先使用 ReviewAnalysisAgent
        if _agents and "review_analyst" in _agents:
            result = await _agents["review_analyst"].execute({
                "publish_records": request.publish_records,
                "engagement_data": request.engagement_data or {},
                "user_feedback": request.user_feedback or [],
            })
            
            if not result.success:
                raise HTTPException(status_code=500, detail=result.error)
            
            report = json.loads(result.content)
            
            return ReviewAnalysisResponse(
                success=True,
                report=report,
                weekly_plan=report.get("weekly_plan"),
            )
        else:
            # Fallback: 使用 ReviewAnalyzer Skill
            review_analyzer = ReviewAnalyzer(model_router=_model_router)
            result = await review_analyzer.execute({
                "publish_records": request.publish_records,
                "engagement_data": request.engagement_data or {},
            })
            
            if not result.success:
                raise HTTPException(status_code=500, detail=result.error)
            
            return ReviewAnalysisResponse(
                success=True,
                report=result.output,
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 政策科普转化 ==========

@router.post("/policy/convert", response_model=PolicyConversionResponse)
async def convert_policy(request: PolicyConversionRequest):
    """
    政策科普转化
    
    将政策原文转化为通俗易懂的科普内容，支持多平台输出。
    使用 PolicyConverterAgent 进行深度解读。
    """
    try:
        if not _model_router:
            raise HTTPException(status_code=500, detail="模型路由器未初始化")
        
        # 优先使用 PolicyConverterAgent
        if _agents and "policy_converter" in _agents:
            result = await _agents["policy_converter"].execute({
                "policy_text": request.policy_text,
                "policy_title": request.policy_title or "",
                "target_audience": request.target_audience or "general",
            })
            
            if not result.success:
                raise HTTPException(status_code=500, detail=result.error)
            
            report = json.loads(result.content)
            
            return PolicyConversionResponse(
                success=True,
                plain_explanation=report.get("plain_explanation"),
                detailed_explanation=report.get("detailed_explanation"),
                impact_analysis=report.get("impact_analysis"),
                output_plans=report.get("output_plans"),
                action_guide=report.get("action_guide"),
            )
        else:
            # Fallback: 使用 PolicyConverter Skill
            from skills.policy_converter import PolicyConverter
            policy_converter = PolicyConverter(model_router=_model_router)
            result = await policy_converter.execute({
                "policy_text": request.policy_text,
                "target_audience": request.target_audience or "general",
            })
            
            if not result.success:
                raise HTTPException(status_code=500, detail=result.error)
            
            return PolicyConversionResponse(
                success=True,
                plain_explanation=result.output.get("summary"),
                output_plans=result.output.get("output_plans"),
                action_guide=result.output.get("action_guide"),
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 数据统计 ==========

@router.get("/stats/overview")
async def get_stats_overview():
    """
    数据概览
    
    获取系统各模块的数据统计概览。
    """
    try:
        return {
            "success": True,
            "data": {
                "total_agents": len(_agents) if _agents else 0,
                "agent_list": [agent.get_info() for agent in _agents.values()] if _agents else [],
                "model_ready": _model_router is not None,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
