import streamlit as st
from field_view import render_field_sales_view
import data_manager

# Page Configuration for Field Staff
st.set_page_config(page_title="현장사원 뷰", page_icon="🏃‍♂️", layout="wide")

# Authentication Check
if not st.session_state.get('authenticated') or st.session_state.get('role') not in ['field', 'admin']:
    st.warning("접근 권한이 없습니다. 메인 페이지에서 권한에 맞게 로그인해주세요.")
    if st.button("로그인 페이지로 돌아가기"):
        st.switch_page("app.py")
    st.stop()

# Ensure DB is initialized
data_manager.init_db()

# Hide sidebar for the Field Staff View
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# Render the Field Staff View
render_field_sales_view()
