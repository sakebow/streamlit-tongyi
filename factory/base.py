from httpx import Client
from threading import Lock
from pydantic import BaseModel, Field
from typing import ClassVar, Optional, List, Any

from langchain_openai.chat_models.base import ChatOpenAI

class BaseFactory(BaseModel):
    base_url: str = Field(..., description = "API Base URL, NonNullable")
    api_key : str = Field(..., description = "API Key, NonNullable")
    timeout: float = Field(60.0, description="API Timeout (seconds)")

    # ---------- 单例相关 ----------
    _instance: ClassVar[Optional[BaseModel]] = None
    _instance_lock: ClassVar[Lock] = Lock()
    
    # ===== 单例入口 =====
    @classmethod
    def get_instance(cls, **kwargs) -> BaseModel:
        """双重检查锁的线程安全单例"""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls(**kwargs)
        return cls._instance

class BaseLLMFactory(BaseFactory):
    def build(
        self, model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        client: Client = None
    ) -> ChatOpenAI:
        return ChatOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            http_client=client
        )

class BaseEmbeddingFactory(BaseFactory):
    def embeddings(self, *args, **kwargs) -> List[float]:
        """
        embedding text into vector
        well, maybe not so important for now...
        """
    def rerank(self, *args, **kwargs) -> List[Any]:
        """
        rerank documents
        it has to be implemented
        """
        raise NotImplementedError