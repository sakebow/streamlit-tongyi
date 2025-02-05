import os
import re
from http import HTTPStatus
from pymilvus import MilvusClient
from typing import Sequence, List, Dict

import dashscope
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

class Text2Embed:
  """
  RAG服务
  """
  dashscope.api_key = st.secrets["DASHSCOPE_API_KEY"]
  split_pattern_list: List = ["\n", "\n\n"]
  @staticmethod
  def split_content(file: UploadedFile) -> Sequence[str]:
    """
    将上传的文件分割为多个文本块
    """
    _tmp_one_file_texts = file.read().decode("utf-8", errors = "ignore")
    pattern = "|".join(Text2Embed.split_pattern_list)
    chunks = re.split(pattern = pattern, string = _tmp_one_file_texts)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    return chunks
  @staticmethod
  def split_local_content(file_path: str) -> Sequence[str]:
    """
    将本地的文件分割为多个文本块
    """
    with open(file_path, 'r', encoding = 'utf-8') as f:
      file_content = f.read()
    pattern = "|".join(Text2Embed.split_pattern_list)
    chunks = re.split(pattern = pattern, string = file_content)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    return chunks
  @staticmethod
  def embeddings_content(
    content: str, dimension: int  = 1024
  ) -> Sequence:
    resp = dashscope.TextEmbedding.call(
      model = dashscope.TextEmbedding.Models.text_embedding_v3,
      input = content,
      dimension = dimension
    )
    if resp.status_code == HTTPStatus.OK:
      return resp.output["embeddings"][0]["embedding"]
    else:
      return []

class Emdsearcher:
  @staticmethod
  def create_or_replace(
    client: MilvusClient, db_file_name: str, collection_name: str, dimension: int = 1024,
    data: Sequence[str] = None
  ) -> MilvusClient:
    db_file_path = f"{db_file_name}.db"
    if client is None or not os.path.exists(db_file_path):
      client = MilvusClient(db_file_path)
    if client.has_collection(collection_name = collection_name):
      client.drop_collection(collection_name = collection_name)
    client.create_collection(
      collection_name = collection_name, dimension = dimension,
      metric_type="IP",  # Inner product distance
      consistency_level="Strong",  # Strong consistency level
    )
    if data is not None:
      client.insert(collection_name = collection_name, data = data)
    return client
  @staticmethod
  def embedding_search(
    client: MilvusClient, collection_name: str, question: str
  ) -> Sequence[Sequence[Dict]]:
    result = client.search(
      collection_name = collection_name,
      data = [Text2Embed.embeddings_content(content = question)],
      limit = 3,
      search_params = {"metric_type": "IP", "params": {}},
      output_fields = ["text"]
    )
    return result

if __name__ == "__main__":
  # emb = Text2Embed.embeddings_content(
  #   content = "骆轶航：一鸣跟程维认识是哪一年？张一鸣：我们晚一点，2014年或者2015年。", dimension = 1024
  # )
  # client: MilvusClient = None
  # client = Emdsearcher.create_or_replace(
  #   client = client, db_file_name = "rag_test", collection_name = "demo", dimension = 1024, data = emb
  # )
  # print(Emdsearcher.embedding_search("认识是哪一年？"))
  # 我草泥马，milvus不支持windows
  print("=== read ===")
  strings: Sequence[str] = Text2Embed.split_local_content("upload/short.txt")
  print("=== read done ===")

  print("=== embed ===")
  embeddings: Sequence = [Text2Embed.embeddings_content(s) for s in strings]
  print("=== embed done ===")

  print("=== insert ===")
  client: MilvusClient = None
  client = Emdsearcher.create_or_replace(client, "rag_test", "demo", 1024, embeddings)
  print("=== insert done ===")

  print("=== search ===")
  result = Emdsearcher.embedding_search(client, "demo", "跟程维认是是什么时候")
  print("=== search done ===")
  
  print(result)