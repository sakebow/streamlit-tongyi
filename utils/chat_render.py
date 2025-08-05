# handler.py
from __future__ import annotations
import re, time
import streamlit as st
from collections.abc import Iterable as AbcIterable
from typing import Any, Sequence, Iterator, Tuple, Optional
from collections.abc import Iterator

from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.messages.base import BaseMessageChunk, BaseMessage

from utils.page_content import get_messages_container

_THINK_RE = re.compile(r"<think>(.*?)</think>", re.S)


class ChatRenderer:
    """兼容 LangChain/LangGraph 的流式渲染器（expander + chat_message）"""

    def __init__(
        self,
        role: str,
        save: bool = True,
        typing_delay: float = 0.02,
        state_path: "Sequence[str] | str" = "dashscope",
    ):
        self.role = role
        self.save = save
        self.typing_delay = typing_delay
        self.state_path = state_path

        with st.chat_message(role):
            self.answer_holder = st.empty()

        self.expander = None
        self.think_holder = None
        self._buffer = ""

    # ===== 公共接口 =====
    def render(
        self,
        msg_stream: "str | BaseMessage | BaseMessageChunk | AbcIterable",
        *,
        nodes: "set[str] | None" = None,  # 可选：只显示这些节点的 token
        tags: "set[str] | None" = None,  # 可选：只显示带这些 tag 的 token
    ):
        """把各种输入统一流式渲染到 UI。"""
        for text, meta in self._iter_tokens(msg_stream):
            # 可选过滤：按节点/标签过滤并发输出，避免串流交叉
            if nodes and (meta or {}).get("langgraph_node") not in nodes:
                continue
            if tags and not (tags <= set((meta or {}).get("tags", []))):
                continue

            if text:
                self._update(text)
                if self.typing_delay:
                    time.sleep(self.typing_delay)
        if self.save:
            get_messages_container(self.state_path).append(
                {"role": self.role, "content": self._buffer}
            )
        print(self.role)
        print(get_messages_container(self.state_path))
        print("\n")

    # ===== 内部：把任意输入迭代成 (text, metadata) =====
    def _iter_tokens(
        self, stream: "str | BaseMessage | BaseMessageChunk | AbcIterable"
    ) -> Iterator[Tuple[str, Optional[dict]]]:
        # 1) 单次对象：str / BaseMessage / BaseMessageChunk
        if isinstance(stream, (str, BaseMessage, BaseMessageChunk)):
            text = self._to_text(stream)
            if text:
                yield text, None
            return

        # 2) 可迭代流（LangGraph/自定义）
        if isinstance(stream, AbcIterable):
            for item in stream:
                meta = None
                chunk = item

                # LangGraph messages 模式： (message_chunk, metadata)
                if isinstance(item, tuple) and len(item) == 2:
                    chunk, meta = item

                # 少数情况下会是 [BaseMessageChunk, ...] 的列表
                if (
                    isinstance(chunk, (list, tuple))
                    and chunk
                    and isinstance(chunk[0], BaseMessageChunk)
                ):
                    for c in chunk:
                        text = self._to_text(c)
                        if text:
                            yield text, meta
                    continue

                text = self._to_text(chunk)
                if text:
                    yield text, meta
            return

        raise TypeError("不支持的消息类型")

    # ===== 内部：把各种 Message / Chunk 取出可显示的纯文本 =====
    def _to_text(self, m: "str | BaseMessage | BaseMessageChunk") -> str:
        if isinstance(m, str):
            return m
        if isinstance(m, (BaseMessage, BaseMessageChunk)):
            c = getattr(m, "content", "")
            if isinstance(c, str):
                return c
            # content-blocks（例如 Anthropic）：仅提取 type=='text'
            if isinstance(c, list):
                parts = []
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "text" and "text" in b:
                        parts.append(b["text"])
                return "".join(parts)
        return ""

    # ===== 内部：刷新 UI =====
    def _update(self, new_text: str):
        if not new_text:
            return
        self._buffer += new_text

        # 聚合所有 <think> 段落
        think_parts = "\n".join(_THINK_RE.findall(self._buffer))
        answer_text = _THINK_RE.sub("", self._buffer).strip() or " "

        if think_parts and self.expander is None:
            self.expander = st.expander("🤔 思考过程", expanded=False)
            self.think_holder = self.expander.empty()

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
        state_path: Sequence[str] | str = "dashscope",
    ):
        super().__init__()
        self.role = role
        self.save = save
        self.label = label

        # UI 占位：只有 answer 先占位，<think> 动态生成
        with st.chat_message(role):
            self.answer_holder = st.empty()

        self.expander = None
        self.think_holder = None

        # 累积完整文本
        self.buffer = ""

        self.state_path = state_path

    # ===== Callback API =====
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """收到新 token 就增量刷新 UI。"""
        self._update(token)

    def on_llm_end(self, response, **kwargs: Any) -> None:
        """流式结束，把完整内容写进 session_state。"""
        if self.save:
            get_messages_container(self.state_path).append(
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
            self.expander = st.expander(self.label, expanded=False)
            self.think_holder = self.expander.empty()

        # 刷新 UI
        if self.think_holder is not None:
            self.think_holder.markdown(think_parts)
        self.answer_holder.markdown(answer_text)
