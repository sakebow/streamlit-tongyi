# handler.py
import re, time
import streamlit as st
from typing import Any
from collections.abc import Iterator

from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.messages.base import BaseMessageChunk, BaseMessage

_THINK_RE = re.compile(r"<think>(.*?)</think>", re.S)

class ChatRenderer:
    """同时管理 expander + chat_message 的流式渲染器"""

    def __init__(self, role: str, save: bool = True, typing_delay: float = 0.02):
        self.role          = role
        self.save          = save
        self.typing_delay  = typing_delay

        # UI：先只放 chat_message，占位可反复写
        with st.chat_message(role):
            self.answer_holder = st.empty()

        # expander 延迟创建（只有检测到 <think> 才建）
        self.expander      = None
        self.think_holder  = None

        # 缓冲区
        self._buffer = ""

    # ===== 对外唯一接口 =====
    def render(self, msg: "str | BaseMessage | Iterator[BaseMessageChunk]"):
        if isinstance(msg, str):
            self._update(msg)
        elif isinstance(msg, BaseMessage):
            self._update(msg.content)
        elif isinstance(msg, Iterator):
            for chunk in msg:
                self._update(chunk.content)
                time.sleep(self.typing_delay)
        else:
            raise TypeError("不支持的消息类型")

        if self.save:
            st.session_state.dashscope["messages"].append(
                {"role": self.role, "content": self._buffer}
            )

    # ===== 内部 =====
    def _update(self, new_text: str):
        if not new_text:
            return
        self._buffer += new_text

        # 把 <think> 剥离出来
        think_parts = "\n".join(_THINK_RE.findall(self._buffer))
        answer_text = _THINK_RE.sub("", self._buffer).strip() or " "

        # === 首次检测到 <think> ⇒ 动态创建 expander ===
        if think_parts and self.expander is None:
            self.expander     = st.expander("🤔 思考过程", expanded=False)
            self.think_holder = self.expander.empty()

        # 刷新 UI
        if self.think_holder is not None:
            self.think_holder.markdown(think_parts)
        self.answer_holder.markdown(answer_text)


# chat_render_callback
class ChatRenderCallbackHandler(BaseCallbackHandler):
    """把 LLM 流式 token 渲染到 Streamlit，双容器分流。"""

    def __init__(
        self,
        role: str = "assistant",
        save: bool = True,
        label: str = "🤔 思考过程",
    ):
        super().__init__()
        self.role   = role
        self.save   = save
        self.label  = label

        # UI 占位：只有 answer 先占位，<think> 动态生成
        with st.chat_message(role):
            self.answer_holder = st.empty()

        self.expander     = None
        self.think_holder = None

        # 累积完整文本
        self.buffer = ""

    # ===== Callback API =====
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """收到新 token 就增量刷新 UI。"""
        self._update(token)

    def on_llm_end(self, response, **kwargs: Any) -> None:
        """流式结束，把完整内容写进 session_state。"""
        if self.save:
            st.session_state.dashscope["messages"].append(
                {"role": self.role, "content": self.buffer}
            )

    # ===== 私有 =====
    def _update(self, delta: str) -> None:
        if not delta:
            return
        self.buffer += delta

        # 拆分 <think>
        think_parts = "\n".join(_THINK_RE.findall(self.buffer))
        answer_text = _THINK_RE.sub("", self.buffer).strip() or " "

        # 第一次检测到 <think> ⇒ 创建 expander
        if think_parts and self.expander is None:
            self.expander     = st.expander(self.label, expanded=False)
            self.think_holder = self.expander.empty()

        # 刷新 UI
        if self.think_holder is not None:
            self.think_holder.markdown(think_parts)
        self.answer_holder.markdown(answer_text)
