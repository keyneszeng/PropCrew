"""
批量生成 / 反馈接口
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from skills.batch_generator import BatchGenerator
from skills.feedback_collector import FeedbackCollector
from core.model_router import ModelRouter

router = APIRouter(prefix="/api", tags=["批量 & 反馈"])

_model_router: Optional[ModelRouter] = None


def init_components(model_router: ModelRouter):
    global _model_router
    _model_router = model_router


# ====== 请求/响应模型 ======
class BatchGenerateRequest(BaseModel):
    properties: List[Dict[str, Any]]
    platforms: List[str] = ["xiaohongshu"]
    content_types: List[str] = ["note"]


class BatchGenerateResponse(BaseModel):
    success: bool
    batch_id: Optional[str] = None
    results: List[Dict[str, Any]] = []
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class FeedbackSubmitRequest(BaseModel):
    agent_name: str
    score: int
    needs_improvement: List[str] = []
    good_points: List[str] = []


class FeedbackSubmitResponse(BaseModel):
    success: bool
    feedback_id: Optional[str] = None
    optimization_suggestions: List[str] = []
    error: Optional[str] = None


import asyncio


# ====== 批量生成 ======
@router.post("/batch/generate", response_model=BatchGenerateResponse)
async def batch_generate(request: BatchGenerateRequest):
    """批量内容生成"""
    try:
        if not _model_router:
            raise HTTPException(status_code=500, detail="系统未初始化")

        generator = BatchGenerator(model_router=_model_router)
        result = await generator.execute({
            "properties": request.properties,
            "platforms": request.platforms,
            "content_types": request.content_types,
        })

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        return BatchGenerateResponse(
            success=True,
            batch_id=result.output.get("batch_id"),
            results=result.output.get("results", []),
            summary=result.output.get("summary"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====== 反馈收集 ======
@router.post("/feedback/submit", response_model=FeedbackSubmitResponse)
async def submit_feedback(request: FeedbackSubmitRequest):
    """提交用户反馈"""
    try:
        collector = FeedbackCollector(model_router=_model_router)
        result = await collector.execute({
            "feedback_data": {
                "agent_name": request.agent_name,
                "score": request.score,
                "needs_improvement": request.needs_improvement,
                "good_points": request.good_points,
            }
        })

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        return FeedbackSubmitResponse(
            success=True,
            feedback_id=result.output.get("feedback_id"),
            optimization_suggestions=result.output.get("optimization_suggestions", []),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/stats")
async def feedback_stats():
    """反馈统计"""
    try:
        collector = FeedbackCollector(model_router=_model_router)
        stats = collector.get_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
