from typing import List
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage

class MemoryBucket:
  """
  该类用于记录对话历史记录，仅用于`url`类型的`Agent`
  """
  def __init__(self, memory: BaseChatMessageHistory = None):
    if memory and memory.messages:
      self.memory: List = [{"role": message.type, "content": message.content} for message in memory.messages]
    else:
      self.memory: List = []
  def add_message(self, role: str, message: str) -> None:
    self.memory.append({"role": role, "content": message})
  def add_langchain_message(self, message: BaseMessage, role: str = None) -> None:
    """
    兼容`langchain`中的`HumanMessage`和`AIMessage`等
    """
    # `role or message.type` => `role`为`None`时，使用`message.type`
    self.add_message(role = role or message.type, message = message.content)
  def clear(self):
    self.memory.clear()
  def all(self):
    return self.memory