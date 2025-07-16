import streamlit as st
from httpx import Client
from langchain_openai.chat_models.base import ChatOpenAI

from factory.cmdi import CMDIFactory
from factory.tongyi import TongyiFactory
from utils.chat_render import ChatRenderer

# llm: ChatOpenAI = TongyiFactory.get_instance(
#     base_url = st.secrets["DASH_URL"],
#     api_key = st.secrets["DASHSCOPE_API_KEY"],
#     _client = client
# ).build(
#     model = "qwen-max",
#     client = client
# )

if "dashscope" not in st.session_state:
    st.session_state["dashscope"] = {
        "messages": [
            {
                "role": "assistant",
                "content": "这只是一个基础测试页面，你不可以问一些奇怪的问题，不然的话我也会变得奇怪的இдஇ"
            }
        ]
    }

st.title("基础问答页面")

# ---------- 回放历史 ----------
for m in st.session_state["dashscope"]["messages"]:
    ChatRenderer(m["role"], save=False).render(m["content"])

# ---------- 新输入 ----------
if prompt := st.chat_input("你得注意你的言行……求你了……(´;ω;`)"):
    st.session_state["dashscope"]["messages"].append({
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
        ChatRenderer("user").render(prompt)               # 用户消息
        # LLM 流式响应
        response_stream = llm.stream(prompt)              # Iterator[BaseMessageChunk]
        ChatRenderer("assistant").render(response_stream) # 打字机效果
