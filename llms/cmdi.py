import json
import requests

import streamlit as st

from langchain_core.language_models.llms import LLM, BaseLLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun


from typing import Any, Dict, List, Optional
from pydantic import Field

from llms import ModelConfig, LLMFactory, MemoryBucket

default_cmdi_config = ModelConfig(
  name = "Qwen-2.5-72B-Instruct",
  api_key = f"{st.secrets['APPCODE_TYP']} {st.secrets['APPCODE_KEY']}",
  max_tokens = 32768,
  presence_penalty = 0.9,
  frequency_penalty = 0.9,
  temperature = 0.7,
  top_p = 0.95,
  stream = False
)

class CMDI(LLM):
  """
  目前该产品底层通过`MindIE`提供服务，直接请求也可以用
  但由于各种各样的原因做一下`langchain`兼容
  """
  url: str = Field(..., description = "大模型服务url")
  payload: Dict = Field(..., description = "大模型服务请求体")
  headers: Dict = Field(..., description = "大模型服务请求头")
  def model_init_post(self, url, payload, headers):
    self.url = url
    self.payload = payload
    self.headers = headers
  def _call(
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
    results = requests.post(self.url, json = self.payload, headers = self.headers)
    return str(json.loads(results.text)["choices"][0]["message"]["content"])
  
  def _llm_type(self) -> str: return "CMDI"

class CMDIFactory(LLMFactory):
  def __init__(self, config: ModelConfig = default_cmdi_config):
    self.config: ModelConfig = config
    self.memory: MemoryBucket = MemoryBucket()
  def create(self) -> BaseLLM:
    assert (
      st.secrets['BASE_URL'] is not None and st.secrets['OPEN_URL'] is not None and
      st.secrets['BASE_URL'] != "" and st.secrets['OPEN_URL'] != ""
    ), "请检查`secrets.toml`文件中url的配置是否正确"
    assert (
      st.secrets['APPCODE_TYP'] is not None and st.secrets['APPCODE_KEY'] is not None and
      st.secrets['APPCODE_TYP'] != "" and st.secrets['APPCODE_KEY'] != ""
    ), "请检查`secrets.toml`文件中APPCODE的配置是否正确"
    url: str = f"{st.secrets['BASE_URL']}/{st.secrets['OPEN_URL']}"
    payload: Dict = {
      "model": "Qwen-2.5-72B-Instruct",
      "messages": self.memory.all(),
      "max_tokens": self.config.max_tokens,
      "presence_penalty": self.config.presence_penalty,
      "frequency_penalty": self.config.frequency_penalty,
      "temperature": self.config.temperature,
      "top_p": self.config.top_p,
      "stream": self.config.stream
    }
    headers: Dict = {
      "Content-Type": "application/json",
      "Authorization": f"{st.secrets['APPCODE_TYP']} {st.secrets['APPCODE_KEY']}"
    }
    self.agent = CMDI(
      url = f"{st.secrets['BASE_URL']}/{st.secrets['OPEN_URL']}",
      payload = payload,
      headers = headers
    )
    return self.agent

__all__ = ["CMDIFactory", "default_cmdi_config"]

if __name__ == "__main__":
  cmdi = CMDIFactory(default_cmdi_config).create()
  results = cmdi.invoke("你好")
  print(results)