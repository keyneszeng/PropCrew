"""
环境配置

集中管理所有配置项，支持环境变量覆盖。
"""

import os
from typing import Optional
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Settings:
    """应用配置"""

    # 应用基本信息
    APP_NAME: str = "房地产销售 Agent 智能体"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./real_estate_agent.db")

    # LLM 配置
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "deepseek-v3")
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    MODEL_TEMPERATURE: float = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
    MODEL_MAX_TOKENS: int = int(os.getenv("MODEL_MAX_TOKENS", "2000"))
    MODEL_TIMEOUT: int = int(os.getenv("MODEL_TIMEOUT", "60"))

    # 合规配置
    COMPLIANCE_ENABLED: bool = os.getenv("COMPLIANCE_ENABLED", "True").lower() == "true"
    BANNED_WORDS_FILE: str = os.getenv("BANNED_WORDS_FILE", "./config/banned_words.json")

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Streamlit 配置
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    STREAMLIT_HOST: str = os.getenv("STREAMLIT_HOST", "0.0.0.0")

    @classmethod
    def get_model_config(cls, model_name: str = None) -> dict:
        """获取模型配置"""
        model = model_name or cls.DEFAULT_MODEL
        
        if model == "deepseek-v3":
            return {
                "provider": "deepseek",
                "model_name": "deepseek-chat",
                "api_key": cls.DEEPSEEK_API_KEY,
                "temperature": cls.MODEL_TEMPERATURE,
                "max_tokens": cls.MODEL_MAX_TOKENS,
                "timeout": cls.MODEL_TIMEOUT,
            }
        elif model == "gpt-4o":
            return {
                "provider": "openai",
                "model_name": "gpt-4o",
                "api_key": cls.OPENAI_API_KEY,
                "temperature": cls.MODEL_TEMPERATURE,
                "max_tokens": cls.MODEL_MAX_TOKENS,
                "timeout": cls.MODEL_TIMEOUT,
            }
        else:
            raise ValueError(f"Unknown model: {model}")


# 全局配置实例
settings = Settings()
