import streamlit as st

# st.set_page_config(page_title = "数字员工智能助手", page_icon = ":hotdog:", layout = "wide")
st.title("数字员工智能助手")
st.logo("assets/horizontal_blue.png", icon_image="assets/icon_blue.png")

main_page = st.Page("ui/main.py", title = "主页面", icon = ":material/home:", default = True)
tongyi_page = st.Page("ui/dashscope.py", title = "阿里通义大模型", icon = ":material/cloud:")
# cmdi_page = st.Page("ui/memory_test.py", title = "九天大模型", icon = ":material/public:")
# mmm_page = st.Page("ui/mmm.py", title = "阿里多模态大模型", icon = ":material/public:")

pg = st.navigation({"主页面": [main_page], "大模型": [
    tongyi_page,
    # mmm_page
]})
pg.run()