import streamlit as st
from langchain_community.llms.tongyi import Tongyi
from langchain_core.language_models.llms import BaseLLM

from llms.model import ModelConfig, LLMFactory

default_tongyi_config = ModelConfig(
  name = "qwen-max",
  api_key = st.secrets["DASHSCOPE_API_KEY"],
  top_p = 0.8,
  stream = False
)

omni_tongyi_config = ModelConfig(
  name = "qwen-omni-turbo",
  api_key = st.secrets["DASHSCOPE_API_KEY"],
  top_p = 0.8,
  stream = False
)

class TongyiFactory(LLMFactory):
  """
  这是通义千问的工厂类
  实际上这部分的工作量相当有限，主要在于根据`url`自定义的部分
  """
  def __init__(self, config: ModelConfig = default_tongyi_config):
    self.config = config
  def create(self) -> BaseLLM:
    assert (
      self.config.name is not None and self.config.name != ""
    ), "name is required"
    assert self.config.api_key is not None, "api_key is required"
    return Tongyi(
      model = self.config.name, top_p = self.config.top_p, api_key = self.config.api_key,
      streaming = self.config.stream
    )

__all__ = ["TongyiFactory", "default_tongyi_config", "omni_tongyi_config"]

if __name__ == "__main__":
  llm = TongyiFactory(default_tongyi_config).create()
  print(llm.invoke("你好"))