"""
Context Bus - 共享上下文总线

所有 Agent 通过 Context Bus 共享和交换上下文信息。
支持上下文持久化、版本管理和跨 Agent 通信。
"""

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import threading

logger = logging.getLogger(__name__)


@dataclass
class ContextEntry:
    """上下文条目"""
    key: str
    value: Any
    agent_id: str
    timestamp: str
    version: int = 1


class ContextBus:
    """
    共享上下文总线
    
    功能：
    1. 存储和检索共享上下文
    2. 支持版本管理
    3. 支持上下文持久化
    4. 线程安全
    """

    def __init__(self):
        self._context: Dict[str, ContextEntry] = {}
        self._history: List[ContextEntry] = []
        self._lock = threading.RLock()
        self._version = 0

    def set_context(self, key: str, value: Any, agent_id: str = "system") -> None:
        """设置上下文"""
        with self._lock:
            self._version += 1
            entry = ContextEntry(
                key=key,
                value=value,
                agent_id=agent_id,
                timestamp=datetime.now().isoformat(),
                version=self._version,
            )
            self._context[key] = entry
            self._history.append(entry)
            logger.debug(f"[ContextBus] SET {key} by {agent_id} (v{self._version})")

    def get_context(self, key: Optional[str] = None) -> Any:
        """获取上下文"""
        with self._lock:
            if key is None:
                return {k: v.value for k, v in self._context.items()}
            entry = self._context.get(key)
            return entry.value if entry else None

    def update_context(self, updates: Dict[str, Any], agent_id: str = "system") -> None:
        """批量更新上下文"""
        with self._lock:
            for key, value in updates.items():
                self.set_context(key, value, agent_id)

    def delete_context(self, key: str) -> bool:
        """删除上下文"""
        with self._lock:
            if key in self._context:
                del self._context[key]
                self._version += 1
                logger.debug(f"[ContextBus] DELETE {key}")
                return True
            return False

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取上下文变更历史"""
        with self._lock:
            return [
                {
                    "key": entry.key,
                    "value": entry.value,
                    "agent_id": entry.agent_id,
                    "timestamp": entry.timestamp,
                    "version": entry.version,
                }
                for entry in self._history[-limit:]
            ]

    def get_version(self) -> int:
        """获取当前版本号"""
        return self._version

    def snapshot(self) -> Dict[str, Any]:
        """创建上下文快照"""
        with self._lock:
            return {
                "version": self._version,
                "timestamp": datetime.now().isoformat(),
                "context": {k: v.value for k, v in self._context.items()},
            }

    def restore(self, snapshot: Dict[str, Any]) -> None:
        """从快照恢复上下文"""
        with self._lock:
            self._context.clear()
            self._version = snapshot.get("version", 0)
            for key, value in snapshot.get("context", {}).items():
                self._context[key] = ContextEntry(
                    key=key,
                    value=value,
                    agent_id="restore",
                    timestamp=snapshot.get("timestamp", datetime.now().isoformat()),
                    version=self._version,
                )
            logger.info(f"[ContextBus] Restored from snapshot v{self._version}")

    def clear(self) -> None:
        """清空所有上下文"""
        with self._lock:
            self._context.clear()
            self._history.clear()
            self._version = 0
            logger.info("[ContextBus] Cleared")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）"""
        return self.snapshot()

    def from_dict(self, data: Dict[str, Any]) -> None:
        """从字典恢复（用于反序列化）"""
        self.restore(data)
