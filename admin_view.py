import streamlit as st
import data_manager
import plotly.express as px

def render_admin_dashboard():
    st.title("📊 관리자 대시보드")
    
    # Reload data
    df = data_manager.get_data()
    
    # KPIs
    st.header("실시간 현황")
    col1, col2, col3 = st.columns(3)
    total_contracts = len(df)
    completed_contracts = len(df[df['Status'] == '완료'])
    in_progress_contracts = len(df[df['Status'] == '진행중'])
    
    col1.metric("총 계약 대상", f"{total_contracts} 건")
    col2.metric("완료", f"{completed_contracts} 건")
    col3.metric("진행중", f"{in_progress_contracts} 건")
    
    st.markdown("---")
    
    # Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("전체 진척도")
        status_summary = df['Status'].value_counts().reset_index()
        status_summary.columns = ['상태', '건수']
        fig = px.pie(status_summary, values='건수', names='상태', hole=0.3,
                     color='상태', color_discrete_map={'완료':'blue', '진행중':'orange', '미확인':'red'})
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        st.subheader("⚠️ 미확인 사원 리스트 (Action Required)")
        unchecked_df = df[df['Status'] == '미확인']
        
        if len(unchecked_df) > 0:
            st.warning(f"총 {len(unchecked_df)}건의 미확인 항목이 있습니다.")
            st.dataframe(
                unchecked_df[['Branch', 'Manager', 'Company Name', 'Contact']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("모든 사원이 업무를 확인했습니다.")

    st.markdown("---")
    st.subheader("전체 데이터 보기")
    st.dataframe(df, use_container_width=True)
