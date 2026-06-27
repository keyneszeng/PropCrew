"""
Model Router - 多模型路由

支持多个 LLM 提供商的动态路由和负载均衡。
当前支持：DeepSeek V3, GPT-4o, Claude
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import os

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """模型配置"""
    provider: str  # deepseek, openai, claude
    model_name: str
    api_key: str
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60
    enabled: bool = True


class BaseLLMClient(ABC):
    """LLM 客户端基类"""

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        pass

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        pass


class DeepSeekClient(BaseLLMClient):
    """DeepSeek V3 客户端"""

    def __init__(self, config: ModelConfig):
        self.config = config
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(
                    api_key=self.config.api_key,
                    base_url=self.config.base_url or "https://api.deepseek.com",
                    timeout=self.config.timeout,
                )
            except ImportError:
                logger.error("openai package not installed")
                raise
        return self._client

    async def chat(self, messages, temperature=0.7, max_tokens=2000) -> str:
        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    async def stream_chat(self, messages, temperature=0.7, max_tokens=2000):
        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class OpenAIClient(BaseLLMClient):
    """OpenAI GPT-4o 客户端"""

    def __init__(self, config: ModelConfig):
        self.config = config
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(
                    api_key=self.config.api_key,
                    timeout=self.config.timeout,
                )
            except ImportError:
                logger.error("openai package not installed")
                raise
        return self._client

    async def chat(self, messages, temperature=0.7, max_tokens=2000) -> str:
        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    async def stream_chat(self, messages, temperature=0.7, max_tokens=2000):
        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class ModelRouter:
    """
    模型路由器
    
    功能：
    1. 多模型注册和选择
    2. 负载均衡
    3. 故障转移
    4. 成本优化
    """

    def __init__(self):
        self._clients: Dict[str, BaseLLMClient] = {}
        self._configs: Dict[str, ModelConfig] = {}
        self._default_model = "deepseek-v3"

    def register_model(self, config: ModelConfig) -> None:
        """注册模型"""
        key = f"{config.provider}:{config.model_name}"
        
        if config.provider == "deepseek":
            client = DeepSeekClient(config)
        elif config.provider == "openai":
            client = OpenAIClient(config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
        
        self._clients[key] = client
        self._configs[key] = config
        logger.info(f"[ModelRouter] Registered model: {key}")

    def get_client(self, model_key: Optional[str] = None) -> BaseLLMClient:
        """获取模型客户端"""
        key = model_key or self._default_model
        if key not in self._clients:
            raise ValueError(f"Model not registered: {key}")
        return self._clients[key]

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """发送聊天请求"""
        client = self.get_client(model_key)
        return await client.chat(messages, temperature, max_tokens)

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """流式聊天"""
        client = self.get_client(model_key)
        async for chunk in client.stream_chat(messages, temperature, max_tokens):
            yield chunk

    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return list(self._clients.keys())

    def get_model_info(self, model_key: str) -> Optional[ModelConfig]:
        """获取模型信息"""
        return self._configs.get(model_key)

    def set_default_model(self, model_key: str) -> None:
        """设置默认模型"""
        if model_key in self._clients:
            self._default_model = model_key
            logger.info(f"[ModelRouter] Default model set to: {model_key}")
        else:
            raise ValueError(f"Model not registered: {model_key}")
