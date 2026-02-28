import streamlit as st
from admin_view import render_admin_dashboard
import data_manager

# Page Configuration for Admin
st.set_page_config(page_title="관리자 대시보드", page_icon="📊", layout="wide")

# Ensure DB is initialized
data_manager.init_db()

# Render the Admin Dashboard
render_admin_dashboard()
