import streamlit as st

from utils.page_content import get_markdown_content

st.markdown(get_markdown_content(__file__))