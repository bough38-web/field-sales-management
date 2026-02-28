import streamlit as st
import data_manager

# Page Configuration
st.set_page_config(
    page_title="현장 영업관리 프로그램 로그인",
    page_icon="🏢",
    layout="centered"
)

# Initialize Database on First Run
data_manager.init_db()

# Initialize Session State
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'role' not in st.session_state:
    st.session_state['role'] = None

st.title("🏢 현장 영업관리 시스템")
st.markdown("---")
st.write("보안을 위해 역할을 선택하고 비밀번호를 입력해주세요.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("👨‍💼 관리자 로그인")
    st.caption("초기 비밀번호: admin123")
    admin_pw = st.text_input("관리자 비밀번호", type="password", key="admin_pw")
    if st.button("관리자 접속", use_container_width=True):
        if admin_pw == "admin123":
            st.session_state['authenticated'] = True
            st.session_state['role'] = 'admin'
            st.success("로그인 성공!")
            st.switch_page("pages/1_Admin_Dashboard.py")
        else:
            st.error("비밀번호가 일치하지 않습니다.")

with col2:
    st.subheader("🏃‍♂️ 현장사원 로그인")
    st.caption("초기 비밀번호: field123")
    field_pw = st.text_input("사원 비밀번호", type="password", key="field_pw")
    if st.button("현장사원 접속", use_container_width=True):
        if field_pw == "field123":
            st.session_state['authenticated'] = True
            st.session_state['role'] = 'field'
            st.success("로그인 성공!")
            st.switch_page("pages/2_Field_Staff_View.py")
        else:
            st.error("비밀번호가 일치하지 않습니다.")

