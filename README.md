# TongyiStreamlit

>❗随着`langchain`的更新，库中大量内容也将翻新，并按照不同的功能分类存放，便于查看。
>
>❗`poetry`与`conda`会冲突，由于已经用了`conda`，不再强行转为`poetry`管理，重回`conda`管理。
>
>❗发现了部分智能体接入`OpenAI`智能体的方法，整个架构再次更新。
>
>❗发现了MCP接入的方法，`streamlit`被删除，整个架构再次更新为纯后端。
>
> 感谢[liuhuanyong](https://github.com/liuhuanyong)老哥提供的医药数据库与[ranying666](https://github.com/ranying666)老哥提供的`langchain+qwen`代码。

# 依赖安装

>❗本项目目前测试<span style="color:green">**通过**</span>的环境为：
>
> |key|value|
> |---|---|
> |python|>=3.12|
> |OS|AlmaLinux 9.5 x86_64|
>
>❗本项目目前测试<span style="color:red">**失败**</span>的环境为：
>
> |key|value|
> |---|---|
> |python|>=3.12|
> |OS|Windows 11 x86_64|
> 
> 原因：本项目依赖`pymilvus`，而`pymilvus`目前明确不支持`Windows`，明确支持`Ubuntu`与`MacOS`。本项目于`AlmaLinux`环境中走到这一步完全是凭运气
> 
> （*首*）：哼，哼，哼，啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊

最开始的开始，当然是下载代码：

```bash
$ git clone https://github.com/sakebow/streamlit-tongyi.git
```
0. 使用`conda`安装依赖包

```bash
$ conda create -n vllm python=3.12 -y
$ conda activate vllm
$ pip install -r requirements.txt
```

# 参数配置

目前项目的配置文件更换为`.env`文件。其中的配置项有：

|数据项|描述|默认值|是否必须
|:--:|:--:|:--:|:---:|
|DASHSCOPE_API_KEY|通义千问的api-key|无||
|DASH_URL|通义千问接入OpenAI的URL|无||
|DEEP_URL|自定义大模型接入OpenAI的URL|无||
|BGEM_URL|自定义词嵌入模型接入OpenAI的URL|无||
|APPCODE_KEY|自定义大模型的api-key|无||
|TIMEOUT|自定义大模型网络请求客户端的超时时间（秒）|30|是|
|NEO4J_ADDR|Neo4j数据库的ip|无|否|
|NEO4J_PORT|Neo4j数据库的端口|无|否|
|NEO4J_USER|Neo4j数据库的用户名|无|否|
|NEO4J_PASS|Neo4j数据库的密码|无|否|
|REDIS_ADDR|Redis数据库的ip|无|否|
|REDIS_PORT|Redis数据库的端口|无|否|

其中，通义千问大模型与自定义大模型的URL与api-key需要二选一，或者都要。

# 项目体验

使用脚本或者`IDE`执行`server.py`文件，即可启动项目中的示例。

启动后，暴露端口$8000$。

使用`curl`、`apifox`等客户端请求即可查看实例。下面给出`curl`的示例：

```python
curl -N -X POST http://localhost:8000/mcp \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
--data '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {},
        "clientInfo": {
            "name": "curl", "version": "8.8"
        }
    }
}'
```

该步骤完成了一个`initialize`的请求，主要是获得其中的`Mcp-Session-Id`。然后就可以继续访问`MCP`方法。