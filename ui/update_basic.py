import streamlit as st
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.messages import HumanMessage

from factory import TongyiFactory, ClientFactory
from utils.chat_render import ChatRenderCallbackHandler

llm: ChatOpenAI = TongyiFactory.get_instance(
    base_url=st.secrets["DASH_URL"],
    api_key=st.secrets["DASHSCOPE_API_KEY"],
    _client = ClientFactory.get_instance(
        base_url=st.secrets["DASH_URL"],
        api_key=st.secrets["DASHSCOPE_API_KEY"],
        timeout=30,
    ).client()
).build(
    model = "qwen-max",
)

if "dashscope" not in st.session_state:
    st.session_state["dashscope"] = {
        "messages": [
            {
                "role": "assistant",
                "content": "这只是一个基础测试页面，你不可以问一些奇怪的问题，不然的话我也会变得奇怪的இдஇ"
            }
        ]
    }

st.title("被动触发Render模块")

# ---------- 回放历史 ----------
for m in st.session_state["dashscope"]["messages"]:
    st.chat_message(m["role"]).markdown(m["content"])
    
# ---------- 新输入 ----------
prompt = st.chat_input("你得注意你的言行……求你了……(´;ω;`)")
if prompt:
    # 1️⃣ 先把用户问句写入历史
    st.session_state.dashscope["messages"].append(
        {"role": "user", "content": prompt}
    )
    st.chat_message("user").markdown(prompt)
    handler = ChatRenderCallbackHandler(role="assistant")

    # 2️⃣ 流式调用 + 回调渲染
    _ = list(
        llm.stream([HumanMessage(content=prompt)], config={"callbacks": [handler]})
    )