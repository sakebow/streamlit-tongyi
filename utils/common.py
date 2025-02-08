import os
from typing import List, Sequence
from pymilvus import MilvusClient
from streamlit.runtime.uploaded_file_manager import UploadedFile

from utils.embeddings_manager import EmbeddingSearcher, Text2Embed

class DefaultCommonConfig(enumerate):
  DIMENSION: int = 1024
  SPLIT_PATTERN_LIST: List = ["\n", "\n\n"]

  DATABASE_NAME: str = "rag_test"
  COLLECTION_NAME: str = "demo"

class RagHelper:
  @staticmethod
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
      doc_content.extend(Text2Embed.split_content(file, save_path = f"upload/{file.name}"))
    
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
  @staticmethod
  def search_content(user_input: str, uploaded_files: Sequence[UploadedFile] = None) -> Sequence[str]:
    """
    根据用户输入，搜索相关文件内容
    params:
      user_input: str 用户输入
      uploaded_files: Sequence[UploadedFile] 上传的文件（支持多个文件）
    return: Sequence[str] 相关文件内容
    """
    if uploaded_files is None:
      return []
    client: MilvusClient = RagHelper.configure_retriever(uploaded_files)
    results = EmbeddingSearcher.embedding_search(client, DefaultCommonConfig.COLLECTION_NAME, user_input)
    content = "\n".join([result["entity"]["text"] for result in results])
    return content

class ContentHelper:
  def get_markdown_content(file_path: str) -> Sequence[str]:
    page_name, _ = os.path.splitext(os.path.basename(file_path))
    md_file_path = os.path.join("page_md", f"{page_name}.md")
    with open(md_file_path, 'r') as file:
      content = file.read()
    return content