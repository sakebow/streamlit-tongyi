import streamlit as st
from pathlib import Path
from httpx import Client, Timeout
from langchain_openai.chat_models.base import ChatOpenAI

from factory.cmdi import CMDIFactory
from utils.chat_render import ChatRenderer
from utils.page_content import init_page_state
from workflow.example import build_graph

PAGE_KEY = init_page_state(__file__)

st.title("主动触发Render模块 + 基于LangGraph的意图识别")
graph = build_graph()

for m in st.session_state[
    Path(__file__).parent.name][Path(__file__).stem
]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

with Client(
    base_url = st.secrets["DEEP_URL"],
    headers  = {"Authorization": f"Bearer {st.secrets['APPCODE_KEY']}"},
    timeout  = Timeout(st.secrets["TIMEOUT"]),
) as client:
    intent_model: ChatOpenAI = CMDIFactory.get_instance(
        base_url=st.secrets["DEEP_URL"],
        api_key=st.secrets["APPCODE_KEY"]
    ).build(
        model = "DeepSeekR1",
        temperature = 0.7,
        max_tokens = 4096,
        client = client
    )
    chat_model: ChatOpenAI = CMDIFactory.get_instance(
        base_url=st.secrets["DEEP_URL"],
        api_key=st.secrets["APPCODE_KEY"]
    ).build(
        model = "DeepSeekR1",
        temperature = 0.7,
        max_tokens = 4096,
        client = client
    )
    qa_model: ChatOpenAI = CMDIFactory.get_instance(
        base_url=st.secrets["DEEP_URL"],
        api_key=st.secrets["APPCODE_KEY"]
    ).build(
        model = "DeepSeekR1",
        temperature = 0.7,
        max_tokens = 4096,
        client = client
    )

    models = {"intent": intent_model, "chat": chat_model, "qa": qa_model}

    # ---------- 新输入 ----------
    if prompt := st.chat_input("你得注意你的言行……求你了……(´;ω;`)"):

        ChatRenderer(
            role = "user", state_path = PAGE_KEY, save = True
        ).render(
            prompt                                       # 用户消息
        )
        
        response = graph.stream(
            {
                "messages": st.session_state[Path(__file__).parent.name][Path(__file__).stem],
            },
            config={
                "configurable": {"models": models},
            },
            stream_mode="messages",                      # ✅ token 级别
        )

        ChatRenderer(
            role = "assistant", state_path = PAGE_KEY, save = True
        ).render(
            response
        )