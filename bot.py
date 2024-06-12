import asyncio                                                              # 异步处理器
import streamlit as st                                                      # 大模型demo包装器                                           # 读取.env文件
from playwright.async_api import async_playwright                           # 异步控制
from langchain.schema import Document                                       # 网页文档容器
from langchain.chains.llm import LLMChain                                   # 包装一个大模型的类
from langchain_community.llms import Tongyi                                 # 通义千问
from langchain.prompts.prompt import PromptTemplate                         # prompt模板
from langchain.memory import ConversationBufferMemory                       # 聊天记录
from langchain.chains.combine_documents.stuff import StuffDocumentsChain    # 文档信息拼接到prompt
from langchain_community.document_transformers import Html2TextTransformer  # html转text

# 读取api-key
import os
os.environ["DASHSCOPE_API_KEY"] = st.secrets["DASHSCOPE_API_KEY"]

# Page Config
st.set_page_config("中医药问诊小程序", page_icon=":hospital:")

# 爬取过程
async def fetch_page_content(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        content = await page.content()
        await browser.close()
        return content

@st.cache_data
def load_documents(url):
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    html_content = loop.run_until_complete(fetch_page_content(url))
    html2text = Html2TextTransformer()
    document = Document(page_content=html_content)
    docs_transformed = list(html2text.transform_documents([document]))
    return docs_transformed

# Initialize Tongyi LLM and related components
# Template for chatbot's behavior
template = """
你是一个中医方面的专家，请听取用户所说的话，好好理解用户的病症。

{chat_history}

在了解病症之后，你需要额外参考以下文本，然后回答问题。

{text}

最开始请不要强调参考文本中的内容，需要按照用户说明的病症逐步深入。

最后，请鼓励用户积极说明病症并积极参与治疗。

Human: {human_input}
"""

# Creating a prompt template with input variables
prompt = PromptTemplate(
    input_variables=["chat_history", "text", "human_input"],
    template=template
)

# Initializing ConversationBufferMemory to store chat history
memory = ConversationBufferMemory(memory_key="chat_history", input_key="human_input")

# Creating an LLMChain with Tongyi language model
stf_chain = StuffDocumentsChain(
    llm_chain = LLMChain(
        llm=Tongyi(),
        prompt=prompt,
        verbose=True,
        memory=memory,
        output_key="text"
    ),
    document_variable_name="text"
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I'm the GraphAcademy Chatbot! How can I help you?"},
    ]

def write_message(role, content, save=True):
    if save:
        st.session_state.messages.append({"role": role, "content": content})
    with st.chat_message(role):
        st.markdown(content)
# Submit handler
def handle_submit(message):
    with st.spinner('Thinking...'):
        response = stf_chain.run(
            human_input=message,
            chat_history="",
            input_documents=load_documents("http://120.26.106.143:5000/answer?question=心肌炎")
            # input_documents=[
            #     Document(page_content="心肌炎,熟悉一下：心肌炎(myocarditis)是指由各种原因引起的心肌的局限性或弥漫性炎症，\
            #              多种因素如感染、物理和化学因素均可引起心肌炎，所造成的心肌损害的轻重程度差别很大，临床表现各异，\
            #              轻症患者无任何症状，而重症患者可发生心力衰竭、心源性休克甚至猝死。\
            #              大部分患者经治疗可获得痊愈，有些患者在急性期之后发展为扩张型心肌病改变，可反复发生心力衰竭。\
            #              虽然某些心肌炎由于在终期可过渡为充血性或限制性心肌病，而被某些学者视为继发性心肌病，\
            #              但在发病学上心肌炎毕竟是可区分的疾病类型，引起心肌炎的原因很多：感染性因素，\
            #              主要是病毒如柯萨奇病毒、艾柯病毒、流感病毒、腺病毒、肝炎病毒等;细菌如白喉杆菌、链球菌等;\
            #              真菌;立克次体;螺旋体;原虫等。其中病毒性心肌炎最常见。自身免疫性疾病：如系统性红斑狼疮、巨细胞性心肌炎;\
            #              物理因素：如胸部放射性治疗引起的心肌损伤;化学因素：如多种药物如一些抗菌素、肿瘤化疗药物等。")
            # ]
        )
        write_message('assistant', response)

# Display messages in Session State
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

# Handle any user input
if prompt := st.chat_input("What is up?"):
    write_message('user', prompt)
    handle_submit(prompt)
