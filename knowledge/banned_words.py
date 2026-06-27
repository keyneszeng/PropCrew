"""
违禁词表 - 房地产广告法合规

包含房地产广告法禁止使用的词汇和表达。
参考《广告法》《房地产广告发布规定》等法规。
"""

from typing import List, Dict, Set
import json
import os
from pathlib import Path

# 违禁词分类
BANNED_CATEGORIES = {
    "absolute_terms": "绝对化用语",  # 最、第一、唯一、顶级等
    "investment_promises": "投资承诺",  # 升值、回报、稳赚等
    "location_exaggeration": "区位夸大",  # 市中心、CBD、学区房等
    "quality_exaggeration": "品质夸大",  # 豪宅、顶级、奢华等
    "legal_risks": "法律风险",  # 不限购、可落户、可贷款等
    "misleading_info": "误导信息",  # 距离、配套、交通等
}


class BannedWords:
    """违禁词管理器"""

    def __init__(self):
        self._words: Dict[str, Set[str]] = {
            category: set() for category in BANNED_CATEGORIES.keys()
        }
        self._patterns: List[str] = []  # 正则模式
        self._load_default_words()

    def _load_default_words(self):
        """加载默认违禁词库"""
        # 绝对化用语
        self._words["absolute_terms"] = {
            "最", "第一", "唯一", "顶级", "极致", "完美", "绝对",
            "最好", "最佳", "最优", "最高", "最低", "最快", "最新",
            "首选", "唯一选择", "不二之选", "绝无仅有", "独一无二",
            "国家级", "世界級", "国际级", "领袖", "霸主",
        }

        # 投资承诺
        self._words["investment_promises"] = {
            "升值", "增值", "回报", "收益", "稳赚", "暴利",
            "投资首选", "投资热点", "升值潜力", "财富增值",
            "年化收益", "保本", "无风险", "高回报", "快速回本",
        }

        # 区位夸大
        self._words["location_exaggeration"] = {
            "市中心", "CBD", "核心区", "黄金地段", "绝版地段",
            "学区房", "名校旁", "重点学校", "名校学位",
            "地铁房", "地铁上盖", "零距离", "步行可达",
        }

        # 品质夸大
        self._words["quality_exaggeration"] = {
            "豪宅", "顶级豪宅", "奢华", "尊贵", "皇室",
            "宫殿", "别墅区", "高端社区", "精英社区",
            "五星", "豪华装修", "精装交付",
        }

        # 法律风险
        self._words["legal_risks"] = {
            "不限购", "可落户", "可贷款", "零首付",
            "包过户", "包办证", "包交房", "包入住",
            "内部认购", "VIP认购", "认筹", "定金不退",
        }

        # 误导信息
        self._words["misleading_info"] = {
            "距离", "公里", "分钟", "步行", "车程",
            "配套", "商场", "医院", "学校", "公园",
            # 注意：这些词本身不违规，但需要避免虚假宣传
        }

        # 正则模式（用于更灵活的匹配）
        self._patterns = [
            r"(\d+)%.*?(回报|收益|升值)",  # 百分比+投资承诺
            r"首付(\d+)万",                # 首付xx万起
            r"(\d+)万.*?(首付|总价|单价)",  # 数字+万+价格词
            r"(\d+)分钟.*?(地铁|学校|商场)", # 时间承诺
            r"回报率.*?\d+%",              # 回报率具体数字
            r"年化.*?\d+%",                # 年化收益率
            r"(地铁|学校|商场).*?(\d+)米",  # 距离承诺
        ]

    def add_word(self, category: str, word: str) -> None:
        """添加违禁词"""
        if category not in self._words:
            self._words[category] = set()
        self._words[category].add(word)

    def remove_word(self, category: str, word: str) -> bool:
        """移除违禁词"""
        if category in self._words and word in self._words[category]:
            self._words[category].remove(word)
            return True
        return False

    def check(self, text: str) -> Dict[str, List[str]]:
        """
        检查文本中的违禁词
        
        Returns:
            {category: [words]} 发现的违禁词
        """
        violations = {}
        
        for category, words in self._words.items():
            found = []
            for word in words:
                if word in text:
                    found.append(word)
            if found:
                violations[category] = found
        
        return violations

    def check_with_patterns(self, text: str) -> List[str]:
        """使用正则模式检查"""
        import re
        matches = []
        for pattern in self._patterns:
            found = re.findall(pattern, text)
            matches.extend(found)
        return matches

    def get_all_words(self) -> Dict[str, List[str]]:
        """获取所有违禁词"""
        return {k: list(v) for k, v in self._words.items()}

    def get_word_count(self) -> int:
        """获取违禁词总数"""
        return sum(len(words) for words in self._words.values())

    def save_to_file(self, filepath: str) -> None:
        """保存到文件"""
        data = {
            "categories": BANNED_CATEGORIES,
            "words": self.get_all_words(),
            "patterns": self._patterns,
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self, filepath: str) -> None:
        """从文件加载"""
        if not os.path.exists(filepath):
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._words = {k: set(v) for k, v in data.get("words", {}).items()}
        self._patterns = data.get("patterns", [])
