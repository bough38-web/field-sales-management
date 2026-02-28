import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from scipy.spatial.distance import cdist
import data_manager

def optimize_route(current_lat, current_lng, target_df):
    if len(target_df) == 0:
        return target_df
    current_pos = [[current_lat, current_lng]]
    targets = target_df[['Latitude', 'Longitude']].values
    
    distances = cdist(current_pos, targets, 'euclidean')
    target_df = target_df.copy()
    target_df['Distance'] = distances[0]
    
    return target_df.sort_values(by='Distance')

def render_field_sales_view():
    st.title("🏃‍♂️ 현장사원 앱")
    
    df = data_manager.get_data()
    managers = df['Manager'].unique().tolist()
    
    # Manager Selection (Mock Login)
    selected_manager = st.selectbox("사원 선택 (로그인 시뮬레이션)", managers)
    
    # Filter Data
    my_df = df[df['Manager'] == selected_manager].copy()
    
    if len(my_df) == 0:
        st.info("할당된 고객사가 없습니다.")
        return
        
    # Mock Current Location (using the first location for demo purposes, offset slightly)
    current_lat = my_df.iloc[0]['Latitude'] - 0.01
    current_lng = my_df.iloc[0]['Longitude'] - 0.01
    
    st.subheader("📍 방문 리스트 및 최적 경로")
    optimized_df = optimize_route(current_lat, current_lng, my_df)
    
    # Tabs for Map / List
    tab1, tab2 = st.tabs(["지도 보기", "리스트 보기 (상태 변경)"])
    
    with tab1:
        # Folium Map
        m = folium.Map(location=[current_lat, current_lng], zoom_start=12)
        
        # Add Current Location Marker
        folium.Marker(
            location=[current_lat, current_lng],
            popup="<b>내 위치</b>",
            icon=folium.Icon(color='black', icon='user')
        ).add_to(m)
        
        # Add Customer Markers
        for _, row in optimized_df.iterrows():
            if row['Status'] == '미확인':
                color = 'red'
            elif row['Status'] == '진행중':
                color = 'orange'
            else:
                color = 'blue'
                
            popup_html = f"<b>{row['Company Name']}</b><br>상태: {row['Status']}"
            
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=row['Company Name'],
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(m)
            
        st_data = st_folium(m, width=800, height=500)
    
    with tab2:
        st.caption("고객사를 클릭하여 상세 정보 확인 및 상태를 업데이트 하세요.")
        for _, row in optimized_df.iterrows():
            with st.expander(f"🏢 {row['Company Name']} - 현재 상태: [{row['Status']}]"):
                st.write(f"**연락처**: {row['Contact']}")
                st.write(f"**주소**: {row['Address']}")
                st.write(f"**월정료**: {row['Monthly Fee']:,}원")
                st.write(f"**현재 위치로부터 거리**: {row['Distance']*111:.2f} km (예상치)") # Rough conversion degree to km
                
                # Status Change Actions
                st.write("---")
                st.write("**상태 변경하기**")
                
                col1, col2, col3 = st.columns(3)
                
                def make_update_callback(contract_no, status):
                    def callback():
                        data_manager.update_status(contract_no, status)
                    return callback
                
                # Use callbacks to update state and trigger rerun
                with col1:
                    st.button("진행전(미확인)", key=f"btn_un_{row['Contract No']}", 
                              on_click=make_update_callback(row['Contract No'], "미확인"),
                              use_container_width=True,
                              disabled=row['Status'] == "미확인")
                with col2:
                    st.button("진행중", key=f"btn_ing_{row['Contract No']}",
                              on_click=make_update_callback(row['Contract No'], "진행중"),
                              use_container_width=True,
                              disabled=row['Status'] == "진행중")
                with col3:
                    st.button("완료", key=f"btn_done_{row['Contract No']}",
                              on_click=make_update_callback(row['Contract No'], "완료"),
                              use_container_width=True,
                              disabled=row['Status'] == "완료")
        
        st.info("상태를 변경하면 관리자 대시보드에 즉시 반영됩니다.")
