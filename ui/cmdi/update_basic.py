import streamlit as st
from pathlib import Path
from httpx import Client
from langchain_openai.chat_models.base import ChatOpenAI

from factory.cmdi import CMDIFactory
from utils.chat_render import ChatRenderCallbackHandler

PAGE_KEY = (Path(__file__).parent.name, Path(__file__).stem)

if (
    Path(__file__).parent.name not in st.session_state
):
    st.session_state[Path(__file__).parent.name] = {}
if (
    Path(__file__).stem not in st.session_state[Path(__file__).parent.name]
):
    st.session_state[Path(__file__).parent.name] = {
        Path(__file__).stem: [
            {
                "role": "assistant",
                "content": "这只是一个基础测试页面，你不可以问一些奇怪的问题，不然的话我也会变得奇怪的இдஇ"
            }
        ]
    }

st.title("被动触发Render模块")

# ---------- 回放历史 ----------
for m in st.session_state[Path(__file__).parent.name][Path(__file__).stem]:
    st.chat_message(m["role"]).markdown(m["content"])
    
# ---------- 新输入 ----------
prompt = st.chat_input("你得注意你的言行……求你了……(´;ω;`)")
if prompt:
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
        # 1️⃣ 先把用户问句写入历史
        st.session_state[Path(__file__).parent.name][Path(__file__).stem].append(
            {"role": "user", "content": prompt}
        )
        st.chat_message("user").markdown(prompt)
        handler = ChatRenderCallbackHandler(
            role="assistant", state_path = PAGE_KEY
        )

        # 2️⃣ 流式调用 + 回调渲染
        _ = list(
            llm.stream(
                st.session_state[Path(__file__).parent.name][Path(__file__).stem],
                config={"callbacks": [handler]}
            )
        )