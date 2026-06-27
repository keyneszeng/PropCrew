"""
Agent 日志系统

统一日志管理，支持结构化日志、日志级别控制和文件轮转。
"""

import logging
import json
import os
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, Optional
from enum import Enum
from datetime import datetime


class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class AgentLogger:
    """
    Agent 日志管理器
    
    功能：
    1. 统一日志格式和级别
    2. 支持结构化日志（JSON）
    3. 日志文件轮转
    4. 支持上下文追踪（task_id, agent_id）
    """

    def __init__(
        self,
        name: str = "real_estate_agent",
        log_dir: str = "logs",
        level: LogLevel = LogLevel.INFO,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ):
        self.name = name
        self.log_dir = log_dir
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level.value)
        self._logger.handlers.clear()

        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)

        # 文件日志（轮转）
        file_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, f"{name}.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(level.value)
        file_handler.setFormatter(self._get_formatter())
        self._logger.addHandler(file_handler)

        # 控制台日志
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level.value)
        console_handler.setFormatter(self._get_formatter(use_color=True))
        self._logger.addHandler(console_handler)

    def _get_formatter(self, use_color: bool = False) -> logging.Formatter:
        """获取格式化器"""
        fmt = "%(asctime)s | %(levelname)-8s | %(message)s"
        if use_color:
            fmt = "%(asctime)s | %(levelname)-8s | %(message)s"
        return logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    def _log(self, level: LogLevel, message: str, **context):
        """结构化日志"""
        extra = {
            "timestamp": datetime.now().isoformat(),
            "logger": self.name,
        }
        extra.update(context)
        
        log_entry = {
            "message": message,
            "context": extra,
        }
        
        self._logger.log(level.value, json.dumps(log_entry, ensure_ascii=False))

    def info(self, message: str, **context):
        self._log(LogLevel.INFO, message, **context)

    def debug(self, message: str, **context):
        self._log(LogLevel.DEBUG, message, **context)

    def warning(self, message: str, **context):
        self._log(LogLevel.WARNING, message, **context)

    def error(self, message: str, exc_info=None, **context):
        self._log(LogLevel.ERROR, message, **context)
        if exc_info:
            self._logger.exception(message)

    def critical(self, message: str, **context):
        self._log(LogLevel.CRITICAL, message, **context)
