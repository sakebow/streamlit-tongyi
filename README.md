# TongyiStreamlit

>❗随着`langchain`的更新，库中大量内容也将翻新，并按照不同的功能分类存放，便于查看。
>
> ~~❗该项目进一步通过`pyproject.toml`进行依赖管理，整个架构再次更新。~~
>
>❗`poetry`与`conda`会冲突，由于已经用了`conda`，不再强行转为`poetry`管理，重回`conda`管理。
>
>❗发现了部分智能体接入`OpenAI`智能体的方法，整个架构再次更新。

同样的，感谢[liuhuanyong](https://github.com/liuhuanyong)老哥提供的医药数据库与[ranying666](https://github.com/ranying666)老哥提供的`langchain+qwen`代码。

## 依赖安装

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

~~由于`poetry`的引入，因此依赖安装过程稍有变化，请按照以下步骤进行安装：~~

~~0. 若未使用`conda`，则直接跳转到步骤 $1$ ；若已安装`conda`，请不要卸载`conda`，直接利用虚拟环境执行依赖安装过程：~~
0. 若未使用`conda`，则使用方式二 ；若已安装`conda`，请使用方式一。

方式一：

```bash
$ conda create -n llm python=3.12 -y
$ conda activate llm
$ pip install -r requirements.txt
```

方式二：

1. 安装`poetry`：

```bash
$ pip install poetry
```

2. 安装项目依赖：

```bash
$ poetry install
```

## 参数配置

项目的`.streamlit`文件夹中存在配置文件`secrets.toml`，配置其中所需要的参数即可。

目前必须要有的参数只有一个：`DASHSCOPE_API_KEY`，用于调用`DashScope`的`API`。各位可以[移步此处](https://bailian.console.aliyun.com/)进行申请或购买。

另外的参数暂时不是必须的，目前提供功能的只有：`APPCODE_TYP`、`APPCODE_KEY`、`NEO4J_ADDR`、`NEO4J_PORT`、`NEO4J_USER`、`NEO4J_PASS`、`BASE_URL`、`OPEN_URL`。

其中：

- `NEO4J_ADDR`、`NEO4J_PORT`、`NEO4J_USER`、`NEO4J_PASS`用于提供知识图谱服务
  - 主要方便用户自行添加知识图谱。
- `APPCODE_TYP`、`APPCODE_KEY`、`BASE_URL`、`OPEN_URL`提供自定义大模型服务
  - 主要方便用户自行添加`MindIE`部署的大模型服务；
  - 或者其他大模型，只要返回结果兼容`OpenAI`格式即可；
  - 目前测试通过的大模型有：
    - 九天大模型

## 项目体验

当然，体验之前需要各位最起码购买了阿里云百炼的`api-key`，或者说本地已经部署了一个大模型。

把参数写入配置文件，就可以运行看看了：

```shell
$ streamlit run app.py
```