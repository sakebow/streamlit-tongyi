import streamlit as st
from pathlib import Path
from httpx import Client
from langchain_openai.chat_models.base import ChatOpenAI

from factory.cmdi import CMDIFactory
from utils.chat_render import ChatRenderer
from utils.page_content import init_page_state

PAGE_KEY = init_page_state(__file__)

st.title("基础问答页面")

# ---------- 回放历史 ----------
for m in st.session_state[Path(__file__).parent.name][Path(__file__).stem]:
    ChatRenderer(
        m["role"], save=False, state_path = PAGE_KEY
    ).render(m["content"])

# ---------- 新输入 ----------
if prompt := st.chat_input("你得注意你的言行……求你了……(´;ω;`)"):
    st.session_state[Path(__file__).parent.name][Path(__file__).stem].append({
        "role": "user", "content": prompt
    })
    with Client(
        base_url=st.secrets["DEEP_URL"],
        headers={"Authorization": f'Bearer {st.secrets["APPCODE_KEY"]}'},
        timeout=30,
    ) as client:
        llm: ChatOpenAI = CMDIFactory.get_instance(
            base_url=st.secrets["DEEP_URL"],
            api_key=st.secrets["APPCODE_KEY"],
        ).build(
            model = "DeepSeekR1",
            temperature = 0.7,
            max_tokens = 4096,
            client = client
        )

        ChatRenderer("user", state_path = PAGE_KEY).render(
            prompt               # 用户消息
        )
        # LLM 流式响应
        response_stream = llm.stream(
            st.session_state[Path(__file__).parent.name][Path(__file__).stem]              # Iterator[BaseMessageChunk]
        )
        ChatRenderer("assistant", state_path = PAGE_KEY).render(
            response_stream      # 大模型消息
        )
