import streamlit as st

st.title("数字员工智能助手")
st.logo("assets/horizontal_blue.png", icon_image="assets/icon_blue.png")

main_page = st.Page("ui/main.py", title = "主页面", icon = ":material/home:", default = True)
basic_page = st.Page("ui/basic.py", title = "ChatRender", icon = ":material/chat:")
update_basic_page = st.Page("ui/update_basic.py", title = "ChatRenderCallbackHandler", icon = ":material/comment:")

pg = st.navigation({"主页面": [main_page], "测试页面": [
    basic_page,
    update_basic_page
]})
pg.run()