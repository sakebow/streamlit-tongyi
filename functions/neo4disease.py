from llms.basic import get_llm_factory
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from tools.dbhelper import DiseaseExtractionRunnable
def test_neo4j():
  llm = get_llm_factory("tongyi")
  memory = ConversationBufferMemory(memory_key="chat_history", input_key="human_input")
  entity_extraction_prompt = PromptTemplate(
    input_variables = ["text"],
    template = "请从以下文本中提取病症名称，用逗号分隔多个病症：{text}"
  )
  entity_extraction_chain = entity_extraction_prompt | llm
  template = """
  请你作为一名医学专家，请听取用户所说的话，好好理解用户的病症。
  {chat_history}
  {neo4j_results}
  在了解病症之后，请鼓励用户积极说明病症并积极参与治疗。
  Human: {human_input}
  """
  prompt_template = PromptTemplate(
    template = template,
    input_variables = ["chat_history", "human_input", "neo4j_results"]
  )
  chain = DiseaseExtractionRunnable(chain = entity_extraction_chain, memory = memory) | prompt_template | llm
  human_input = "我最近头痛得厉害，不知道是不是感冒了。"
  response = chain.invoke({"chat_history": memory, "human_input": human_input})
  print(response)
  memory.save_context({"human_input": human_input}, {"output": response})