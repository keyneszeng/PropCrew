"""
Agent 单元测试

测试 Phase 1-3 的所有 Agent。
"""

import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Any, Dict

from core.agent_base import BaseAgent, AgentResult
from core.model_router import ModelRouter
from core.context_bus import ContextBus

# 模拟 ModelRouter
class MockModelRouter:
    """模拟模型路由器"""
    
    def __init__(self):
        self.response_map = {}
    
    async def chat(self, messages, model_key="deepseek-v3", temperature=0.7, max_tokens=2000):
        """模拟 LLM 调用"""
        # 检查 response_map 中是否有匹配
        for key, response in self.response_map.items():
            if key in str(messages):
                return response
        return json.dumps({"test": "mock_response"})


def test_agent_base():
    """测试 Agent 基类"""
    agent = BaseAgent(
        agent_id="test_agent",
        name="测试Agent",
        description="测试用",
        system_prompt="你是测试Agent",
    )
    
    info = agent.get_info()
    assert info["agent_id"] == "test_agent"
    assert info["name"] == "测试Agent"
    assert info["model"] == "deepseek-v3"
    
    # 测试 Context Bus
    context_bus = ContextBus()
    agent.set_context_bus(context_bus)
    assert agent._context_bus is not None


def test_agent_result():
    """测试 AgentResult"""
    result = AgentResult(
        agent_id="test",
        content='{"key": "value"}',
        metadata={"key": "value"},
        success=True,
    )
    
    d = result.to_dict()
    assert d["agent_id"] == "test"
    assert d["success"] == True
    
    result2 = AgentResult(
        agent_id="test",
        content="",
        success=False,
        error="错误信息",
    )
    assert result2.error == "错误信息"


def test_context_bus():
    """测试 Context Bus"""
    bus = ContextBus()
    
    # 初始状态
    assert bus.get_context() == {}
    
    # 更新上下文
    bus.update_context({"key1": "value1"})
    assert bus.get_context()["key1"] == "value1"
    
    # 批量更新
    bus.update_context({"key2": "value2", "key3": "value3"})
    ctx = bus.get_context()
    assert ctx["key1"] == "value1"
    assert ctx["key2"] == "value2"
    
    # 清空
    bus.clear()
    assert bus.get_context() == {}


# ====== Phase 3 Agent 测试 ======

def test_lead_converter_import():
    """测试 LeadConverterAgent 导入"""
    try:
        from agent.lead_converter import LeadConverterAgent
        assert LeadConverterAgent is not None
    except ImportError as e:
        assert False, f"导入失败: {e}"


def test_review_analysis_import():
    """测试 ReviewAnalysisAgent 导入"""
    try:
        from agent.review_analysis import ReviewAnalysisAgent
        assert ReviewAnalysisAgent is not None
    except ImportError as e:
        assert False, f"导入失败: {e}"


def test_policy_converter_agent_import():
    """测试 PolicyConverterAgent 导入"""
    try:
        from agent.policy_converter_agent import PolicyConverterAgent
        assert PolicyConverterAgent is not None
    except ImportError as e:
        assert False, f"导入失败: {e}"


def test_compliance_officer_import():
    """测试 ComplianceOfficerAgent 导入"""
    try:
        from agent.compliance_officer import ComplianceOfficerAgent
        assert ComplianceOfficerAgent is not None
    except ImportError as e:
        assert False, f"导入失败: {e}"


async def _test_lead_converter_execute():
    """测试 LeadConverterAgent 执行（需要模型）"""
    from agent.lead_converter import LeadConverterAgent
    from skills.talk_generator import TalkGenerator
    
    mock_router = MockModelRouter()
    mock_router.response_map = {
        "客户意图": json.dumps({
            "intent_type": "price_inquiry",
            "intensity": 4,
            "key_concerns": ["价格", "优惠"],
            "persona": "首次购房者",
        }),
        "你是房地产销售": json.dumps({
            "intent_analysis": {
                "intent_type": "price_inquiry",
                "intensity": 4,
                "key_concerns": ["价格"],
                "persona": "首次购房",
            },
            "options": [
                {
                    "id": 1,
                    "scenario": "comment_reply",
                    "style": "亲切",
                    "text": "您好！价格我们可以详细聊聊～",
                    "key_highlights": ["友好开场"],
                    "call_to_action": "进一步沟通",
                }
            ],
            "recommended_option": 1,
            "compliance_notes": ["避免承诺具体折扣"],
        }),
    }
    
    agent = LeadConverterAgent(model_router=mock_router)
    agent.set_context_bus(ContextBus())
    
    result = await agent.execute({
        "customer_question": "这套房子价格还能再低吗？",
        "customer_profile": {},
        "scenario": "comment_reply",
    })
    
    assert result.success == True
    data = json.loads(result.content)
    assert "options" in data
    assert len(data["options"]) > 0


