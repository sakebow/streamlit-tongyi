from typing import Sequence, List

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from pymilvus import MilvusClient

from utils import EmbeddingSearcher, Text2Embed

DATABASE_NAME = "rag_test"
COLLECTION_NAME = "demo"

# 读取文件
@st.cache_resource(ttl = "1h")
def configure_retriever(uploaded_files: Sequence[UploadedFile]) -> MilvusClient:
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
  client = EmbeddingSearcher.create_or_replace(client, DATABASE_NAME, COLLECTION_NAME, 1024, embeddings)
  return client

# 页面配置
# st.set_page_config(page_title = "embeddings_search", page_icon = ":hotdog:", layout = "wide")
st.title("embeddings_search")
# 用户交互
user_input = st.chat_input("请输入问题")
# 侧边上传文件
uploaded_files = st.sidebar.file_uploader(
  label = "上传文件", type = ["txt"], accept_multiple_files = True
)
if not user_input and not uploaded_files:
  st.write("有什么能帮你？")
elif user_input and not uploaded_files:
  st.warning("暂未上传文件，请先上传文件")
elif not user_input and uploaded_files:
  st.warning("你想要了解什么？")
elif user_input and uploaded_files:
  client = configure_retriever(uploaded_files)
  results = EmbeddingSearcher.embedding_search(client, COLLECTION_NAME, user_input)
  st.write(f"已找出{len(results)}条数据")
  st.write(results)