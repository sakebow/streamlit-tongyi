# hello_world_graph.py
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from langgraph.config import get_stream_writer   # lets us emit custom chunks

class Input(TypedDict): text: str
class Output(TypedDict): branch: int | None; answer: str
class State(Input, Output): ...

def detect_intent(state: Input) -> Output:
    # trivial intent: odd length ⇒ branch 0 else branch 1
    return {"branch": len(state["text"]) % 2, "answer": ""}

def hello_node(state: State) -> Output:
    writer = get_stream_writer()                # <─ custom stream hook
    for ch in "<think>Helloing…</think>":
        writer(ch)                              # token-level delta
    return {"answer": f"Hello，{state['text']}"}

def world_node(state: State) -> Output:
    writer = get_stream_writer()
    for ch in "<think>Worlding…</think>":
        writer(ch)
    return {"answer": f"{state['text']} world!"}

def build_graph() -> StateGraph:
    sg = StateGraph(State)
    sg.add_node("intent", detect_intent)
    sg.add_node("hello", hello_node)
    sg.add_node("world", world_node)
    sg.add_conditional_edges("intent", lambda s: "hello" if s["branch"] else "world")
    sg.add_edge(START, "intent")
    sg.add_edge("hello", END)
    sg.add_edge("world", END)
    graph = sg.compile()
    return graph

if __name__ == "__main__":
    graph: StateGraph = build_graph()
    print(graph.invoke({"text": "LangGraph"}))