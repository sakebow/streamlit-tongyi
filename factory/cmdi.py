from factory.base import BaseLLMFactory

class CMDIFactory(BaseLLMFactory):
    ...
    
if __name__ == "__main__":
    import streamlit as st
    from langchain_openai.chat_models.base import ChatOpenAI
    from factory.client import ClientFactory

    f1 = CMDIFactory.get_instance(
        base_url=st.secrets["DEEP_URL"],
        api_key=st.secrets["APPCODE_KEY"],
        _client = ClientFactory.get_instance(
            base_url=st.secrets["DEEP_URL"],
            api_key=st.secrets["APPCODE_KEY"],
            timeout=30,
        ).client()
    )
    f2 = CMDIFactory.get_instance(
        base_url=st.secrets["DEEP_URL"],
        api_key=st.secrets["APPCODE_KEY"],
        _client = ClientFactory.get_instance(
            base_url=st.secrets["DEEP_URL"],
            api_key=st.secrets["APPCODE_KEY"],
            timeout=30,
        ).client()
    )
    print(f1 is f2)

    llm: ChatOpenAI = CMDIFactory.get_instance(
        base_url=st.secrets["DEEP_URL"],
        api_key=st.secrets["APPCODE_KEY"],
        _client = ClientFactory.get_instance(
            base_url=st.secrets["DEEP_URL"],
            api_key=st.secrets["APPCODE_KEY"],
            timeout=30,
        ).client()
    ).build(
        model = "DeepSeek-70B",
        temperature = 0.7,
        max_tokens = 4096
    )
    llm.generate
    from langchain_core.messages import BaseMessage
    response: BaseMessage = llm.invoke([
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello, World"
        }
    ])
    print(response.content)
    from collections.abc import Iterator
    from langchain_core.messages import BaseMessageChunk
    response: Iterator[BaseMessageChunk] = llm.stream([
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello, World"
        }
    ])
    for text in response:
        print(text.content, end = "", flush=True)