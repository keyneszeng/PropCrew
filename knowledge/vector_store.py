"""
向量存储 - ChromaDB 集成

用于知识库的语义搜索和相似性匹配。
Phase 2 功能，支持房源、小区、政策、模板的向量检索。
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """向量文档"""
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class VectorStore:
    """
    向量存储
    
    功能：
    1. 文档向量化存储
    2. 语义相似性搜索
    3. 多集合管理
    4. 支持 ChromaDB 和内存模式
    """

    def __init__(
        self,
        collection_name: str = "default",
        persist_dir: Optional[str] = None,
        embedding_function: Optional[Any] = None,
    ):
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.embedding_function = embedding_function
        self._documents: Dict[str, VectorDocument] = {}
        self._initialized = False
        self._client = None
        self._collection = None

    def initialize(self):
        """初始化向量存储"""
        if self._initialized:
            return
        
        try:
            import chromadb
            from chromadb.config import Settings
            
            if self.persist_dir:
                self._client = chromadb.PersistentClient(
                    path=self.persist_dir,
                    settings=Settings(
                        anonymized_telemetry=False,
                    ),
                )
            else:
                self._client = chromadb.EphemeralClient(
                    settings=Settings(
                        anonymized_telemetry=False,
                    ),
                )
            
            # 创建或获取集合
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            
            self._initialized = True
            logger.info(f"[VectorStore] Initialized collection: {self.collection_name}")
            
        except ImportError:
            logger.warning("[VectorStore] ChromaDB not installed, using in-memory mode")
            self._use_memory_mode()

    def _use_memory_mode(self):
        """使用内存模式（ChromaDB 不可用时）"""
        self._initialized = True
        logger.info("[VectorStore] Using in-memory mode")

    def add_document(self, doc: VectorDocument) -> None:
        """添加文档"""
        if not self._initialized:
            self.initialize()
        
        if self._client:
            # ChromaDB 模式
            self._collection.add(
                ids=[doc.id],
                documents=[doc.text],
                metadatas=[doc.metadata],
                embeddings=[doc.embedding] if doc.embedding else None,
            )
            logger.debug(f"[VectorStore] Added document: {doc.id}")
        else:
            # 内存模式
            self._documents[doc.id] = doc
            logger.debug(f"[VectorStore] Added document (memory): {doc.id}")

    def add_documents(self, docs: List[VectorDocument]) -> None:
        """批量添加文档"""
        for doc in docs:
            self.add_document(doc)

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        语义搜索
        
        Args:
            query: 查询文本
            n_results: 返回结果数
            where: 过滤条件
            
        Returns:
            [(doc_id, distance, metadata), ...]
        """
        if not self._initialized:
            self.initialize()
        
        if self._client:
            # ChromaDB 模式
            results = self._collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where,
                include=["metadatas", "distances"],
            )
            
            return [
                (results["ids"][0][i], results["distances"][0][i], results["metadatas"][0][i])
                for i in range(len(results["ids"][0]))
            ]
        else:
            # 内存模式（简单关键词匹配）
            query_words = set(query.lower().split())
            scores = []
            
            for doc_id, doc in self._documents.items():
                doc_words = set(doc.text.lower().split())
                intersection = query_words & doc_words
                score = len(intersection) / len(query_words) if query_words else 0
                scores.append((doc_id, score, doc.metadata))
            
            scores.sort(key=lambda x: x[1], reverse=True)
            return scores[:n_results]

    def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """获取文档"""
        if not self._initialized:
            self.initialize()
        
        if self._client:
            results = self._collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"],
            )
            
            if results["ids"]:
                return VectorDocument(
                    id=doc_id,
                    text=results["documents"][0],
                    metadata=results["metadatas"][0],
                )
            return None
        else:
            return self._documents.get(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        if not self._initialized:
            self.initialize()
        
        if self._client:
            self._collection.delete(ids=[doc_id])
            return True
        else:
            if doc_id in self._documents:
                del self._documents[doc_id]
                return True
            return False

    def get_count(self) -> int:
        """获取文档数量"""
        if not self._initialized:
            self.initialize()
        
        if self._client:
            return self._collection.count()
        else:
            return len(self._documents)

    def clear(self) -> None:
        """清空所有文档"""
        if not self._initialized:
            self.initialize()
        
        if self._client:
            self._collection.delete(ids=self._collection.get()["ids"])
        else:
            self._documents.clear()

    def persist(self) -> None:
        """持久化（ChromaDB 自动持久化）"""
        if self._client and self.persist_dir:
            logger.info(f"[VectorStore] Persisted to {self.persist_dir}")
