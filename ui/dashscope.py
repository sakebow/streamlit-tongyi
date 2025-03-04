from typing import Sequence
import pandas as pd
import streamlit as st
from pymilvus import MilvusClient
from langchain.agents.agent_types import AgentType
from langchain.agents import initialize_agent, tool
from langchain.callbacks.streamlit import StreamlitCallbackHandler
from streamlit.runtime.uploaded_file_manager import UploadedFile

from llms import TongyiFactory
from utils import RagHelper, DefaultCommonConfig, ElectricOrderItemDBManager

st.session_state.dashscope = dict()

@st.cache_resource(ttl = "1h")
def configure_retriever(uploaded_files: Sequence[UploadedFile]) -> MilvusClient:
  return RagHelper.configure_retriever(uploaded_files)

# 侧边上传文件
uploaded_files = st.sidebar.file_uploader(
  label = "上传文件", type = DefaultCommonConfig.SUPPORT_TYPES, accept_multiple_files = True
)

@tool
def search_content(user_input: str) -> str:
  """
  根据用户输入，搜索相关文件内容
  params:
    user_input: str 用户输入
    uploaded_files: Sequence[UploadedFile] 上传的文件（支持多个文件）
  return: Sequence[str] 相关文件内容
  """
  return RagHelper.search_content(user_input, uploaded_files)

edbm = ElectricOrderItemDBManager()

class BatisManager:
  def __init__(self):
    self.results = None
  @edbm.search("SELECT * FROM item_list WHERE order_year = #{order_year}")
  def search_items_by_year(self, order_year: int):
      ...

@tool
def search_db_by_year(year: int) -> any:
  """
  根据输入的年份查询数据库并返回结果
  params:
    year: int 年份
  return: any 查询结果
  """
  results = [dict(item) for item in BatisManager().search_items_by_year(year)]
  if len(results) > 25:
    pd.DataFrame(results).to_csv("upload/results.csv", encoding="utf-8", index=False, columns=[
      "id", "border_id", "contract_num", "order_depart", "proj_name",
      "item_code", "item_name", "item_num", "item_money", "item_send",
      "order_start", "item_repeat"
    ])
    return "已下载至results.csv"
  else: return results 

def write_message(role: str, message: str, save: bool = True):
  if save:
    st.session_state.dashscope["messages"].append({"role": role, "content": message})
  with st.chat_message(role):
    st.markdown(message)

st.title("阿里千问")

llm = TongyiFactory().create()
agent = initialize_agent(
  tools = [search_content, search_db_by_year],
  llm = llm,
  agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
  verbose = True
)

if "messages" not in st.session_state:
  st.session_state.dashscope["messages"] = [{
    "role": "assistant",
    "content": "欢迎使用阿里通义千问，有什么能帮助你的吗？"
  }]

for message in st.session_state.dashscope["messages"]:
  write_message(message['role'], message['content'], save = False)

if user_input := st.chat_input("想说点什么？"):
  write_message("user", user_input)
  response = agent.invoke(user_input, {"callbacks" : [StreamlitCallbackHandler(st.container())]})
  write_message("assistant", response['output'])