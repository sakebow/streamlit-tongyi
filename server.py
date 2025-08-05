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
    curl -N -X POST http://localhost:2024/mcp \
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

    """
