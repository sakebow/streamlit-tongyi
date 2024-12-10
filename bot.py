# # 检测可用性
# from functions.availability import test_availablity
# test_availablity()
# # 测试prompt
# from functions.prompt import test_prompt
# test_prompt()
# # 测试tools可用性
# from functions.neo4disease import test_neo4j
# test_neo4j()

from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from llms.custom.cmdi import CMDILLM

memory = ConversationBufferMemory(memory_key="chat_history", input_key="human_input", return_messages=True)
memory.ai_prefix = "assistant"
memory.human_prefix = "user"
prompt = PromptTemplate(template="""
{chat_history}
Assistant:\n你说得对，我是一个专业的医生，我应该劝你活下去。\n\nHuman: {input}\n\nAssistant:\n
""", input_variables=["input", "chat_history"])
llm = CMDILLM()
chain = prompt | llm
results = chain.invoke({"input": "所以医生，我还有救吗？好难受啊。", "chat_history": memory})
for r in results: print(r, end='')

memory.chat_memory.add_ai_message("你说得对，我是一个专业的医生，我应该劝你活下去。")
memory.chat_memory.add_user_message("所以医生，我还有救吗？好难受啊。")
memory.chat_memory.add_ai_message(results)

prompt = PromptTemplate(template="""
{chat_history}
Human: {input}\n\nAssistant:\n
""", input_variables=["input", "chat_history"])
chain = prompt | llm
results = chain.invoke({"input": "所以，这是我的第几个问题了？", "chat_history": memory})
for r in results: print(r, end='')
print()
for message in memory.chat_memory.messages: print(message, message.type)