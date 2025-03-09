import streamlit as st

from langchain_openai.chat_models.base import ChatOpenAI

from llms.model import ModelConfig, AgentFactory, basic_cmdi_model_config

class CMDIFactory(AgentFactory):
    base_url: str = st.secrets["DEEP_URL"]
    config: ModelConfig = basic_cmdi_model_config
    llm: ChatOpenAI = ChatOpenAI(api_key = config.api_key, base_url = base_url, model=config.name)
    def agent(self) -> ChatOpenAI:
        return self.llm