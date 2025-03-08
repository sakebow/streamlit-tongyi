import re
import json
import requests

import streamlit as st
from langchain.tools import BaseTool
from langchain_core.language_models.llms import BaseLLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.outputs import GenerationChunk, LLMResult, Generation

from typing import Any, Dict, List, Optional, Iterator
from pydantic import Field

from llms.model import ModelConfig, LLMFactory
from llms.memory import MemoryBucket

# default_cmdi_config = ModelConfig(
#   name = "Qwen-2.5-72B-Instruct",
#   api_key = f"{st.secrets['APPCODE_TYP']} {st.secrets['APPCODE_KEY']}",
#   max_tokens = 32768,
#   presence_penalty = 0.9,
#   frequency_penalty = 0.9,
#   temperature = 0.7,
#   top_p = 0.95,
#   stream = False
# )

default_cmdi_config = ModelConfig(
    name="DeepSeek-R1-Distill-Qwen-14B",
    api_key=f"{st.secrets['APPCODE_TYP']} {st.secrets['APPCODE_KEY']}",
    max_tokens=32768,
    presence_penalty=0.9,
    frequency_penalty=0.9,
    temperature=0.7,
    top_p=0.95,
    stream=False,
)

deepseek_cmdi_config = ModelConfig(
    name="DeepSeek-R1-Distill-Qwen-32B",
    # name="DeepSeekR1",
    api_key=f"{st.secrets['APPCODE_TYP']} {st.secrets['APPCODE_KEY']}",
    max_tokens=32768,
    presence_penalty=0.9,
    frequency_penalty=0.9,
    temperature=0.7,
    top_p=0.95,
    stream=False,
)


class CMDI(BaseLLM):
    """
    目前该产品底层通过`MindIE`提供服务，直接请求也可以用
    但由于各种各样的原因做一下`langchain`兼容
    """

    url: str = Field(..., description="大模型服务url")
    payload: Dict = Field(..., description="大模型服务请求体")
    headers: Dict = Field(..., description="大模型服务请求头")
    client: Any = None

    def model_init_post(self, url, payload, headers):
        self.url = url
        self.payload = payload
        self.headers = headers

    def _generate(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Run the LLM on the given input.

        Override this method to implement the LLM logic.

        Args:
          prompt: The prompt to generate from.
          stop: Stop words to use when generating. Model output is cut off at the
            first occurrence of any of the stop substrings.
            If stop tokens are not supported consider raising NotImplementedError.
          run_manager: Callback manager for the run.
          **kwargs: Arbitrary additional keyword arguments. These are usually passed
            to the model provider API call.

        Returns:
          The model output as a string. Actual completions SHOULD NOT include the prompt.
        """
        prompt_content = ""
        if isinstance(prompt, str):
            prompt_content = prompt
        elif isinstance(prompt, list):
            prompt_content = prompt[0]
        self.payload["messages"].append({"role": "user", "content": prompt_content})
        response = requests.post(self.url, json=self.payload, headers=self.headers)
        print(response.text)
        results = str(json.loads(response.text)["choices"][0]["message"]["content"])
        generations = [[Generation(text = results)]]
        return LLMResult(generations=generations)

    def _stream(
        self,
        prompt: str,
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        prompt_content = ""
        if isinstance(prompt, str):
            prompt_content = prompt
        elif isinstance(prompt, list):
            prompt_content = prompt[0]
        self.payload["messages"].append({"role": "user", "content": prompt_content})
        self.payload["stream"] = True
        response = requests.post(self.url, json=self.payload, headers=self.headers)
        results = response.content.decode(encoding='utf-8')
        pattern = r'data:.*?(?=\ndata:|$)'
        matches = [item.strip().replace("data: ", "") for item in re.findall(pattern, results, re.DOTALL)]
        chunks = ''.join([json.loads(match)["choices"][0]["delta"]["content"] for match in matches if "[DONE]" not in match])
        generations = GenerationChunk(text=chunks)
        if run_manager:
            run_manager.on_llm_new_token(generations, verbose=self.verbose)
        yield generations

    def _llm_type(self) -> str:
        return "CMDI"


class CMDIFactory(LLMFactory):
    def __init__(self, config: ModelConfig = deepseek_cmdi_config):
        self.config: ModelConfig = config
        self.memory: MemoryBucket = MemoryBucket()

    def create(self):
        assert (
            st.secrets["BASE_URL"] is not None
            and st.secrets["OPEN_URL"] is not None
            and st.secrets["BASE_URL"] != ""
            and st.secrets["OPEN_URL"] != ""
        ), "请检查`secrets.toml`文件中url的配置是否正确"
        assert (
            st.secrets["APPCODE_TYP"] is not None
            and st.secrets["APPCODE_KEY"] is not None
            and st.secrets["APPCODE_TYP"] != ""
            and st.secrets["APPCODE_KEY"] != ""
        ), "请检查`secrets.toml`文件中APPCODE的配置是否正确"
        url: str = f"{st.secrets['DEEP_URL']}/{st.secrets['OPEN_URL']}"
        payload: Dict = {
            "model": self.config.name,
            "messages": self.memory.all(),
            "max_tokens": self.config.max_tokens,
            "presence_penalty": self.config.presence_penalty,
            "frequency_penalty": self.config.frequency_penalty,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "stream": self.config.stream,
        }
        headers: Dict = {
            "Content-Type": "application/json",
            "Authorization": f"{st.secrets['APPCODE_TYP']} {st.secrets['APPCODE_KEY']}",
        }
        self.agent = CMDI(
            url=url,
            payload=payload,
            headers=headers,
        )
        return self
    def build(self):
        return self.agent
    def with_tools(self, tools: List[Dict]):
        self.agent.payload["tools"] = tools
        self.agent.payload["tool_choice"] = "required"
        return self


__all__ = ["CMDIFactory", "default_cmdi_config", "deepseek_cmdi_config"]

if __name__ == "__main__":
    cmdi_factory = CMDIFactory(deepseek_cmdi_config)
    cmdi = cmdi_factory.create()
    cmdi_factory.memory.add_langchain_message(HumanMessage(content="你好"), role="user")
    cmdi_factory.memory.add_langchain_message(
        AIMessage(content="你好！我是千问，有什么能帮助你的吗？"), role="assistant"
    )
    results_invoke: str = cmdi.invoke("这是我的第几个问题了？")
    print(results_invoke)
    results_stream: LLMResult[List[str]] = cmdi.stream("这是我的第几个问题了？")
    print([r for r in results_stream][0])