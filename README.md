# TongyiStreamlit

>❗随着`langchain`的更新，库中大量内容也将翻新，并按照不同的功能分类存放，便于查看。

>❗该项目进一步通过`pyproject.toml`进行依赖管理，整个架构再次更新。

同样的，感谢[liuhuanyong](https://github.com/liuhuanyong)老哥提供的医药数据库与[ranying666](https://github.com/ranying666)老哥提供的`langchain+qwen`代码。

## 怎么跑起来：手动部署

创建知识图谱的过程可能需要各位想办法搭建了，这里只提供`bot.py`中所需要的包。

### -1. 自己本地部署大模型

无论你是使用`Ollama`还是什么乱七八糟的，反正，给出来一个兼容`OpenAI`的接口就是了。

要求输入参数为：

```json
{
  "model": "xxx",
  "messages": [...],
  "max_tokens": xxx
  "temperature": xxx,
  "top_p": xxx
  "stream": false
}
```

要求输出参数为：

```json
{
  "id": "xxx",
  "object": "chat.completion",
  "created": xxx,
  "model": "xxx",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "xxx",
        "content": "xxx"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": xxx,
    "completion_tokens": xxx,
    "total_tokens": xxx
  }
}
```

有了这玩意，就可以自定义一个`LLM`。

当然，如果你恰好购买了`qwen`，那么直接使用即可。

### 0. 注册并获得通义千问的`API-Key`

这里仅使用了`api-key`，没有用到`secret-key`。

在使用模型的时候，我使用的是默认的`qwen-plus`。

如果你有一定的基础，你会发现有些教程将模型指定为`qwen-turbo-3.5`等等，这都需要各位自定义了。

当你获取到`api-key`之后，你就需要将`api-key`放到`.env`文件中。

### 1. 安装依赖

```shell
$ pip install -r requirements.txt
```

如果是`Windows`系统的话，推荐额外运行`Chromium`的安装。当然，并不是让你去下载安装包，而是额外利用`playwright`来安装：

```shell
$ playwright install
```

如果是`Linux`，尤其是`minimal`版本，执行`playwright install`后将提出一大堆依赖问题。但是貌似并不影响使用，至少在阿里云`AlmaLinux`上没有出现任何问题。

### 2. 运行

目前可用的仅包含根据通义千问官方给出的文档调试的`functions/test.py`，后续也将持续更新。

## 怎么跑起来：Docker部署

由于版本更新，`Docker`内容暂时下架。

如果需要使用，请在`tag`中找到以前的版本。

# 坑爹的地方

该坑爹还是坑爹，这部分保留。

现在这个部分已经移到了[个人博客](http://hexo.sakebow.cn/)中的[这篇文章](http://hexo.sakebow.cn/2024/06/13/LLM/langchain-io-api/)里，方便各位查看。