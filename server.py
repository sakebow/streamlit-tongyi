# server.py
from fastmcp import FastMCP
from workflow.example import build_graph

mcp = FastMCP("HelloWorldGraph")

@mcp.tool()
async def run_graph(text: str) -> str:
    """
    Run the multi-node graph and stream SSE events:
    node-start, node-delta, node-end
    """
    graph = build_graph()
    writer = mcp.get_stream_writer()      # FastMCP utility
    async for mode, chunk in graph.astream(
        {"text": text},
        stream_mode=["updates", "messages", "custom"]
    ):
        node = chunk.get("node") or mode     # simplistic tag
        if mode == "updates" and chunk.get("branch") is not None:
            # intent finished → kick off branch node
            continue
        if mode == "custom":                 # token from writer()
            writer({"phase": "delta", "node": node, "text": chunk})
        elif mode == "messages":             # LLM token
            writer({"phase": "delta", "node": node, "text": chunk[0]})
        elif mode == "updates":              # node done
            writer({"phase": "end", "node": node})
    return "done"

if __name__ == "__main__":
    # Streamable HTTP = HTTP + SSE per MCP spec
    mcp.run(transport="http", port=8000, path="/mcp")
    """
    启动服务后，请使用如下命令进行测试：
    curl -N -X POST http://localhost:8000/mcp/ \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    --data '{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": { "name": "curl", "version": "8.8" }
        }
    }'
    其中需要额外注意的是：
    1. URL的末尾一定有斜线：/mcp/，如果没有，则会导致307
    2. 请求头中的Accept字段必须是：application/json, text/event-stream
        2.1. 不可以将他们单独设置，否则中间的分隔符号会变成`;`，导致406
        2.2. 必须是两个同时有，否则会导致406
    3. jsonrpc只有2.0这个选项
    4. id自定义但不可为空
    5. method是指要调用的RPC方法名
        5.1. method不是指代码中的方法名，而是指RPC方法名
        5.2. 此处参数只有固定的选项，initialize是其中之一
    6. params是与方法绑定的参数对象
        6.1. 同样的，不是指代码中的方法名，而是指RPC方法名
        6.2. protocolVersion一般选择2025-03-26
        6.3. capabilities表明期望启动的特性，同样只有固定的选项
        6.4. clientInfo是客户端元数据
    
    完成上述命令之后，仅完成握手，即能力调研
    """
