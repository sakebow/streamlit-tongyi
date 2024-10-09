import os
import streamlit as st

from abc import ABC, abstractmethod

class LLMFactory(ABC):
  """
  LLM虚拟工厂
  """
  @abstractmethod
  def build(self):
    ...

class TongyiFactory(LLMFactory):
  """
  通义千问LLM工厂，需要 $3$ 个参数：api_key, model_name, top_p
  """
  def __init__(self, api_key: str = st.secrets["DASHSCOPE_API_KEY"], model_name: str = "qwen-max", top_p: float = 0.7):
    self.api_key = api_key
    self.model_name = model_name
    self.top_p = top_p

  def build(self):
    from langchain_community.llms import Tongyi
    llm = Tongyi(model = self.model_name, top_p = self.top_p, api_key = self.api_key)
    return llm

class OpenAIFactory(LLMFactory):
  """
  OpenAILLM工厂，需要 $2$ 个参数：api_key, model_name
  """
  def __init__(self, api_key: str = st.secrets["OPENAI_API_KEY"], model_name: str = "gpt-3.5-turbo-instruct"):
    self.api_key = api_key
    self.model_name = model_name

  def build(self):
    from langchain.llms import OpenAI
    os.environ["OPENAI_API_KEY"] = self.api_key
    llm = OpenAI(model_name=self.model_name)
    return llm

# 工厂方法，根据 llm_type 返回对应的 LLMFactory
def get_llm_factory(llm_type: str, **kwargs) -> LLMFactory:
  if llm_type == "tongyi":
    return TongyiFactory(**kwargs).build()
  elif llm_type == "openai":
    return OpenAIFactory(**kwargs).build()
  else:
    raise ValueError(f"Unsupported LLM type: {llm_type}")