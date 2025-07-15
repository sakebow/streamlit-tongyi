import os
from typing import Sequence

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