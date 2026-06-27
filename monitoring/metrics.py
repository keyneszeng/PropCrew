"""
性能指标收集

收集 API 调用次数、响应时间、Token 消耗等指标。
"""

import time
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict


class MetricsCollector:
    """
    性能指标收集器
    
    功能：
    1. API 调用统计（次数、耗时）
    2. Agent 调用统计
    3. Token 消耗追踪
    4. 错误率统计
    """

    def __init__(self):
        self._api_calls: List[Dict] = []
        self._agent_calls: List[Dict] = []
        self._errors: List[Dict] = []

    def record_api_call(self, endpoint: str, method: str, duration_ms: float, status_code: int, tokens_used: int = 0):
        """记录 API 调用"""
        self._api_calls.append({
            "endpoint": endpoint,
            "method": method,
            "duration_ms": duration_ms,
            "status_code": status_code,
            "tokens_used": tokens_used,
            "timestamp": datetime.now().isoformat(),
        })

    def record_agent_call(self, agent_id: str, duration_ms: float, success: bool, tokens_used: int = 0):
        """记录 Agent 调用"""
        self._agent_calls.append({
            "agent_id": agent_id,
            "duration_ms": duration_ms,
            "success": success,
            "tokens_used": tokens_used,
            "timestamp": datetime.now().isoformat(),
        })

    def record_error(self, source: str, error_type: str, message: str, details: Optional[Dict] = None):
        """记录错误"""
        self._errors.append({
            "source": source,
            "error_type": error_type,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        })

    def get_stats(self) -> Dict:
        """获取指标统计"""
        total_api = len(self._api_calls)
        total_agent = len(self._agent_calls)
        total_errors = len(self._errors)

        # API 统计
        api_avg_duration = 0
        api_errors = 0
        api_tokens = 0
        if self._api_calls:
            api_avg_duration = sum(c["duration_ms"] for c in self._api_calls) / total_api
            api_errors = sum(1 for c in self._api_calls if c["status_code"] >= 400)
            api_tokens = sum(c.get("tokens_used", 0) for c in self._api_calls)

        # Agent 统计
        agent_avg_duration = 0
        agent_errors = 0
        agent_tokens = 0
        if self._agent_calls:
            agent_avg_duration = sum(c["duration_ms"] for c in self._agent_calls) / total_agent
            agent_errors = sum(1 for c in self._agent_calls if not c["success"])
            agent_tokens = sum(c.get("tokens_used", 0) for c in self._agent_calls)

        # Agent 调用排行
        agent_ranking = defaultdict(int)
        for c in self._agent_calls:
            agent_ranking[c["agent_id"]] += 1

        return {
            "api": {
                "total_calls": total_api,
                "avg_duration_ms": round(api_avg_duration, 2),
                "errors": api_errors,
                "error_rate": f"{api_errors / max(total_api, 1) * 100:.2f}%",
                "total_tokens": api_tokens,
            },
            "agent": {
                "total_calls": total_agent,
                "avg_duration_ms": round(agent_avg_duration, 2),
                "errors": agent_errors,
                "error_rate": f"{agent_errors / max(total_agent, 1) * 100:.2f}%",
                "total_tokens": agent_tokens,
                "calls_by_agent": dict(agent_ranking),
            },
            "errors": {
                "total": total_errors,
                "by_source": dict(self._get_errors_by_source()),
            },
        }

    def _get_errors_by_source(self) -> Dict:
        """按来源统计错误"""
        by_source = defaultdict(int)
        for e in self._errors:
            by_source[e["source"]] += 1
        return by_source

    def to_json(self) -> str:
        """导出为 JSON"""
        return json.dumps(self.get_stats(), ensure_ascii=False, indent=2)
