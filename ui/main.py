import streamlit as st

from utils import ContentHelper

st.markdown(ContentHelper.get_markdown_content(__file__))