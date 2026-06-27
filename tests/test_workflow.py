"""
端到端测试

测试完整的工作流：内容总监 → 卖点分析师 → 小红书文案 → 合规检查
"""

import asyncio
import json
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.context_bus import ContextBus
from core.task_manager import TaskManager, TaskPriority
from core.model_router import ModelRouter, ModelConfig
from agent.coordinator import ContentCoordinatorAgent
from agent.property_analyst import PropertyAnalystAgent
from agent.xiaohongshu_writer import XiaohongshuWriterAgent
from compliance.rule_engine import ComplianceRuleEngine
from knowledge.banned_words import BannedWords


async def test_full_workflow():
    """测试完整工作流"""
    print("=" * 60)
    print("🧪 端到端测试：房地产内容生成工作流")
    print("=" * 60)
    
    # 初始化组件
    context_bus = ContextBus()
    task_manager = TaskManager()
    model_router = ModelRouter()
    
    # 注册模型（使用 DeepSeek 作为示例）
    # 注意：实际使用时需要替换为真实的 API Key
    config = ModelConfig(
        provider="deepseek",
        model_name="deepseek-chat",
        api_key="sk-test-key",  # 测试用，实际使用时替换
    )
    model_router.register_model(config)
    
    # 初始化 Agent
    coordinator = ContentCoordinatorAgent(model_router=model_router)
    coordinator.set_context_bus(context_bus)
    
    analyst = PropertyAnalystAgent(model_router=model_router)
    analyst.set_context_bus(context_bus)
    
    writer = XiaohongshuWriterAgent(model_router=model_router)
    writer.set_context_bus(context_bus)
    
    # 注册 Agent
    task_manager.register_agent(coordinator.agent_id, coordinator)
    task_manager.register_agent(analyst.agent_id, analyst)
    task_manager.register_agent(writer.agent_id, writer)
    
    # 初始化合规引擎
    compliance_engine = ComplianceRuleEngine()
    
    # 测试数据
    test_property = """
    地址：北京市朝阳区望京SOHO
    户型：3室2厅2卫
    面积：120平米
    价格：800万
    特色：南北通透，精装修，学区房，地铁15号线望京南站
    """
    
    print("\n📋 测试数据：")
    print(test_property)
    
    # 步骤 1: 内容总监分析
    print("\n📋 步骤 1: 内容总监分析需求...")
    try:
        coordinator_result = await coordinator.execute({
            "user_request": f"帮我写一条小红书探房笔记：{test_property}",
            "property_info": test_property,
        })
        print(f"✅ 内容总监完成，任务类型：{coordinator_result.metadata.get('task_type', 'unknown')}")
    except Exception as e:
        print(f"❌ 内容总监失败：{e}")
        return False
    
    # 步骤 2: 卖点分析师
    print("\n🔍 步骤 2: 卖点分析师提取卖点...")
    try:
        analyst_result = await analyst.execute({
            "property_info": test_property,
        })
        print(f"✅ 卖点分析师完成，提取卖点数：{len(json.loads(analyst_result.content).get('selling_points', []))}")
    except Exception as e:
        print(f"❌ 卖点分析师失败：{e}")
        return False
    
    # 步骤 3: 小红书文案
    print("\n✍️ 步骤 3: 小红书文案创作...")
    try:
        writer_result = await writer.execute({
            "property_info": test_property,
            "selling_points": json.loads(analyst_result.content).get("selling_points", []),
        })
        note = json.loads(writer_result.content)
        print(f"✅ 小红书文案完成，标题：{note.get('title', 'N/A')}")
        print(f"   字数：{note.get('word_count', len(note.get('content', '')))}")
        print(f"   标签：{', '.join(note.get('tags', []))}")
    except Exception as e:
        print(f"❌ 小红书文案失败：{e}")
        return False
    
    # 步骤 4: 合规检查
    print("\n🔍 步骤 4: 合规检查...")
    full_text = f"{note.get('title', '')} {note.get('content', '')}"
    compliance_result = compliance_engine.check(full_text)
    
    if compliance_result.is_compliant:
        print("✅ 内容合规，可以发布")
    else:
        print(f"⚠️ 发现 {len(compliance_result.violations)} 个潜在问题")
        for violation in compliance_result.violations[:3]:
            print(f"   - {violation.get('word', violation.get('match', ''))}: {violation.get('suggestion', '')}")
    
    # 输出最终结果
    print("\n" + "=" * 60)
    print("📝 最终生成的小红书笔记：")
    print("=" * 60)
    print(f"\n标题：{note.get('title', '')}")
    print(f"\n正文：\n{note.get('content', '')}")
    print(f"\n标签：{' '.join(['#' + tag for tag in note.get('tags', [])])}")
    
    print("\n" + "=" * 60)
    print("✅ 端到端测试完成！")
    print("=" * 60)
    
    return True


async def test_compliance_engine():
    """测试合规引擎"""
    print("\n" + "=" * 60)
    print("🧪 合规引擎测试")
    print("=" * 60)
    
    compliance_engine = ComplianceRuleEngine()
    
    # 测试用例
    test_cases = [
        {
            "name": "合规内容",
            "text": "这套房子南北通透，采光很好，适合家庭居住。",
            "expected_compliant": True,
        },
        {
            "name": "绝对化用语",
            "text": "这是最好的房子，第一选择，唯一的机会！",
            "expected_compliant": False,
        },
        {
            "name": "投资承诺",
            "text": "投资首选，升值潜力巨大，稳赚不赔！",
            "expected_compliant": False,
        },
        {
            "name": "学区误导",
            "text": "学区房，对口名校，保证入学！",
            "expected_compliant": False,
        },
    ]
    
    for case in test_cases:
        print(f"\n📝 测试用例：{case['name']}")
        print(f"   内容：{case['text']}")
        
        result = compliance_engine.check(case['text'])
        print(f"   合规：{'✅' if result.is_compliant else '❌'}")
        print(f"   风险等级：{result.risk_level}")
        
        if not result.is_compliant:
            print(f"   违规数：{len(result.violations)}")
            for violation in result.violations[:2]:
                print(f"   - {violation.get('word', violation.get('match', ''))}")
        
        # 验证预期
        if result.is_compliant == case['expected_compliant']:
            print("   ✅ 测试通过")
        else:
            print("   ❌ 测试失败")
    
    print("\n" + "=" * 60)
    print("✅ 合规引擎测试完成！")
    print("=" * 60)


async def main():
    """主测试函数"""
    try:
        # 运行工作流测试
        workflow_success = await test_full_workflow()
        
        # 运行合规引擎测试
        await test_compliance_engine()
        
        if workflow_success:
            print("\n🎉 所有测试通过！")
            return 0
        else:
            print("\n❌ 部分测试失败")
            return 1
            
    except Exception as e:
        print(f"\n❌ 测试异常：{e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
