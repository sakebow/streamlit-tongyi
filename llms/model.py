import streamlit as st
from pydantic import BaseModel, Field

from langchain_openai.chat_models.base import ChatOpenAI

class ModelConfig(BaseModel):
  """
  初始化大模型配置
  name: str = Field(..., description="模型名称")
  api_key: str = Field(..., description="API Key")
  max_tokens: int = Field(32768, ge = 1, description="最大输出长度")
  temperature: float = Field(0.7, ge = 0.0, le = 1.0, description="结果分布参数")
  top_p: float = Field(0.8, ge = 0.0, le = 1.0, description="采样参数, 取值范围为[0, 1]")
  n: int = Field(1, ge = 1, description="输出结果数量")
  presence_penalty: float = Field(0.9, ge = 0.0, le = 1.0, description="重复惩罚参数")
  frequency_penalty: float = Field(0.9, ge = 0.0, le = 1.0, description="频率惩罚参数")
  stream: bool = Field(False, description="是否流式输出")
  """
  name: str = Field(..., description="模型名称")
  api_key: str = Field(..., description="API Key")
  max_tokens: int = Field(32768, ge = 1, description="最大输出长度")
  temperature: float = Field(0.7, ge = 0.0, le = 1.0, description="结果分布参数")
  top_p: float = Field(0.8, ge = 0.0, le = 1.0, description="采样参数, 取值范围为[0, 1]")
  n: int = Field(1, ge = 1, description="输出结果数量")
  presence_penalty: float = Field(0.9, ge = 0.0, le = 1.0, description="重复惩罚参数")
  frequency_penalty: float = Field(0.9, ge = 0.0, le = 1.0, description="频率惩罚参数")
  stream: bool = Field(False, description="是否流式输出")

basic_qwen_model_config: ModelConfig = ModelConfig(
  name = "qwen-max",
  api_key=st.secrets["DASHSCOPE_API_KEY"]
)

onmi_qwen_model_config: ModelConfig = ModelConfig(
  name = "qwen-omni-turbo",
  api_key=st.secrets["DASHSCOPE_API_KEY"]
)

basic_cmdi_model_config: ModelConfig = ModelConfig(
  name = "DeepSeek-R1-Distill-Qwen-32B",
  api_key=st.secrets["APPCODE_KEY"]
)

class AgentFactory(BaseModel):
  """
  大模型工厂，用于创建大模型对象
  """
  base_url: str = Field(..., description="API Base URL")
  config: ModelConfig = Field(..., description="模型配置")
  llm: ChatOpenAI = Field(None, description="大模型对象")
  def agent(self) -> ChatOpenAI:
    """子类必须实现"""
    raise NotImplementedError