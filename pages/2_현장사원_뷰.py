import streamlit as st
from field_view import render_field_sales_view
import data_manager

# Page Configuration for Field Staff
st.set_page_config(page_title="현장사원 뷰", page_icon="🏃‍♂️", layout="wide")

# Ensure DB is initialized
data_manager.init_db()

# Render the Field Staff View
render_field_sales_view()
