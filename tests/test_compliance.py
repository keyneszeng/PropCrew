"""
合规引擎单元测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compliance.rule_engine import ComplianceRuleEngine
from knowledge.banned_words import BannedWords


def test_banned_words():
    """测试违禁词库"""
    banned = BannedWords()
    words = banned.get_all_words()
    
    assert len(words) > 0, "违禁词库不能为空"
    assert "absolute_terms" in words, "缺少绝对化用语分类"
    assert "investment_promises" in words, "缺少投资承诺分类"
    
    print("✅ 违禁词库测试通过")


def test_compliance_engine():
    """测试合规引擎"""
    engine = ComplianceRuleEngine()
    
    # 测试合规内容
    result = engine.check("这套房子南北通透，采光很好，适合家庭居住。")
    assert result.is_compliant, "合规内容应通过检查"
    
    # 测试绝对化用语
    result = engine.check("这是最好的房子，第一选择！")
    assert not result.is_compliant, "绝对化用语应被拦截"
    assert any(v.get("word") == "最" for v in result.violations), "应检测到'最'"
    
    # 测试投资承诺
    result = engine.check("投资首选，升值潜力巨大！")
    assert not result.is_compliant, "投资承诺应被拦截"
    assert any(v.get("word") == "升值" for v in result.violations), "应检测到'升值'"
    
    print("✅ 合规引擎测试通过")


def test_risk_level():
    """测试风险等级评估"""
    engine = ComplianceRuleEngine()
    
    # 低风险
    result = engine.check("这套房子不错。")
    assert result.risk_level == "low", f"低风险内容应为 low，实际为 {result.risk_level}"
    
    # 高风险
    result = engine.check("最好的房子，升值潜力巨大，稳赚不赔！")
    assert result.risk_level == "high", f"高风险内容应为 high，实际为 {result.risk_level}"
    
    print("✅ 风险等级测试通过")


if __name__ == "__main__":
    test_banned_words()
    test_compliance_engine()
    test_risk_level()
    print("\n🎉 所有合规测试通过！")
