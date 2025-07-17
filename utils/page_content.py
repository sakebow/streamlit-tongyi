import os
import streamlit as st
from typing import List, Sequence, Dict, Any

def get_markdown_content(file_path: str) -> Sequence[str]:
    """
    将现有的markdown文件生成到streamlit页面中
    >>> 注意：要求md文件和py文件同名
    params: file_path: str markdown文件路径
    return: Sequence[str] markdown文件内容
    """
    page_name, _ = os.path.splitext(os.path.basename(file_path))
    md_file_path = os.path.join("page_md", f"{page_name}.md")
    with open(md_file_path, 'r') as file:
      content = file.read()
    return content

def get_messages_container(state_path: Sequence[str] | str = "dashscope") -> List[Dict[str, Any]]:
    """保证 session_state 中给定路径下存在 ["messages"]，并返回该 list 引用。  
    参数可以是单个字符串，也可以是 ('root', 'sub', …) 形式的多级路径。
    """
    # 把单字符串改成 tuple，便于统一处理
    if isinstance(state_path, str):
        state_path = (state_path,)

    node = st.session_state
    n = len(state_path)
    for idx in range(n - 1):
        node = node.setdefault(state_path[idx], {})
    # 此时 node 是最深一级 dict
    return node.setdefault(state_path[:-1], [])
