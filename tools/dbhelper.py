"""
db helper tools
"""
import streamlit as st
from neo4j import GraphDatabase
from typing import List, Optional

from langchain.schema.runnable import Runnable
from langchain.prompts.base import BasePromptTemplate
from langchain_core.memory import BaseMemory

# 创建 Neo4j 驱动
uri = f'bolt://{st.secrets["NEO4J_ADDR"]}:{st.secrets["NEO4J_PORT"]}'
username = st.secrets["NEO4J_USER"]
password = st.secrets["NEO4J_PASS"]
driver = GraphDatabase.driver(uri, auth = (username, password))

class DiseaseQueryRunnable(Runnable):
  """
  自定义一个Runnable类，并重载invoke方法，在业务中查询病症实体是否在数据库中
  Args:
    entities: List[str]: 病症实体列表
    config: Optional[dict]: 配置参数 可以为空
  Returns:
    str
  """
  def invoke(self, entities: List[str], config: Optional[dict] = None) -> str:
    neo4j_results = []
    for entity in entities:
      query = f"MATCH (d:Disease {{name: '{entity}'}}) RETURN d"
      with driver.session() as session:
        result = session.run(query)
        records = [record["d"] for record in result]
        if records:
          neo4j_results.append(f"病症 '{entity}' 存在于数据库中。")
        else:
          neo4j_results.append(f"病症 '{entity}' 不存在于数据库中。")
    return "\n".join(neo4j_results)

class DiseaseExtractionRunnable(Runnable):
  # 其实BasePromptTemplate 也继承自 Runnable，但是这里为了明确说明可以接PromptTemplate，所以才写在这里。
  def __init__(self, chain: Runnable | BasePromptTemplate, memory: BaseMemory):
    self.chain = chain
    self.memory = memory
  """
  自定义Runnable对象，并重载invoke方法，在业务中利用大模型语言理解能力提取病症实体
  Args:
    inputs: dict: 输入参数
    config: Optional[dict]: 配置参数 可以为空
  Returns:
    dict
  """
  def invoke(self, inputs: dict, config: Optional[dict] = None) -> dict:
    human_input = inputs["human_input"]
    # 提取实体
    extracted_entities = self.chain.invoke({"text": human_input})
    entities = [e.strip() for e in extracted_entities.split(',') if e.strip()]
    # 查询 Neo4j
    neo4j_results = DiseaseQueryRunnable().invoke(entities)
    # 获取对话历史
    chat_history = self.memory.load_memory_variables({"human_input": human_input})["chat_history"]
    # 返回 PromptTemplate 所需的输入
    result = {
      "chat_history": chat_history,
      "human_input": human_input,
      "neo4j_results": neo4j_results
    }
    # print(result)
    return result