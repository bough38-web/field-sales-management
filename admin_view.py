import streamlit as st
import data_manager
import pandas as pd
import plotly.express as px
import threading

def render_admin_dashboard():
    st.title("📊 관리자 대시보드")
    
    # --- Dynamic Excel Upload & Mapping Section ---
    with st.expander("📥 엑셀 데이터 업로드 및 컬럼 매핑 (전문가용)", expanded=False):
        st.write("새로운 엑셀 데이터를 업로드하고, 우리 시스템에 맞게 컬럼을 지정하여 반영합니다.")
        uploaded_file = st.file_uploader("엑셀 파일 선택 (.xlsx)", type=['xlsx'])
        
        if uploaded_file is not None:
            try:
                raw_df = pd.read_excel(uploaded_file)
                excel_cols = raw_df.columns.tolist()
                st.success(f"파일 로드 성공! 총 {len(raw_df)}행, {len(excel_cols)}개의 컬럼이 발견되었습니다.")
                
                # Define Fields to Map
                fields_to_map = {
                    'Branch': '지사 (Branch)',
                    'Contract No': '계약번호 (Contract No)',
                    'Company Name': '상호명 (Company Name)',
                    'Monthly Fee': '월정료 (Monthly Fee)',
                    'Manager': '담당사원 (Manager)',
                    'Contact': '연락처 (Contact)',
                    'Address': '설치주소 (Address)',
                    'Stop Reason': '정지사유 (Stop Reason)',
                    'Stop Start Date': '정지시작일자 (Stop Start Date)',
                    'Stop Days': '당월말 정지일수 (Stop Days)'
                }
                
                # Helper for auto-guessing mapped column
                def guess_index(field_key, cols):
                    hints = {
                        'Branch': ['지사', '본부', 'branch'],
                        'Contract No': ['계약번호', '계약', '번호', 'contract'],
                        'Company Name': ['상호', '고객사', '이름', 'name', 'company'],
                        'Monthly Fee': ['월정료', '금액', 'fee'],
                        'Manager': ['사원', '담당자', 'manager'],
                        'Contact': ['휴대폰', '연락처', '전화번호', 'phone', 'contact'],
                        'Address': ['주소', '설치주소', 'address'],
                        'Stop Reason': ['정지사유', '사유', 'reason'],
                        'Stop Start Date': ['정지시작일자', '정지일자', 'date'],
                        'Stop Days': ['당월말_정지일수', '정지일수', 'days']
                    }
                    for i, col in enumerate(cols):
                        for hint in hints.get(field_key, []):
                            if hint in str(col).lower():
                                return i
                    return 0
                
                mapping_result = {}
                col1, col2 = st.columns(2)
                for i, (field_key, display_name) in enumerate(fields_to_map.items()):
                    with col1 if i % 2 == 0 else col2:
                        default_idx = guess_index(field_key, excel_cols)
                        mapping_result[field_key] = st.selectbox(
                            display_name, 
                            options=excel_cols, 
                            index=default_idx, 
                            key=f"map_{field_key}"
                        )
                        
                if st.button("적용 및 지오코딩(좌표변환) 시작", type="primary", use_container_width=True):
                    with st.spinner("데이터를 변환하고 좌표를 가져오는 중입니다. 잠시만 기다려주세요..."):
                        # Process and save DB
                        mapped_df = data_manager.apply_custom_mapping(raw_df, mapping_result)
                        
                        # Generate Lat/Lng
                        data_manager.geocode_missing(mapped_df)
                        
                    st.success("데이터 적용 및 좌표 변환이 완료되었습니다!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"파일을 읽거나 처리하는 중 오류가 발생했습니다: {e}")
    # --- End Upload Section ---
    
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
        st.plotly_chart(fig, use_container_width=True) # Plotly chart might still use it, we will keep it for plotly to be safe. 

    with chart_col2:
        st.subheader("⚠️ 미확인 사원 리스트 (Action Required)")
        unchecked_df = df[df['Status'] == '미확인']
        
        if len(unchecked_df) > 0:
            st.warning(f"총 {len(unchecked_df)}건의 미확인 항목이 있습니다.")
            st.dataframe(
                unchecked_df[['Branch', 'Manager', 'Company Name', 'Contact']],
                width='stretch',
                hide_index=True
            )
        else:
            st.success("모든 사원이 업무를 확인했습니다.")

    st.markdown("---")
    st.subheader("전체 데이터 보기")
    st.dataframe(df, width='stretch')
