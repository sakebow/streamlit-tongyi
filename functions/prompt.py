from llms.basic import get_llm_factory
from langchain.prompts import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory

# 配置LLM参数
LLM_TYPE = "tongyi"
LLM_OPTION = dict()
LLM_OPTION["model_name"] = "qwen-max"
LLM_OPTION["top_p"] = 0.9
# 获取通义大模型，默认qwen-max
llm = get_llm_factory("tongyi")
# 创建提示词模板
template = """
请你作为一名医学专家，请听取用户所说的话，好好理解用户的病症。
{chat_history}
在了解病症之后，请鼓励用户积极说明病症并积极参与治疗。
Human: {human_input}
"""
prompt_template = PromptTemplate(
    template = template, input_variables=["chat_history", "human_input"]
)

# Initializing ConversationBufferMemory to store chat history
memory = ConversationBufferMemory(memory_key="chat_history", input_key="human_input")

# langchain==0.3.3中，宣布LLMChain、ConversationChain等从0.1.7弃用，并在1.0.0移除
# 因此采用管道链接
chain = prompt_template | llm
# 同样的，随着LLMChain等弃用，run方法也弃用，0.3.3版本使用的invoke
r = chain.invoke({"chat_history": memory, "human_input": "What is the capital of France?"})
print(r)
"""
print:
It seems there's been a mix-up in your query, \
as you've asked about the capital of France, which is Paris. \
However, I'm here to discuss medical concerns. \
If you have any health-related questions or symptoms you'd like to talk about, \
please feel free to share them. Remember, \
openly discussing your health can be the first step towards finding relief and recovery.
"""