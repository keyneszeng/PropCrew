"""
合规规则引擎 - Layer 1 合规检查

负责内容生成后的第一层合规检查，使用规则引擎拦截明显的违规内容。
"""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from knowledge.banned_words import BannedWords

logger = logging.getLogger(__name__)


@dataclass
class ComplianceResult:
    """合规检查结果"""
    is_compliant: bool
    violations: List[Dict[str, Any]]
    suggestions: List[str]
    risk_level: str  # low, medium, high
    checked_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_compliant": self.is_compliant,
            "violations": self.violations,
            "suggestions": self.suggestions,
            "risk_level": self.risk_level,
            "checked_at": self.checked_at,
        }


class ComplianceRuleEngine:
    """
    合规规则引擎
    
    功能：
    1. 违禁词检查
    2. 绝对化用语检查
    3. 投资承诺检查
    4. 价格误导检查
    5. 生成修改建议
    """

    def __init__(self, banned_words: Optional[BannedWords] = None):
        self.banned_words = banned_words or BannedWords()
        self._rules = self._init_rules()

    def _init_rules(self) -> Dict[str, Dict[str, Any]]:
        """初始化检查规则"""
        return {
            "banned_words": {
                "name": "违禁词检查",
                "severity": "high",
                "enabled": True,
            },
            "absolute_terms": {
                "name": "绝对化用语检查",
                "severity": "high",
                "enabled": True,
            },
            "investment_promises": {
                "name": "投资承诺检查",
                "severity": "high",
                "enabled": True,
            },
            "price_misleading": {
                "name": "价格误导检查",
                "severity": "medium",
                "enabled": True,
            },
            "location_exaggeration": {
                "name": "区位夸大检查",
                "severity": "medium",
                "enabled": True,
            },
        }

    def check(self, text: str) -> ComplianceResult:
        """
        执行合规检查
        
        Args:
            text: 待检查的文本
            
        Returns:
            ComplianceResult: 检查结果
        """
        from datetime import datetime
        
        violations = []
        suggestions = []
        
        # 1. 违禁词检查
        word_violations = self.banned_words.check(text)
        for category, words in word_violations.items():
            for word in words:
                violations.append({
                    "rule": "banned_words",
                    "category": category,
                    "word": word,
                    "severity": "high",
                    "suggestion": self._get_word_suggestion(word, category),
                })
        
        # 2. 正则模式检查
        pattern_matches = self.banned_words.check_with_patterns(text)
        for match in pattern_matches:
            violations.append({
                "rule": "pattern_match",
                "match": match,
                "severity": "medium",
                "suggestion": "避免使用具体数字承诺",
            })
        
        # 3. 绝对化用语检查
        absolute_violations = self._check_absolute_terms(text)
        violations.extend(absolute_violations)
        
        # 4. 投资承诺检查
        investment_violations = self._check_investment_promises(text)
        violations.extend(investment_violations)
        
        # 5. 价格误导检查
        price_violations = self._check_price_misleading(text)
        violations.extend(price_violations)
        
        # 6. 生成修改建议
        if violations:
            suggestions = self._generate_suggestions(violations, text)
        
        # 7. 评估风险等级
        risk_level = self._assess_risk_level(violations)
        
        return ComplianceResult(
            is_compliant=len(violations) == 0,
            violations=violations,
            suggestions=suggestions,
            risk_level=risk_level,
            checked_at=datetime.now().isoformat(),
        )

    def _check_absolute_terms(self, text: str) -> List[Dict[str, Any]]:
        """检查绝对化用语"""
        violations = []
        absolute_patterns = [
            (r"最[^\s]{1,10}", "避免使用'最'字开头"),
            (r"第一[^\s]{1,10}", "避免使用'第一'"),
            (r"唯一[^\s]{1,10}", "避免使用'唯一'"),
            (r"顶级[^\s]{1,10}", "避免使用'顶级'"),
            (r"极致[^\s]{1,10}", "避免使用'极致'"),
            (r"完美[^\s]{1,10}", "避免使用'完美'"),
        ]
        
        for pattern, suggestion in absolute_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                violations.append({
                    "rule": "absolute_terms",
                    "match": match,
                    "severity": "high",
                    "suggestion": suggestion,
                })
        
        return violations

    def _check_investment_promises(self, text: str) -> List[Dict[str, Any]]:
        """检查投资承诺"""
        violations = []
        investment_patterns = [
            (r"升值[^\s]{0,10}", "避免承诺升值"),
            (r"增值[^\s]{0,10}", "避免承诺增值"),
            (r"回报[^\s]{0,10}", "避免承诺回报"),
            (r"收益[^\s]{0,10}", "避免承诺收益"),
            (r"稳赚[^\s]{0,10}", "避免承诺稳赚"),
            (r"投资首选[^\s]{0,10}", "避免使用'投资首选'"),
        ]
        
        for pattern, suggestion in investment_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                violations.append({
                    "rule": "investment_promises",
                    "match": match,
                    "severity": "high",
                    "suggestion": suggestion,
                })
        
        return violations

    def _check_price_misleading(self, text: str) -> List[Dict[str, Any]]:
        """检查价格误导"""
        violations = []
        price_patterns = [
            (r"(\d+)[万千百].*?(首付|总价|单价)", "避免具体价格承诺"),
            (r"(\d+)%.*?(优惠|折扣|让利)", "避免具体优惠承诺"),
        ]
        
        for pattern, suggestion in price_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                violations.append({
                    "rule": "price_misleading",
                    "match": match,
                    "severity": "medium",
                    "suggestion": suggestion,
                })
        
        return violations

    def _get_word_suggestion(self, word: str, category: str) -> str:
        """获取违禁词替换建议"""
        suggestions = {
            "最": "可以用'非常'、'特别'代替",
            "第一": "可以用'领先'、'知名'代替",
            "唯一": "可以用'独特'、'特色'代替",
            "顶级": "可以用'高端'、'优质'代替",
            "升值": "可以用'潜力'、'价值'代替",
            "学区": "可以用'教育资源'、'学校配套'代替",
            "不限购": "可以用'符合购房条件'代替",
            "可落户": "可以用'满足落户要求'代替",
        }
        return suggestions.get(word, f"避免使用'{word}'")

    def _generate_suggestions(self, violations: List[Dict[str, Any]], text: str) -> List[str]:
        """生成修改建议"""
        suggestions = []
        
        for violation in violations[:5]:  # 只取前5个
            suggestion = violation.get("suggestion", "")
            if suggestion and suggestion not in suggestions:
                suggestions.append(suggestion)
        
        if not suggestions:
            suggestions.append("内容基本合规，无需修改")
        
        return suggestions

    def _assess_risk_level(self, violations: List[Dict[str, Any]]) -> str:
        """评估风险等级"""
        if not violations:
            return "low"
        
        high_count = sum(1 for v in violations if v.get("severity") == "high")
        medium_count = sum(1 for v in violations if v.get("severity") == "medium")
        
        if high_count >= 3:
            return "high"
        elif high_count >= 1 or medium_count >= 3:
            return "medium"
        else:
            return "low"

    def get_rule_info(self) -> Dict[str, Any]:
        """获取规则信息"""
        return {
            "rules": self._rules,
            "banned_word_count": self.banned_words.get_word_count(),
        }
