# TongyiStreamlit

这个项目初步设想大概是这样：

![初步设想](http://images.sakebow.cn/experience/qwen-bot/bot.png)

简单地说，这个项目就是在`streamlit`上搭建一个聊天机器人。[点击这里跳转到体验链接](http://120.26.106.143:8501/)。

目前已经完成了通义千问的接入。

尤其感谢[liuhuanyong](https://github.com/liuhuanyong)老哥提供的医药数据库与[ranying666](https://github.com/ranying666)老哥提供的`langchain+qwen`代码。

## 为什么做

主要是想尝试一下自己的想法。毕竟这也只是一个相当基础的想法，开源出来也没什么大不了的。

在通义千问的基础上，额外添加了一个中医知识图谱。数据集来源：[以疾病为中心的一定规模医药领域知识图谱](https://github.com/liuhuanyong/QASystemOnMedicalKG)

## 怎么跑起来：手动部署

创建知识图谱的过程可能需要各位想办法搭建了，这里只提供`bot.py`中所需要的包。

0. **注册并获得通义千问的`API-Key`**

这里仅使用了`api-key`，没有用到`secret-key`。

在使用模型的时候，我使用的是默认的`qwen-plus`。

如果你有一定的基础，你会发现有些教程将模型指定为`qwen-turbo-3.5`等等，这都需要各位自定义了。

当你获取到`api-key`之后，你就需要将`api-key`放到`.env`文件中。

1. **安装依赖**

```shell
$ pip install -r requirements.txt
```

如果是`Windows`系统的话，推荐额外运行`Chromium`的安装。当然，并不是让你去下载安装包，而是额外利用`playwright`来安装：

```shell
$ playwright install
```

如果是`Linux`，尤其是`minimal`版本，执行`playwright install`后将提出一大堆依赖问题。但是貌似并不影响使用，至少在阿里云`AlmaLinux`上没有出现任何问题。

2. **运行**

如果你暂时还不确定效果如何，那就直接运行：

```shell
$ streamlit run bot.py
```

如果出现什么问题，问题将很详细地打印在终端里。

当你觉得没什么问题之后，就可以挂在后台了：

```shell
$ nohup streamlit run bot.py > /var/log/bot.log 2>&1 &
```

别忘了把防火墙打开，如果是云服务器的话就开启安全组。

打开浏览器，就能访问了。

## 怎么跑起来：Docker部署

我目前准备了一个`Dockerfile`。执行也很简单：

```shell
$ sudo docker build -t streamlit/tongyi:v1 .
$ sudo docker run -d -p 8501:8501 --name tongyi-streamlit streamlit/tongyi:v1
```

# 坑爹的地方

现在这个部分已经移到了[个人博客](http://hexo.sakebow.cn/)中的[这篇文章](http://hexo.sakebow.cn/2024/06/13/LLM/langchain-io-api/)里，方便各位查看。