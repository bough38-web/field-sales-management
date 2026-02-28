import streamlit as st
import pandas as pd
import folium
from folium import plugins
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
        
    # Expert-level Search & Filter Options
    with st.expander("🔍 검색 및 필터 옵션 (전문가 옵션)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            search_query = st.text_input("상호명 검색", placeholder="예: 스타벅스")
        with col2:
            status_filter = st.multiselect(
                "방문 상태 필터", 
                options=['미확인', '진행중', '완료'],
                default=['미확인', '진행중', '완료']
            )
            
    # Apply Filters
    if search_query:
        my_df = my_df[my_df['Company Name'].str.contains(search_query, case=False, na=False)]
    if status_filter:
        my_df = my_df[my_df['Status'].isin(status_filter)]
        
    if len(my_df) == 0:
        st.warning("조건에 맞는 고객사가 없습니다. 필터를 조정해주세요.")
        return
        
    # Default Location (Seoul City Hall) in case all coordinates are NaN
    current_lat = 37.5665
    current_lng = 126.9780
    
    # Try to find the first valid customer location to center the map
    valid_locations = my_df.dropna(subset=['Latitude', 'Longitude'])
    if not valid_locations.empty:
        current_lat = valid_locations.iloc[0]['Latitude'] - 0.01
        current_lng = valid_locations.iloc[0]['Longitude'] - 0.01
    
    st.subheader("📍 방문 리스트 및 최적 경로")
    
    # Filter out NaNs BEFORE route optimization to prevent euclidean distance crash
    optimized_df = optimize_route(current_lat, current_lng, valid_locations)
    
    # We still want to show the invalid ones in the list below, so we'll append them
    invalid_locations = my_df[my_df['Latitude'].isna() | my_df['Longitude'].isna()].copy()
    if not invalid_locations.empty:
        invalid_locations['Distance'] = float('inf') # Put them at the end of the route
        optimized_df = pd.concat([optimized_df, invalid_locations])
        
    # Assign route order to top 15
    optimized_df['Route_Order'] = None
    valid_idx = optimized_df[optimized_df['Distance'] != float('inf')].index
    for i, idx in enumerate(valid_idx[:15]):
        optimized_df.at[idx, 'Route_Order'] = i + 1
    
    # Tabs for Map / List
    tab1, tab2 = st.tabs(["지도 보기", "리스트 보기 (상태 변경)"])
    
    with tab1:
        st.markdown("#### 🚀 추천 방문 경로 리스트 (가까운 순 15곳)")
        top_15_df = optimized_df[optimized_df['Route_Order'].notna()].copy()
        if not top_15_df.empty:
            top_15_df['직선거리'] = (top_15_df['Distance'] * 111).apply(lambda x: f"{x:.1f} km")
            display_df = top_15_df[['Route_Order', 'Company Name', 'Status', '직선거리', 'Contact', 'Address']].rename(
                columns={'Route_Order': '방문순서', 'Company Name': '상호', 'Status': '상태', 'Contact': '연락처', 'Address': '주소'}
            )
            display_df['방문순서'] = display_df['방문순서'].astype(int)
            st.dataframe(display_df, hide_index=True, use_container_width=True)
            
        st.markdown("#### 🗺️ 현장 지도")
        # Folium Map with Base Layers
        m = folium.Map(location=[current_lat, current_lng], zoom_start=14, tiles=None)
        
        # 1. Default OpenStreetMap (Regular Roads)
        folium.TileLayer('OpenStreetMap', name='기본 도로망 (OpenStreetMap)').add_to(m)
        
        # 2. Vworld/CartoDB (Clean layout)
        folium.TileLayer('CartoDB positron', name='깔끔한 약도 (CartoDB)').add_to(m)
        
        # 3. Google Satellite Hybrid (Detailed buildings & roads)
        folium.TileLayer(
            tiles='http://mt0.google.com/vt/lyrs=y&hl=ko&x={x}&y={y}&z={z}',
            attr='Google',
            name='위성 및 상세 도로망 (Google Hybrid)'
        ).add_to(m)
        
        # Add Layer Control to toggle the map styles
        folium.LayerControl(position='topright').add_to(m)
        
        # Add Locate Control (내 위치 이동 버튼)
        plugins.LocateControl(
            position="topright",
            strings={"title": "내 실시간 위치 찾기", "popup": "현재 위치"},
        ).add_to(m)
        
        # Add Current Location Marker
        folium.Marker(
            location=[current_lat, current_lng],
            popup="<div style='width: 150px;'><b>📍 기준 위치(출발점)</b></div>",
            icon=folium.Icon(color='black', icon='user')
        ).add_to(m)
        
        # Guide Option: Draw animated line to top 15 nearest locations
        valid_targets = optimized_df.dropna(subset=['Latitude', 'Longitude'])
        if not valid_targets.empty:
            top_15 = valid_targets.head(15)
            route_coords = [[current_lat, current_lng]] + top_15[['Latitude', 'Longitude']].values.tolist()
            plugins.AntPath(
                locations=route_coords,
                dash_array=[10, 20],
                delay=1000,
                color='red',
                pulse_color='white',
                weight=3,
                tooltip='최적 방문 경로 가이드 (상위 15곳)'
            ).add_to(m)
        
        # Add Customer Markers
        for _, row in optimized_df.iterrows():
            if pd.isna(row['Latitude']) or pd.isna(row['Longitude']):
                continue # Skip if location could not be geocoded
                
            if row['Status'] == '미확인':
                color = 'red'
            elif row['Status'] == '진행중':
                color = 'orange'
            else:
                color = 'blue'
                
            order_text = f"[{int(row['Route_Order'])}] " if pd.notna(row['Route_Order']) else ""
            distance_km = f"{row['Distance'] * 111:.1f}km" if pd.notna(row['Route_Order']) else ""
            dist_html = f"<div style='margin-bottom: 4px;'><b>직선거리:</b> <span style='color:#27AE60; font-weight:bold;'>{distance_km}</span></div>" if distance_km else ""
                
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; font-size: 13px; border: 1px solid #ddd; background-color: white; padding: 12px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 220px;">
                <h4 style="margin-top: 0; margin-bottom: 8px; color: #2C3E50; font-size: 15px;">🏢 {order_text}{row['Company Name']}</h4>
                <div style="border-bottom: 1px solid #eee; margin-bottom: 8px;"></div>
                <div style="margin-bottom: 4px;"><b>상태:</b> <span style="color:{color}; font-weight:bold;">{row['Status']}</span></div>
                {dist_html}
                <div style="margin-bottom: 4px;"><b>정지사유:</b> {row['Stop Reason']}</div>
                <div style="margin-bottom: 4px;"><b>정지일자:</b> {row['Stop Start Date']}</div>
                <div style="margin-bottom: 4px;"><b>당월정지:</b> <span style="color:#E74C3C;">{row['Stop Days']}일</span></div>
            </div>
            """
            
            # Formatted Icons: Add numbers for top 15
            if pd.notna(row['Route_Order']):
                icon = plugins.BeautifyIcon(
                    border_color=color,
                    text_color=color,
                    number=int(row['Route_Order']),
                    inner_icon_style='margin-top:0; font-weight:bold;'
                )
            else:
                icon = folium.Icon(color=color, icon='info-sign')
            
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{order_text}{row['Company Name']} {distance_km}",
                icon=icon
            ).add_to(m)
            
        # returned_objects=[] prevents Streamlit from waiting for interaction data (Fast speed boost)
        st_data = st_folium(m, width=800, height=500, returned_objects=[])
    
    with tab2:
        st.caption("고객사를 클릭하여 상세 정보 확인 및 상태를 업데이트 하세요.")
        for idx, row in optimized_df.iterrows():
            with st.expander(f"🏢 {row['Company Name']} - 현재 상태: [{row['Status']}]"):
                st.write(f"**연락처**: {row['Contact']}")
                st.write(f"**주소**: {row['Address']}")
                st.write(f"**월정료**: {row['Monthly Fee']:,}원")
                st.write(f"**정지사유**: {row['Stop Reason']}")
                st.write(f"**정지시작일자**: {row['Stop Start Date']}")
                st.write(f"**당월말 정지일수**: {row['Stop Days']}일")
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
                # Note: Appended `idx` to the key to prevent StreamlitDuplicateElementKey when multiple items share a contract_no
                with col1:
                    st.button("진행전(미확인)", key=f"btn_un_{row['Contract No']}_{idx}", 
                              on_click=make_update_callback(row['Contract No'], "미확인"),
                              use_container_width=True,
                              disabled=row['Status'] == "미확인")
                with col2:
                    st.button("진행중", key=f"btn_ing_{row['Contract No']}_{idx}",
                              on_click=make_update_callback(row['Contract No'], "진행중"),
                              use_container_width=True,
                              disabled=row['Status'] == "진행중")
                with col3:
                    st.button("완료", key=f"btn_done_{row['Contract No']}_{idx}",
                              on_click=make_update_callback(row['Contract No'], "완료"),
                              use_container_width=True,
                              disabled=row['Status'] == "완료")
        
        st.info("상태를 변경하면 관리자 대시보드에 즉시 반영됩니다.")