async def _test_review_analysis_execute():
    """测试 ReviewAnalysisAgent 执行（需要模型）"""
    from agent.review_analysis import ReviewAnalysisAgent
    
    mock_router = MockModelRouter()
    mock_router.response_map = {
        "你是房地产": json.dumps({
            "summary": "本周发布10条内容，总曝光5000",
            "metrics": {
                "total_posts": 10,
                "total_views": 5000,
                "total_interactions": 200,
                "avg_views_per_post": 500,
                "avg_interaction_rate": 0.04,
                "best_platform": "xiaohongshu",
                "best_content_type": "note",
            },
            "trends": [{"dimension": "平台", "finding": "小红书效果最佳", "evidence": "曝光占比60%"}],
            "insights": [{"type": "success", "content": "探房类内容最受欢迎", "impact": "高"}],
            "content_analysis": {"best_performers": [], "improvement_areas": []},
            "recommendations": [{"priority": "高", "action": "增加探房内容", "expected_impact": "提升曝光"}],
            "weekly_plan": {
                "monday": {"theme": "探房", "platform": "xiaohongshu", "content_type": "note"},
                "tuesday": {"theme": "政策解读", "platform": "douyin", "content_type": "script"},
            },
        }),
    }
    
    agent = ReviewAnalysisAgent(model_router=mock_router)
    agent.set_context_bus(ContextBus())
    
    result = await agent.execute({
        "publish_records": [
            {"title": "笔记1", "views": 1000, "likes": 50, "comments": 10},
        ],
        "engagement_data": {"total_views": 1000},
    })
    
    assert result.success == True
    data = json.loads(result.content)
    assert "summary" in data
    assert "metrics" in data


async def _test_policy_converter_execute():
    """测试 PolicyConverterAgent 执行（需要模型）"""
    from agent.policy_converter_agent import PolicyConverterAgent
    
    mock_router = MockModelRouter()
    mock_router.response_map = {
        "你是房地产": json.dumps({
            "policy_info": {
                "title": "公积金贷款新政",
                "source": "公积金管理中心",
                "publish_date": "2025-01-01",
                "category": "housing_fund",
            },
            "plain_explanation": "公积金贷款额度提高了",
            "detailed_explanation": "新政将公积金贷款额度从80万提高到100万",
            "impact_analysis": [
                {"group": "购房者", "impact": "贷款额度提高", "severity": "高"},
            ],
            "output_plans": [
                {
                    "id": 1,
                    "platform": "xiaohongshu",
                    "content_type": "note",
                    "title": "公积金新政解读",
                    "key_points": ["额度提高"],
                    "compliance_notes": ["以官方为准"],
                }
            ],
            "action_guide": ["查看新政详情"],
            "references": {},
        }),
    }
    
    agent = PolicyConverterAgent(model_router=mock_router)
    agent.set_context_bus(ContextBus())
    
    result = await agent.execute({
        "policy_text": "公积金贷款额度调整至100万",
        "policy_title": "公积金贷款新政",
        "target_audience": "buyer",
    })
    
    assert result.success == True
    data = json.loads(result.content)
    assert "plain_explanation" in data
    assert "impact_analysis" in data


async def _test_compliance_officer_execute():
    """测试 ComplianceOfficerAgent 执行（需要模型）"""
    from agent.compliance_officer import ComplianceOfficerAgent
    from compliance.rule_engine import ComplianceRuleEngine
    
    mock_router = MockModelRouter()
    mock_router.response_map = {
        "你是合规修改": json.dumps({
            "modification_suggestions": [
                {"original": "升值潜力大", "suggested": "有保值空间", "reason": "避免承诺升值"},
            ],
            "ai_detection_avoidance": [
                {"technique": "句式多样化", "example": "避免重复"},
            ],
        }),
    }
    
    agent = ComplianceOfficerAgent(
        model_router=mock_router,
        compliance_engine=ComplianceRuleEngine(),
    )
    agent.set_context_bus(ContextBus())
    
    result = await agent.execute({
        "text": "这个小区升值潜力大，是最好的一号楼，国家级标准",
        "platform": "xiaohongshu",
        "content_type": "note",
    })
    
    assert result.success == True
    data = json.loads(result.content)
    assert "status" in data
    assert "compliance_score" in data
    assert "layer1_results" in data
    assert "layer2_results" in data


def test_all_agents_import():
    """测试所有 Agent 导入"""
    from agent.coordinator import ContentCoordinatorAgent
    from agent.property_analyst import PropertyAnalystAgent
    from agent.xiaohongshu_writer import XiaohongshuWriterAgent
    from agent.video_director import VideoDirectorAgent
    from agent.district_researcher import DistrictResearcherAgent
    from agent.lead_converter import LeadConverterAgent
    from agent.review_analysis import ReviewAnalysisAgent
    from agent.policy_converter_agent import PolicyConverterAgent
    from agent.compliance_officer import ComplianceOfficerAgent
    
    agents = [
        ContentCoordinatorAgent,
        PropertyAnalystAgent,
        XiaohongshuWriterAgent,
        VideoDirectorAgent,
        DistrictResearcherAgent,
        LeadConverterAgent,
        ReviewAnalysisAgent,
        PolicyConverterAgent,
        ComplianceOfficerAgent,
    ]
    
    assert len(agents) == 9
    print(f"✅ 全部 9 个 Agent 导入成功")


if __name__ == "__main__":
    # 运行同步测试
    test_agent_base()
    test_agent_result()
    test_context_bus()
    test_lead_converter_import()
    test_review_analysis_import()
    test_policy_converter_agent_import()
    test_compliance_officer_import()
    test_all_agents_import()
    
    # 运行异步测试
    asyncio.run(_test_lead_converter_execute())
    asyncio.run(_test_review_analysis_execute())
    asyncio.run(_test_policy_converter_execute())
    asyncio.run(_test_compliance_officer_execute())
    
    print("\n🎉 所有测试通过！")
