import os
import re
from http import HTTPStatus
from pymilvus.client.types import ExtraList
from pymilvus.milvus_client.index import IndexParams
from pymilvus import MilvusClient, FieldSchema, CollectionSchema, DataType
from typing import Sequence, List, Dict

import dashscope
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

class DefaultCommonConfig(enumerate):
  DIMENSION: int = 1024
  SPLIT_PATTERN_LIST: List = ["\n", "\n\n"]

class Text2Embed:
  """
  将文件转为向量embedding
  """
  dashscope.api_key = st.secrets["DASHSCOPE_API_KEY"]
  @staticmethod
  def split_content(file: UploadedFile, save_path: str = None) -> Sequence[str]:
    """
    将上传的文件分割为多个文本块，并保存到本地
    """
    _tmp_one_file_texts = file.read().decode("utf-8", errors = "ignore")
    pattern = "|".join(DefaultCommonConfig.SPLIT_PATTERN_LIST)
    chunks = re.split(pattern = pattern, string = _tmp_one_file_texts)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    if save_path is not None and os.path.exists(save_path):
      with open(file = save_path, mode = "w", encoding = "utf-8") as f:
        f.write("\n".join(chunks))
    return chunks
  @staticmethod
  def split_local_content(file_path: str) -> Sequence[str]:
    """
    将本地的文件分割为多个文本块（测试用处较多）
    """
    with open(file_path, 'r', encoding = 'utf-8') as f:
      file_content = f.read()
    pattern = "|".join(DefaultCommonConfig.SPLIT_PATTERN_LIST)
    chunks = re.split(pattern = pattern, string = file_content)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    return chunks
  @staticmethod
  def embeddings_content(
    content: str, dimension: int = DefaultCommonConfig.DIMENSION
  ) -> Sequence:
    """
    调用`dashscope`的文本`embedding`服务
    本段完全摘自`dashscope`的官方文档
    """
    resp = dashscope.TextEmbedding.call(
      model = dashscope.TextEmbedding.Models.text_embedding_v3,
      input = content,
      dimension = dimension
    )
    if resp.status_code == HTTPStatus.OK:
      return resp.output["embeddings"][0]["embedding"]
    else:
      return []

class EmbeddingSearcher:
  @staticmethod
  def create_or_replace(
    client: MilvusClient, db_file_name: str, collection_name: str, dimension: int = DefaultCommonConfig.DIMENSION,
    data: Sequence[str] = None
  ) -> MilvusClient:
    """
    创建搜索样本库
    """
    # 为了简化操作，直接本地创建搜索样本库，并采用覆盖创建的方式
    db_file_path = f"{db_file_name}.db"
    if client is None or not os.path.exists(db_file_path):
      client = MilvusClient(db_file_path)
    if client.has_collection(collection_name = collection_name):
      client.drop_collection(collection_name = collection_name)
    # 创建集合
    client.create_collection(
      collection_name = collection_name, dimension = dimension,
      metric_type="IP",  # Inner product distance
      consistency_level="Strong",  # Strong consistency level
      # 创建集合`schema`
      schema = CollectionSchema(fields=[
        ## 下面三个字段来自`milvus`官网的`example`
        ### `id`字段，自增（手动）主键，标记当前句子是第几个
        FieldSchema(name = "id", dtype = DataType.INT64, is_primary = True, description="primary key"),
        ### `embeddings`字段，存储当前句子的向量
        FieldSchema(name = "embeddings", dtype = DataType.FLOAT_VECTOR, description="embeddings", dim=dimension),
        ### `text`字段，存储句子本身
        FieldSchema(name = "text", dtype = DataType.VARCHAR, description="text", max_length=65535)
      ], description = "data schema")
    )
    # 创建集合索引，创建后才可以使用`IP`搜索策略
    index_params = IndexParams()
    ## 主要针对`embeddings`字段创建索引
    index_params.add_index(field_name = "embeddings", index_type = "IVF_FLAT", index_name = "embeddings")
    client.create_index(collection_name = collection_name, index_params = index_params)
    # 插入数据
    if data is not None:
      client.insert(collection_name = collection_name, data = data)
    return client
  @staticmethod
  def embedding_search(
    client: MilvusClient, collection_name: str, question: str, top_k: int = 5
  ) -> Sequence[Sequence[Dict]]:
    """
    搜索向量
    """
    result = client.search(
      collection_name = collection_name,
      anns_field = "embeddings",  # 指定搜索的向量字段名（关键参数）
      data = [Text2Embed.embeddings_content(content = question)], # 输入搜索向量
      limit = top_k,
      output_fields = ["text"]
    )
    """
    result输出：
      data: ["[
        {'id': 0, 'distance': 0.7548444271087646, 'entity': {'text': ...}},
        {'id': 1, 'distance': 0.7238685488700867, 'entity': {'text': ...}},
        {'id': 3, 'distance': 0.6937779784202576, 'entity': {'text': ...}}, ...]
      "]
    因此解包需要指定返回第一个结果
    """
    return result[0]

if __name__ == "__main__":
  # wcnmd，milvus不支持windows
  # wdnmd，目前milvus在AlmaLinux+Xfce上表现良好，MacOS 未测试
  strings: Sequence[str] = Text2Embed.split_local_content("upload/example.txt")
  
  embeddings: Sequence = [
    {"id": idx, "embeddings": Text2Embed.embeddings_content(s), "text": s}
    for idx, s in enumerate(strings)
  ]
  
  client: MilvusClient = None
  client = EmbeddingSearcher.create_or_replace(client, "rag_test", "demo", 1024, embeddings)

  result: ExtraList = EmbeddingSearcher.embedding_search(client, "demo", "跟程维认识是什么时候")
  
  print(result)