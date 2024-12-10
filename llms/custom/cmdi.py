import json
import requests

import streamlit as st

from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun


from typing import Any, Dict, Tuple, List, Optional


class CMDILLM(LLM):
  """
  由于部分大模型已经利用昇腾的 `MindIE` 构建了基本的推理接口，直接请求接口也能用
  但还是希望能够直接用上 `langchain` 的各种工具。
  于是，利用 `LLM` 包装一下请求过程
  其中，必须完成的接口包括：_call, _llm_type
  """

  def _request_builder_(self, prompt: str) -> Tuple[Dict, Dict]:
    """
    创建请求参数
    """
    url: str = f"{st.secrets['BASE_URL']}/{st.secrets['MORE_URL']}/{st.secrets['OPEN_URL']}"
    payload: Dict = {
      "model": "Qwen-2.5-72B-Instruct",
      "messages": [],
      "max_tokens": 32768,
      "presence_penalty": 1.9,
      "frequency_penalty": 1.9,
      "temperature": 0.7,
      "top_p": 0.9,
      "stream": False
    }
    payload["messages"].append({"role": "user", "content": prompt})
    headers: Dict = {
      "Content-Type": "application/json",
      "Authorization": f"{st.secrets['APPCODE_TYP']} {st.secrets['APPCODE_KEY']}"
    }
    return url, payload, headers


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
    url, payload, headers = self._request_builder_(prompt)
    results = requests.post(url, json=payload, headers=headers)
    return str(json.loads(results.text)["choices"][0]["message"]["content"])
  
  def _llm_type(self) -> str: return "CMDI"