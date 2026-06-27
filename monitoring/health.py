"""
系统健康检查

检查各模块运行状态，提供健康检查 API。
"""

from typing import Any, Dict, Optional
from datetime import datetime


class HealthChecker:
    """
    系统健康检查器
    
    功能：
    1. 检查各组件运行状态
    2. 检查数据库连接
    3. 检查模型路由
    4. 返回整体健康度评分
    """

    def __init__(self):
        self._components: Dict[str, bool] = {}
        self._last_check: Optional[str] = None

    def check_component(self, name: str, healthy: bool, detail: Optional[str] = None) -> Dict:
        """检查单个组件"""
        self._components[name] = healthy
        return {
            "name": name,
            "healthy": healthy,
            "detail": detail or "OK" if healthy else "FAIL",
        }

    def check_all(self, agents: Optional[Dict] = None, db=None, model_router=None) -> Dict:
        """全面健康检查"""
        self._last_check = datetime.now().isoformat()
        results = []

        # 检查 Agent
        if agents:
            agent_count = len(agents)
            agent_healthy = all(
                hasattr(a, "agent_id") for a in agents.values()
            )
            results.append(self.check_component(
                "agents", agent_healthy,
                f"{agent_count} agents registered" if agent_healthy else "agents misconfigured"
            ))

        # 检查数据库
        if db:
            try:
                session = db.get_session()
                session.execute(db.engine.dialect.statement_compiler(db.engine, None).__class__.__module__)
                session.close()
                results.append(self.check_component("database", True))
            except Exception as e:
                results.append(self.check_component("database", False, str(e)))

        # 检查模型路由
        if model_router:
            has_models = model_router.has_models()
            results.append(self.check_component(
                "model_router", has_models,
                f"models: {model_router.get_model_keys()}" if has_models else "no models registered"
            ))

        # 总体健康度
        healthy_count = sum(1 for r in results if r["healthy"])
        total = len(results)
        health_score = healthy_count / max(total, 1)

        return {
            "status": "healthy" if health_score == 1.0 else "degraded" if health_score >= 0.5 else "unhealthy",
            "health_score": round(health_score * 100),
            "timestamp": self._last_check,
            "components": results,
        }
