import streamlit as st
from admin_view import render_admin_dashboard
import data_manager

# Page Configuration for Admin
st.set_page_config(page_title="관리자 대시보드", page_icon="📊", layout="wide")

# Authentication Check
if not st.session_state.get('authenticated') or st.session_state.get('role') != 'admin':
    st.warning("접근 권한이 없습니다. 메인 페이지에서 관리자로 로그인해주세요.")
    if st.button("로그인 페이지로 돌아가기"):
        st.switch_page("app.py")
    st.stop()

# Ensure DB is initialized
data_manager.init_db()

# Render the Admin Dashboard
render_admin_dashboard()
