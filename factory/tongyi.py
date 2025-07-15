from factory.base import BaseLLMFactory

class TongyiFactory(BaseLLMFactory):
    ...

if __name__ == "__main__":
    import streamlit as st
    from langchain_openai.chat_models.base import ChatOpenAI
    from factory.client import ClientFactory
    llm: ChatOpenAI = TongyiFactory.get_instance(
        base_url=st.secrets["DASH_URL"],
        api_key=st.secrets["DASHSCOPE_API_KEY"],
        _client = ClientFactory.get_instance(
            base_url=st.secrets["DEEP_URL"],
            api_key=st.secrets["APPCODE_KEY"],
            timeout=30,
        ).client()
    ).build(
        model = "qwen-max",
    )

    response = llm.invoke([
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello, World"
        }
    ])
    # from langchain_core.messages import BaseMessage
    # response: BaseMessage = llm.invoke([
    #     {
    #         "role": "system",
    #         "content": "You are a helpful assistant."
    #     },
    #     {
    #         "role": "user",
    #         "content": "Hello, World"
    #     }
    # ])
    # print(response.content)
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
    for chunk in response:
        print(chunk.content)