from typing import Sequence, List

import streamlit as st
from pymilvus import MilvusClient
from langchain.agents.agent_types import AgentType
from langchain.agents import initialize_agent, tool
from langchain.callbacks.streamlit import StreamlitCallbackHandler
from streamlit.runtime.uploaded_file_manager import UploadedFile

from llms import TongyiFactory
from utils import EmbeddingSearcher, Text2Embed, DefaultCommonConfig

@st.cache_resource(ttl = "1h")
def configure_retriever(uploaded_files: Sequence[UploadedFile]) -> MilvusClient:
  """
  读取文件，生成embedding，并保存到milvus中
  params: uploaded_files: 上传的文件（支持多个文件）
  return: MilvusClient
  """
  if uploaded_files is None:
    return []
  doc_content: List = []
  for file in uploaded_files:
    doc_content.extend(Text2Embed.split_content(file, save_path = "upload"))
  
  embeddings: Sequence = [
    {"id": idx, "embeddings": Text2Embed.embeddings_content(s), "text": s}
    for idx, s in enumerate(doc_content)
  ]
  
  client: MilvusClient = None
  client = EmbeddingSearcher.create_or_replace(
    client,
    DefaultCommonConfig.DATABASE_NAME, DefaultCommonConfig.COLLECTION_NAME,
    1024, embeddings
  )
  return client


# 页面配置
# st.set_page_config(page_title = "rag_test", page_icon = ":hotdog:", layout = "wide")
st.title("rag_test")

# 侧边上传文件
uploaded_files = st.sidebar.file_uploader(
  label = "上传文件", type = DefaultCommonConfig.SUPPORT_TYPES, accept_multiple_files = True
)

@tool
def search_content_with_llm(user_input: str) -> str:
  """
  搜索文件的过程中增加LLM的辅助
  """
  if "file_message" in st.session_state:
    return st.session_state.file_message
  client: MilvusClient = configure_retriever(uploaded_files)
  results = EmbeddingSearcher.embedding_search(client, DefaultCommonConfig.COLLECTION_NAME, user_input)
  content = "\n".join([result["entity"]["text"] for result in results])
  st.session_state.file_message = content
  return content

llm = TongyiFactory().create()
agent = initialize_agent(
  tools = [search_content_with_llm],
  llm = llm,
  agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
  verbose = True
)

if "messages" not in st.session_state:
  st.session_state.messages = [{
    "role": "assistant",
    "content": "你好，我能够帮你查询上传文件中的内容。如果文件中存在，我会告诉你答案；如果文件中找不到答案，我也会告诉你文件中并没有答案。"
  }]

def write_message(role: str, message: str, save: bool = True):
  if save:
    st.session_state.messages.append({"role": role, "content": message})
  with st.chat_message(role):
    st.markdown(message)

for message in st.session_state.messages:
  write_message(message['role'], message['content'], save = False)

if user_input := st.chat_input("想说点什么？"):
  write_message("user", user_input)
  response = agent.run(user_input, callbacks = [StreamlitCallbackHandler(st.container())])
  write_message("assistant", response)