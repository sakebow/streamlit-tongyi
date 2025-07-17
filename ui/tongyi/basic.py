import streamlit as st
from pathlib import Path
from langchain_openai.chat_models.base import ChatOpenAI

from factory.tongyi import TongyiFactory
from utils.chat_render import ChatRenderer
from utils.page_content import init_page_state

PAGE_KEY = init_page_state(__file__)

llm: ChatOpenAI = TongyiFactory.get_instance(
    base_url = st.secrets["DASH_URL"],
    api_key = st.secrets["DASHSCOPE_API_KEY"],
).build(
    model = "qwen-max",
)

st.title("基础问答页面")

# ---------- 回放历史 ----------
for m in st.session_state[Path(__file__).parent.name][Path(__file__).stem]:
    ChatRenderer(m["role"], save=False, state_path = PAGE_KEY).render(m["content"])

# ---------- 新输入 ----------
if prompt := st.chat_input("你得注意你的言行……求你了……(´;ω;`)"):
    st.session_state[Path(__file__).parent.name][Path(__file__).stem].append({
        "role": "user", "content": prompt
    })
    ChatRenderer("user", state_path = PAGE_KEY).render(
        prompt, st.session_state[Path(__file__).parent.name][Path(__file__).stem]               # 用户消息
    )
    # LLM 流式响应
    response_stream = llm.stream(
        st.session_state[Path(__file__).parent.name][Path(__file__).stem]
    )              # Iterator[BaseMessageChunk]
    ChatRenderer("assistant", state_path = PAGE_KEY).render(
        response_stream, st.session_state[Path(__file__).parent.name][Path(__file__).stem] # 大模型消息
    )
