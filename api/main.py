"""
FastAPI 主应用

房地产销售 Agent 智能体的 API 服务。
"""

import os
import sys
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from api.routes.content import router as content_router, init_components as init_content_components
from api.routes.analysis import router as analysis_router, init_components as init_analysis_components
from api.routes.batch import router as batch_router, init_components as init_batch_components
from monitoring.logger import AgentLogger
from monitoring.metrics import MetricsCollector
from monitoring.health import HealthChecker

from api.models.schemas import SystemStatusResponse
from core.context_bus import ContextBus
from core.task_manager import TaskManager
from core.model_router import ModelRouter, ModelConfig
from agent.coordinator import ContentCoordinatorAgent
from agent.property_analyst import PropertyAnalystAgent
from agent.xiaohongshu_writer import XiaohongshuWriterAgent
from agent.video_director import VideoDirectorAgent
from agent.district_researcher import DistrictResearcherAgent
from agent.lead_converter import LeadConverterAgent
from agent.compliance_officer import ComplianceOfficerAgent
from agent.review_analysis import ReviewAnalysisAgent
from agent.policy_converter_agent import PolicyConverterAgent
from compliance.rule_engine import ComplianceRuleEngine
from compliance.ai_checker import AIComplianceChecker
from knowledge.banned_words import BannedWords
from database.models import DatabaseManager
from config.settings import settings


