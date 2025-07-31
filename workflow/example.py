import re, os
import streamlit as st
from httpx import Client, Timeout
from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_community.chat_models import ChatOpenAI
from streamlit.runtime.uploaded_file_manager import UploadedFile
from typing import Optional, Literal, Annotated, Sequence, Dict, Any
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage

# ============== State 定义 ==============
class AppState(TypedDict):
    # 会话消息（自动追加）
    messages: Annotated[list[AnyMessage], add_messages]
    # 用户上传的文件（Streamlit UploadedFile 或 None）
    uploaded_file: UploadedFile
    # 意图：0=普通聊天, 1=文件解析
    branch: Optional[int]
    # 解析后的纯文本
    file_text: Optional[str]
    # 用于显示的最终答案（可选）
    final_answer: Optional[str]

# 用 Structured Output 约束意图输出为 0/1
class IntentSchema(BaseModel):
    """根据用户输入判断分支: 0=普通聊天, 1=文件解析"""
    branch: Literal[0, 1] = Field(..., description="0 for chat, 1 for file parsing")
    rationale: Optional[str] = Field(None, description="optional reasoning")

def _get_user_input(state: AppState) -> HumanMessage:
    """
    读取最后一条用户消息，调用 LLM 得到 {branch: 0/1}
    """
    user_text = ""
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            user_text = m.content if m.content else ""
            break
    if user_text == "":
        user_text = "（空输入）"
    return HumanMessage(content=user_text)

# ============== 节点定义 ==============
def node_intent(state: AppState, config: RunnableConfig) -> Dict[str, Any]:
    """
    读取最后一条用户消息，调用 LLM 得到 {branch: 0/1}
    """
    user_text: HumanMessage = _get_user_input(state = state)
    models: Dict[str, ChatOpenAI] = config.get("configurable", {}).get("models", {})
    intent_llm: ChatOpenAI = models["intent"]  # 只在这里使用
    # 给清晰指令，要求仅按规则给出 0 或 1
    prompt = (
        "你是一个路由器：\n"
        "若用户只是闲聊/问答，输出 branch=0；\n"
        "若需要阅读或解析用户上传的文件才能答，输出 branch=1。\n"
        "严格遵守：只有 0 或 1 两种；不要解释任何内容。\n"
        f"用户消息：{user_text}"
    )
    res: AnyMessage = intent_llm.invoke(prompt)
    if res.content[-1] in [0, 1]:
        return {"branch": int(res.content[-1])}
    else:
        return {"branch": 0}

def node_chat(state: AppState, config: RunnableConfig) -> Dict[str, Any]:
    """
    直接开始聊天
    """
    chat_llm: ChatOpenAI = config["configurable"]["models"]["chat"]
    response = chat_llm.invoke(state["messages"])
    return {
        "message": [AIMessage(content=response.content)],
        "final_answer": response.content,
    }

def _extract_file_content(uploadedfile: UploadedFile, save_path: str = None) -> Sequence[str]:
    _tmp_one_file_texts:str = uploadedfile.read().decode("utf-8", errors = "ignore")
    pattern: str = "|".join(["\n", "\n\n"])
    chunks: Sequence[str] = re.split(pattern = pattern, string = _tmp_one_file_texts)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    if save_path is not None and os.path.exists(save_path):
      with open(file = f"{save_path}/{uploadedfile.name}", mode = "w", encoding = "utf-8") as f:
        f.write("\n".join(chunks))
    return chunks

def node_parse_file(state: AppState) -> Dict[str, Any]:
    uploaded = state.get("uploaded_file", None)
    if uploaded is None:
        msg = "未检测到上传文件，请先通过页面选择文件。"
        return {
            "messages": [AIMessage(content=msg)],
            "file_text": "",
            "final_answer": msg
        }
    context = _extract_file_content(uploaded)
    if context is None:
        msg = "未检测到文件内容，请检查文件。"
        return {
            "messages": [AIMessage(content=msg)],
            "file_text": "",
            "final_answer": msg
        }
    return {"file_text": context}

def node_rag(state: AppState, config: RunnableConfig) -> Dict[str, Any]:
    user_q = _get_user_input(state = state)
    sys_prompt = (
        "你将根据【文档内容】回答用户问题。\n"
        "若文档未涵盖，明确说明并仅基于文档给出可验证的结论；必要时给出下一步建议。\n"
    )
    composed_messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"文档内容（节选，可不完整）：\n{state.get('file_text','')[:6000]}"},
        {"role": "user", "content": f"用户问题：\n{user_q}"}
    ]
    qa_llm: ChatOpenAI = config["configurable"]["models"]["qa"]
    res = qa_llm.invoke(composed_messages)
    return {"messages": [AIMessage(content=res.content)], "final_answer": res.content}

# ============== 条件路由 ==============
def route_by_intent(state: AppState) -> Literal["chat", "parse_file"]:
    """
    根据 state['branch'] 决定走向
    """
    return "chat" if state.get("branch", 0) == 0 else "parse_file"

def build_graph():
    builder = StateGraph(AppState)
    builder.add_node("intent", node_intent)
    builder.add_node("chat", node_chat)
    builder.add_node("parse_file", node_parse_file)
    builder.add_node("answer_with_file", node_rag)

    builder.add_edge(START, "intent")
    # 条件分支：intent -> chat / parse_file
    builder.add_conditional_edges("intent", route_by_intent, {"chat": "chat", "parse_file": "parse_file"})
    # 文件流：parse_file -> answer_with_doc -> END
    builder.add_edge("parse_file", "answer_with_file")
    builder.add_edge("chat", END)
    builder.add_edge("answer_with_file", END)

    graph = builder.compile()
    return graph

if __name__ == "__main__":
    graph = build_graph()
    from factory.cmdi import CMDIFactory
    with Client(
        base_url = st.secrets["DEEP_URL"],
        headers  = {"Authorization": f"Bearer {st.secrets['APPCODE_KEY']}"},
        timeout  = Timeout(30),
    ) as client:
        intent_model: ChatOpenAI = CMDIFactory.get_instance(
            base_url=st.secrets["DEEP_URL"],
            api_key=st.secrets["APPCODE_KEY"]
        ).build(
            model = "DeepSeekR1",
            temperature = 0.7,
            max_tokens = 4096,
            client = client
        )
        chat_model: ChatOpenAI = CMDIFactory.get_instance(
            base_url=st.secrets["DEEP_URL"],
            api_key=st.secrets["APPCODE_KEY"]
        ).build(
            model = "DeepSeekR1",
            temperature = 0.7,
            max_tokens = 4096,
            client = client
        )
        qa_model: ChatOpenAI = CMDIFactory.get_instance(
            base_url=st.secrets["DEEP_URL"],
            api_key=st.secrets["APPCODE_KEY"]
        ).build(
            model = "DeepSeekR1",
            temperature = 0.7,
            max_tokens = 4096,
            client = client
        )

        models = {"intent": intent_model, "chat": chat_model, "qa": qa_model}

        result: Dict[str, Any] = graph.invoke(
            {
                "messages": [HumanMessage(content="你好，我是小娜，请问有什么问题可以帮您？")],
            },
            config={"configurable": {"models": models}}
        )
        print(result["final_answer"])