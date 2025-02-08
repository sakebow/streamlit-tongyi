from typing import Sequence

import streamlit as st
from pymilvus import MilvusClient
from langchain.callbacks.streamlit import StreamlitCallbackHandler
from streamlit.runtime.uploaded_file_manager import UploadedFile

from llms import CMDIFactory
from utils import EmbeddingSearcher, DefaultCommonConfig, RagHelper

st.session_state.cmdi = dict()

@st.cache_resource(ttl = "1h")
def configure_retriever(uploaded_files: Sequence[UploadedFile]) -> MilvusClient:
  return RagHelper.configure_retriever(uploaded_files)

# 页面配置
st.title("rag_test")

llm = CMDIFactory().create()

if "messages" not in st.session_state:
  st.session_state.cmdi["messages"] = [{
    "role": "assistant",
    "content": "你好，我是九天平台的大模型，有什么可以帮你？"
  }]

uploaded_file: Sequence[UploadedFile] = st.sidebar.file_uploader("上传文件", type = DefaultCommonConfig.SUPPORT_TYPES, accept_multiple_files = True)

def write_message(role: str, message: str, save: bool = True):
  if save:
    st.session_state.cmdi["messages"].append({"role": role, "content": message})
  with st.chat_message(role):
    st.markdown(message)

for message in st.session_state.cmdi["messages"]:
  write_message(message['role'], message['content'], save = False)

if user_input := st.chat_input("想说点什么？"):
  write_message("user", user_input)
  response = llm.invoke(user_input, {"callbacks" : [StreamlitCallbackHandler(st.container())]})
  write_message("assistant", response)
  if uploaded_file is not None:
    client = configure_retriever(uploaded_file)
    content = EmbeddingSearcher.embedding_search(client, DefaultCommonConfig.COLLECTION_NAME, user_input, top_k = 1)
    write_message("assistant", content)