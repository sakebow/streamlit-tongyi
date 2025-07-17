import streamlit as st

st.title("数字员工智能助手")
st.logo("assets/horizontal_blue.png", icon_image="assets/icon_blue.png")

main_page = st.Page(
    "ui/main.py", title = "主页面", icon = ":material/home:", default = True
)
basic_cmdi_page = st.Page(
    "ui/cmdi/basic.py", title = "ChatRender（自定义大模型）", icon = ":material/chat:",
    url_path = "cmdi-basic"
)
update_basic_cmdi_page = st.Page(
    "ui/cmdi/update_basic.py", title = "ChatRenderCallbackHandler（自定义大模型）", icon = ":material/comment:",
    url_path = "cmdi-update_basic"
)
basic_tongyi_page = st.Page(
    "ui/tongyi/basic.py", title = "ChatRender（通义大模型）", icon = ":material/chat:",
    url_path = "tongyi-basic"
)
update_basic_tongyi_page = st.Page(
    "ui/tongyi/update_basic.py", title = "ChatRenderCallbackHandler（通义大模型）", icon = ":material/comment:",
    url_path = "tongyi-update_basic"
)
pg = st.navigation({
    "主页面": [main_page],
    "自定义大模型测试页面": [
        basic_cmdi_page,
        update_basic_cmdi_page
    ],
    "通义大模型测试页面": [
        basic_tongyi_page,
        update_basic_tongyi_page
    ]
})
pg.run()