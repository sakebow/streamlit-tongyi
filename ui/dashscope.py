from typing import Sequence
import pandas as pd
import streamlit as st
from pymilvus import MilvusClient
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

def write_message(role: str, message: str, save: bool = True):
  if save:
    st.session_state.dashscope["messages"].append({"role": role, "content": message})
  with st.chat_message(role):
    st.markdown(message)

st.title("阿里千问")

llm = TongyiFactory().agent()

if "messages" not in st.session_state:
  st.session_state.dashscope["messages"] = [{
    "role": "assistant",
    "content": "欢迎使用阿里通义千问，有什么能帮助你的吗？"
  }]

for message in st.session_state.dashscope["messages"]:
  write_message(message['role'], message['content'], save = False)

if user_input := st.chat_input("想说点什么？"):
  write_message("user", user_input)
  response = llm.invoke(user_input, {"callbacks" : [StreamlitCallbackHandler(st.container())]})
  write_message("assistant", response.content)