"""
db helper tools
"""
import streamlit as st
from neo4j import GraphDatabase

from langchain.agents import Tool

# 创建 Neo4j 驱动
uri = f'bolt://{st.secrets["NEO4J_ADDR"]}:{st.secrets["NEO4J_PORT"]}'
username = st.secrets["NEO4J_USER"]
password = st.secrets["NEO4J_PASS"]
driver = GraphDatabase.driver(uri, auth = (username, password))

def neo4j_query(query: str) -> list:
  """
  query neo4j database
  Args:
    query (str): 查询语句
  Rereturns:
    list: 查询结果
  """
  with driver.session() as session:
    result = session.run(query)
    return [record.data() for record in result]

# 定义工具
neo4j_tool = Tool(
  name="Neo4jQuery",
  func=neo4j_query,
  description="用于执行 Neo4j 查询的工具。"
)

tools = [neo4j_tool]