# 全局组件
context_bus: Optional[ContextBus] = None
task_manager: Optional[TaskManager] = None
model_router: Optional[ModelRouter] = None
agents: Optional[Dict[str, Any]] = None
compliance_engine: Optional[ComplianceRuleEngine] = None
db_manager: Optional[DatabaseManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global context_bus, task_manager, model_router, agents, compliance_engine, db_manager
    
    # 启动时初始化
    print("🚀 启动房地产销售 Agent 智能体...")
    
    # 初始化上下文总线
    context_bus = ContextBus()
    
    # 初始化任务管理器
    task_manager = TaskManager()
    
    # 初始化模型路由器
    model_router = ModelRouter()
    
    # 注册模型
    if settings.DEEPSEEK_API_KEY:
        config = ModelConfig(
            provider="deepseek",
            model_name="deepseek-chat",
            api_key=settings.DEEPSEEK_API_KEY,
            temperature=settings.MODEL_TEMPERATURE,
            max_tokens=settings.MODEL_MAX_TOKENS,
            timeout=settings.MODEL_TIMEOUT,
        )
        model_router.register_model(config)
        print(f"✅ 模型 deepseek-v3 已注册")
    
    if settings.OPENAI_API_KEY:
        config = ModelConfig(
            provider="openai",
            model_name="gpt-4o",
            api_key=settings.OPENAI_API_KEY,
            temperature=settings.MODEL_TEMPERATURE,
            max_tokens=settings.MODEL_MAX_TOKENS,
            timeout=settings.MODEL_TIMEOUT,
        )
        model_router.register_model(config)
        print(f"✅ 模型 gpt-4o 已注册")
    
    # ====== 初始化 Agent ======
    agents = {}
    
    # Phase 1/2 Agent
    coordinator = ContentCoordinatorAgent(model_router=model_router)
    coordinator.set_context_bus(context_bus)
    task_manager.register_agent(coordinator.agent_id, coordinator)
    agents["coordinator"] = coordinator
    print(f"  ✅ Agent: 内容总监 ({coordinator.agent_id})")
    
    analyst = PropertyAnalystAgent(model_router=model_router)
    analyst.set_context_bus(context_bus)
    task_manager.register_agent(analyst.agent_id, analyst)
    agents["analyst"] = analyst
    print(f"  ✅ Agent: 卖点分析师 ({analyst.agent_id})")
    
    writer = XiaohongshuWriterAgent(model_router=model_router)
    writer.set_context_bus(context_bus)
    task_manager.register_agent(writer.agent_id, writer)
    agents["xiaohongshu_writer"] = writer
    print(f"  ✅ Agent: 小红书文案 ({writer.agent_id})")
    
    video_dir = VideoDirectorAgent(model_router=model_router)
    video_dir.set_context_bus(context_bus)
    task_manager.register_agent(video_dir.agent_id, video_dir)
    agents["video_director"] = video_dir
    print(f"  ✅ Agent: 短视频编导 ({video_dir.agent_id})")
    
    district_researcher = DistrictResearcherAgent(model_router=model_router)
    district_researcher.set_context_bus(context_bus)
    task_manager.register_agent(district_researcher.agent_id, district_researcher)
    agents["district_researcher"] = district_researcher
    print(f"  ✅ Agent: 板块研究员 ({district_researcher.agent_id})")
    
    # Phase 3: 新增 Agent
    lead_converter = LeadConverterAgent(
        model_router=model_router,
        model="deepseek-v3",
    )
    lead_converter.set_context_bus(context_bus)
    task_manager.register_agent(lead_converter.agent_id, lead_converter)
    agents["lead_converter"] = lead_converter
    print(f"  ✅ Agent: 线索转化顾问 ({lead_converter.agent_id})")
    
    review_analyst = ReviewAnalysisAgent(
        model_router=model_router,
        model="deepseek-v3",
    )
    review_analyst.set_context_bus(context_bus)
    task_manager.register_agent(review_analyst.agent_id, review_analyst)
    agents["review_analyst"] = review_analyst
    print(f"  ✅ Agent: 复盘分析师 ({review_analyst.agent_id})")
    
    policy_converter = PolicyConverterAgent(
        model_router=model_router,
        model="deepseek-v3",
    )
    policy_converter.set_context_bus(context_bus)
    task_manager.register_agent(policy_converter.agent_id, policy_converter)
    agents["policy_converter"] = policy_converter
    print(f"  ✅ Agent: 政策科普顾问 ({policy_converter.agent_id})")
    
    # 合规质检 Agent（依赖 compliance_engine 和 model_router）
    compliance_officer = ComplianceOfficerAgent(
        model_router=model_router,
        model="deepseek-v3",
    )
    compliance_officer.set_context_bus(context_bus)
    task_manager.register_agent(compliance_officer.agent_id, compliance_officer)
    agents["compliance_officer"] = compliance_officer
    print(f"  ✅ Agent: 合规质检员 ({compliance_officer.agent_id})")
    
    print(f"\n✅ 共 {len(agents)} 个 Agent 已注册（Phase 1/2: 5 + Phase 3: 4）")
    
    # ====== 初始化合规引擎 ======
    compliance_engine = ComplianceRuleEngine()
    print(f"✅ 合规引擎已初始化（违禁词数量：{compliance_engine.banned_words.get_word_count()}）")
    
    # ====== 初始化数据库 ======
    db_manager = DatabaseManager(settings.DATABASE_URL)
    db_manager.create_tables()
    print(f"✅ 数据库已初始化")
    
    # ====== 初始化 API 路由组件 ======
    init_content_components(
        context_bus=context_bus,
        task_manager=task_manager,
        model_router=model_router,
        agents=agents,
        compliance_engine=compliance_engine,
        db_manager=db_manager,
    )
    init_analysis_components(
        model_router=model_router,
        agents=agents,
    )
    print("🎉 系统启动完成！（9 个 Agent, 13 个 Skill, 7 张表, 监控就绪）")
    
    yield
    
    # 关闭时清理
    print("🛑 系统关闭...")


# 创建 FastAPI 应用
app = FastAPI(
    title="房地产销售 Agent 智能体 API",
    description="AI 驱动的房地产内容生成平台 | Phase 3 - 完整功能版",
    version="2.0.0",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(content_router)
app.include_router(analysis_router)
app.include_router(batch_router)


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "agents": len(agents) if agents else 0,
        "model_router": model_router is not None,
        "compliance_engine": compliance_engine is not None,
        "database": db_manager is not None,
    }

# 详细健康检查
@app.get("/api/monitoring/health")
async def detailed_health():
    '''详细健康检查'''
    checker = HealthChecker()
    return checker.check_all(
        agents=agents,
        db=db_manager,
        model_router=model_router,
    )


# 性能指标
@app.get("/api/monitoring/metrics")
async def get_metrics():
    '''获取性能指标'''
    from monitoring.metrics import MetricsCollector
    mc = MetricsCollector()
    return mc.get_stats()



# 系统状态
@app.get("/api/system/status", response_model=SystemStatusResponse)
async def system_status():
    """系统状态"""
    try:
        agent_list = []
        if agents:
            agent_list = [agent.get_info() for agent in agents.values()]
        
        return SystemStatusResponse(
            agents=len(agents) if agents else 0,
            skills=9,  # 9 个 Skill
            history_count=0,
            banned_words_count=compliance_engine.banned_words.get_word_count() if compliance_engine else 0,
            task_stats=task_manager.get_stats() if task_manager else {},
            agent_info=agent_list,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Agent 列表
@app.get("/api/agents")
async def list_agents():
    """获取所有注册的 Agent 信息"""
    try:
        if not agents:
            return {"agents": []}
        
        return {
            "agents": [
                {
                    "id": agent_id,
                    "name": agent.name,
                    "description": agent.description,
                    "model": agent.model,
                    "skills": [s.skill_id for s in agent.skills if hasattr(s, 'skill_id')],
                }
                for agent_id, agent in agents.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "detail": "服务器内部错误"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
