import re
import dashscope
from http import HTTPStatus
from typing import Sequence, List

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from pymilvus import MilvusClient

# 读取文件
@st.cache_resource(ttl = "1h")
def configure_retriever(uploaded_files: Sequence[UploadedFile]):
  doc_content: List = []
  for file in uploaded_files:
    _one_file_path = f"./upload/{file.name}"
    with open(_one_file_path, "wb") as f:
      f.write(file.getvalue())
    _one_file_text = file.read().decode("utf-8", errors = "ignore")
    pattern = "|".join(["\n", "\n\n"])
    chunks = re.split(pattern = pattern, string = _one_file_text)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    doc_content.extend(chunks)
  result = None
  batch_counter = 0
  DASHSCOPE_MAX_BATCH_SIZE = 10
  INNER_DIMENSION = 1024
  for i in range(0, len(doc_content), DASHSCOPE_MAX_BATCH_SIZE):
    batch = doc_content[i:i + DASHSCOPE_MAX_BATCH_SIZE]
    resp = dashscope.TextEmbedding.call(
      model=dashscope.TextEmbedding.Models.text_embedding_v3,
      input=batch,
      dimension=INNER_DIMENSION
    )
    if resp.status_code == HTTPStatus.OK:
      if result is None:
        result = resp
      else:
        for emb in resp.output['embeddings']:
          emb['text_index'] += batch_counter
          result.output['embeddings'].append(emb)
        result.usage['total_tokens'] += resp.usage['total_tokens']
    else:
      print(resp)
    batch_counter += len(batch)
    milvus_client = MilvusClient(uri = 'assets/rag_test.db')
    collection_name = "rag_test"
    if milvus_client.has_collection(collection_name): milvus_client.drop_collection(collection_name)
    milvus_client.create_collection(
      collection_name = collection_name,
      dimension = INNER_DIMENSION,
      metric_type = "IP",  # Inner product distance
      consistency_level = "Strong",  # Strong consistency level
    )
    # milvus_client.insert(collection_name = collection_name, data = [{
    #   "id": i, "vector": embedding, "text": line
    # } for i, embedding in enumerate(result['output']['embeddings'])])
  return doc_content, result

# 页面配置
st.set_page_config(page_title = "rag_test", page_icon = ":robot:", layout = "wide")
st.title("rag_test")
# 侧边上传文件
uploaded_files = st.sidebar.file_uploader(
  label = "上传文件", type = ["txt"], accept_multiple_files = True
)
all_texts, results = configure_retriever(uploaded_files)
st.write(f"已找出{len(all_texts)}条数据")
st.write(results)
st.stop()