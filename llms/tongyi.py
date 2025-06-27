import streamlit as st

from langchain_openai.chat_models.base import ChatOpenAI

from llms.model import ModelConfig, AgentFactory, basic_qwen_model_config

class TongyiFactory(AgentFactory):
    base_url: str = st.secrets["DASH_URL"]
    config: ModelConfig = basic_qwen_model_config
    llm: ChatOpenAI = None
    def agent(self) -> ChatOpenAI:
        return ChatOpenAI(
            api_key=st.secrets["DASHSCOPE_API_KEY"],
            base_url=st.secrets["DASH_URL"],
            model="qwen-max",
            temperature=0.7,
            max_tokens=1024,
            top_p=0.8,
            frequency_penalty=0.9,
            presence_penalty=0.9,
        )