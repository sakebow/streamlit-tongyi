import streamlit as st

from langchain_openai.chat_models.base import ChatOpenAI

from openai import OpenAI

from llms.model import ModelConfig, AgentFactory, basic_cmdi_model_config

class CMDIFactory(AgentFactory):
    base_url: str = st.secrets["DEEP_URL"]
    config: ModelConfig = basic_cmdi_model_config
    llm: ChatOpenAI = None
    def agent(self):
        if self.llm is None:
            self.llm = ChatOpenAI(
                api_key = self.config.api_key,
                base_url = self.base_url,
                model=self.config.name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
            )
        return self
    def create(self) -> OpenAI:
        return OpenAI(
            base_url=self.base_url,
            api_key=self.config.api_key
        )
    def build(self) -> ChatOpenAI:
        return self.llm
    
if __name__ == "__main__":
    # llm = CMDIFactory().create()
    # response = llm.chat.completions.create(
    #     model="DeepSeek-R1-Distill-Qwen-32B",
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": "You are a helpful assistant."
    #         },
    #         {
    #             "role": "user",
    #             "content": "Hello, World"
    #         }
    #     ],
    #     max_tokens=32768
    # )
    # print(response)
    """
    这里成功输出：
    ChatCompletion(id='endpoint_common_17', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='<think>\nOkay, so I\'m trying to figure out how to respond to this message. The user wrote, "You are a helpful assistant." and then "Hello, World". I\'m not entirely sure what they\'re asking for, but I\'ll try to break it down.\n\nFirst, "You are a helpful assistant." seems like a prompt or instruction. Maybe they\'re setting the stage for how they want me to respond. Then they say "Hello, World", which is a classic first program in many programming languages. It\'s often used to test if something is working correctly.\n\nI wonder if they\'re asking me to write a "Hello, World" program in a specific language. But they didn\'t mention any language, so that\'s a bit confusing. Alternatively, maybe they\'re just greeting me and want a friendly response.\n\nI should consider both possibilities. If they want a program, I can offer to write it in a language of their choice. If they\'re just greeting, I can respond politely. Since they didn\'t specify, I\'ll make sure to ask for clarification if needed.\n\nAlso, I should keep my response friendly and open-ended to encourage them to provide more details. That way, I can assist them better based on their actual needs.\n</think>\n\nHello! It seems like you\'re greeting me. If you\'d like, I can help you write a "Hello, World" program in any programming language of your choice. Please let me know how I can assist you further!', refusal=None, role='assistant', audio=None, function_call=None, tool_calls=None))], created=1743400205, model='DeepSeek-R1-Distill-Qwen-32B', object='chat.completion', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=302, prompt_tokens=12, total_tokens=314, completion_tokens_details=None, prompt_tokens_details=None))
    """
    llm2 = CMDIFactory().agent().build()
    response = llm2.invoke([
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello, World"
        }
    ])
    print(response)
    # def response_resolver(response):
    #     tool_calls = response.additional_kwargs.get("tool_calls", [])
    #     if not tool_calls:
    #         # 说明模型没有想调用任何函数，那就可以直接把 content 输出，或者另做处理
    #         return response.content
    #     else:
    #         # 如果模型想调用多个函数，可以循环处理，这里只演示第一个
    #         call = tool_calls[0]
    #         print(call)
    #         # 获取函数名
    #         function_name = call["function"]["name"]  # "addition_tool"
    #         print(function_name)
    #         # 获取参数字符串，转成字典
    #         function_args_str = json.loads(call["function"]["arguments"])  # 比如 {"__arg1": "1 + 2"}
    #         print(function_args_str)
    #         # 注意：有的模型会把它放在 call["function"]["arguments"]，视具体结构而定
    #         # 有时要 json.loads(call["function"]["arguments"])
            
    #         # 你要先确认函数名是否是 "addition_tool"，再解析参数
    #         if function_name == "addition_tool":
    #             # 解析参数
    #             a_plus_b = function_args_str["__arg1"]  # "1 + 2"
    #             # 假设 addition_tool 实际需要的就是两个数字
    #             a_str, b_str = [item.strip() for item in a_plus_b.split("+")]
    #             result = addition_tool(float(a_str), float(b_str))
    #             return result
    #         else:
    #             # 如果还可能有其他函数，就根据函数名分发
    #             return f"unknown function {function_name}"