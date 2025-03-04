import os
import importlib
from pymilvus import MilvusClient
from sqlalchemy.engine.row import Row
from pydantic import BaseModel, Field
from typing import List, Sequence, Any
from streamlit.runtime.uploaded_file_manager import UploadedFile

from utils.embeddings_manager import EmbeddingSearcher, Text2Embed
from utils.config import DefaultCommonConfig

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
    """
    将现有的markdown文件生成到streamlit页面中
    params: file_path: str markdown文件路径
    return: Sequence[str] markdown文件内容
    """
    page_name, _ = os.path.splitext(os.path.basename(file_path))
    md_file_path = os.path.join("page_md", f"{page_name}.md")
    with open(md_file_path, 'r') as file:
      content = file.read()
    return content

class DBManager(BaseModel):
  """
  类似MyBatisPlus的数据库池，为方法增加SQL解析注解，直接在方法上写SQL即可执行结果
  """
  base_type: str = Field(..., description="数据库表名")
  link: str = Field(..., description="数据库连接地址")
  local_generator: Any = Field(..., description="实体类实例化解析生成器")
  # 查询方法
  def search(query_template): ...
  def import_class_from_package(self, package_name, class_name):
    """
    动态导入DTO类，用于保存SQL执行结果
    params:
      package_name: str 包名
      class_name: str 类名
    return: Any 类对象
    """
    # 导入包
    _package = importlib.import_module(package_name)
    # 寻找是否存在该类
    if class_name not in _package.__all__:
      raise ImportError(f"{class_name} not found in {package_name}")
    # 返回该类或者报错
    cls = getattr(_package, class_name)
    if cls is not None:
      return cls
    else:
      raise ImportError(f"{class_name} not found in {package_name}")
  def create_item_obj(self, row: Row):
    """
    将该类序列化输出
    """
    return self.local_generator(**row._asdict()) if self.local_generator else None