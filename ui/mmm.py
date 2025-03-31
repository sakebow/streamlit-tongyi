import streamlit as st
from openai import OpenAI

from langchain.callbacks.streamlit import StreamlitCallbackHandler

from utils import CompletionUtils

st.session_state["mmm"] = {}

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=st.secrets["DASHSCOPE_API_KEY"],
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def write_message(role: str, message: str, save: bool = True):
  if save:
    st.session_state["mmm"]["messages"].append({"role": role, "content": message})
  with st.chat_message(role):
    st.markdown(message)

# print(CompletionUtils.mm_completion(client, "这幅图片讲了什么？", "/home/sakebow/Downloads/miku.jpg", st.session_state["mmm"]["messages"]))
st.title("多模态")

if "messages" not in st.session_state:
  st.session_state["mmm"]["messages"] = [{
    "role": "assistant",
    "content": "欢迎使用多模态，有什么能帮助你的吗？"
  }]

for message in st.session_state["mmm"]["messages"]:
  write_message(message['role'], message['content'], save = False)

# import streamlit as st
# from openai import OpenAI

# client = OpenAI(
#     # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
#     api_key=st.secrets["DASHSCOPE_API_KEY"],
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
# )

# completion = client.chat.completions.create(
#     model="qwen-omni-turbo",
#     messages=[
#         {
#             "role": "system",
#             "content": [{"type": "text", "text": "You are a helpful assistant."}],
#         },
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": "http://images.sakebow.cn/LLM/introduction/%E4%B8%8B%E8%BD%BD%E4%BB%80%E4%B9%88%E5%A5%BD%E5%91%A2.png"
#                     },
#                 },
#                 {"type": "text", "text": "图中描绘的是什么景象？"},
#             ],
#         },
#     ],
#     # 设置输出数据的模态，当前支持["text"]
#     modalities=["text"],
#     # stream 必须设置为 True，否则会报错
#     stream=True,
#     stream_options={
#         "include_usage": True
#     }
# )

# for chunk in completion:
#     if chunk.choices:
#         print(chunk.choices[0].delta)
#     else:
#         print(chunk.usage)
