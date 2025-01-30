from pydantic import BaseModel, Field
from typing import List
from abc import ABC, abstractmethod

from llms.cmdi import CMDIFactory
from llms.tongyi import TongyiFactory

class ModelConfig(BaseModel):
  """
  初始化大模型配置
  name: 模型名称
  top_p: 采样参数, 取值范围为[0, 1]
  api_key: API Key
  """
  # `name`并不推荐命名为`model_name`，因为官方警告给的是：与保护命名空间`model_`冲突
  # 为了避免问题，不要定义`model_name`
  name: str = Field(..., description="模型名称")
  api_key: str = Field(..., description="API Key")
  max_tokens: int = Field(32768, ge = 1, description="最大输出长度")
  presence_penalty: float = Field(0.9, ge = 0.0, le = 1.0, description="重复惩罚参数")
  frequency_penalty: float = Field(0.9, ge = 0.0, le = 1.0, description="频率惩罚参数")
  temperature: float = Field(0.7, ge = 0.0, le = 1.0, description="结果分布参数")
  top_p: float = Field(0.8, ge = 0.0, le = 1.0, description="采样参数, 取值范围为[0, 1]")
  stream: bool = Field(False, description="是否流式输出")

class LLMFactory(ABC):
  """
  便于创建大模型实例
  """
  @abstractmethod
  def create(self):...


class MemoryBucket:
  """
  该类用于记录对话历史记录，仅用于`url`类型的`Agent`
  """
  def __init__(self):
    self.memory: List = []
  def add_message(self, role: str, message: str) -> None:
    self.memory.append({"role": role, "content": message})
  def clear(self):
    self.memory.clear()
  def all(self):
    return self.memory

__all__ = [
  "ModelConfig", "LLMFactory", "MemoryBucket",
  "CMDIFactory", "TongyiFactory"
]