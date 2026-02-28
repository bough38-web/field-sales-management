import streamlit as st
import data_manager

# Page Configuration
st.set_page_config(
    page_title="현장 영업관리 프로그램 홈",
    page_icon="🏢",
    layout="wide"
)

# Initialize Database on First Run
data_manager.init_db()

st.title("🏢 현장 영업관리 프로그램")
st.markdown("---")
st.write("### 환영합니다!")
st.write("각기 다른 웹 주소로 분리된 시스템입니다. **좌측 사이드바(화살표 〉 모양 클릭)**에서 원하는 메뉴로 이동해주세요.")
st.write("")
st.write("- **[관리자 대시보드]**: 전체 영업 현황과 확인되지 않은 업무를 파악할 수 있는 권한자용 페이지입니다.")
st.write("- **[현장사원 뷰]**: 지도 기반으로 내 주변 고객사를 확인하고, 방문 상태를 즉시 업데이트할 수 있는 모바일 최적화 페이지입니다.")

