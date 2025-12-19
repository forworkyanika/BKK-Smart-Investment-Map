import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import folium
from streamlit_folium import st_folium

class LandValuationApp:
    def __init__(self):
        st.set_page_config(
            page_title="BKK Smart Investment Map", 
            layout="wide", 
            page_icon="🏙️",
            initial_sidebar_state="expanded"
        )
        
        # Initialize State
        if 'selected_lat' not in st.session_state:
            st.session_state.selected_lat = 13.7455 # Siam
        if 'selected_lon' not in st.session_state:
            st.session_state.selected_lon = 100.5340

        self.bts_gdf = self.load_transit_data()
        self.landmarks_gdf = self.load_landmark_data()
        self.apply_theme()

    def apply_theme(self):
        """
        ปรับปรุง CSS:
        1. บังคับตัวหนังสือในกล่อง (.nearby-box) ให้เป็นสีดำเสมอ (!important)
        2. เพิ่มเงา (Box Shadow) ให้กล่องดูมีมิติ
        """
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600&display=swap');
            html, body, [class*="css"] { font-family: 'Prompt', sans-serif !important; }
            
            /* Metric สีน้ำเงินเข้ม */
            [data-testid="stMetricValue"] { color: #2E86C1 !important; }
            
            /* --- ส่วนที่แก้ไข: กล่องข้อความ --- */
            .nearby-box {
                background-color: #ffffff; /* พื้นหลังสีขาว */
                color: #333333 !important; /* บังคับตัวหนังสือสีเทาเข้มเกือบดำ (แก้ปัญหาอ่านไม่ออก) */
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 10px;
                border-left: 6px solid #FF4B4B; /* แถบสีแดงด้านซ้าย */
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* เงา */
                transition: transform 0.2s; /* เอฟเฟกต์ขยับนิดหน่อย */
            }
            
            .nearby-box:hover {
                transform: scale(1.02); /* ขยายเมื่อเอาเมาส์จี้ */
            }

            .nearby-box b {
                color: #000000 !important; /* ชื่อสถานที่สีดำสนิท */
                font-size: 1.1em;
            }
            
            .nearby-box small {
                color: #666666 !important; /* ตัวหนังสือเล็กสีเทาเข้ม */
            }
        </style>
        """, unsafe_allow_html=True)

    @st.cache_data
    def load_transit_data(_self):
        """ข้อมูลรถไฟฟ้า"""
        stations = []
        stations.extend([
            {"name": "BTS Siam", "lat": 13.7456, "lon": 100.5341, "line": "Sukhumvit", "color": "#76D7C4"},
            {"name": "BTS Asok", "lat": 13.7371, "lon": 100.5604, "line": "Sukhumvit", "color": "#76D7C4"},
            {"name": "BTS Mo Chit", "lat": 13.8022, "lon": 100.5539, "line": "Sukhumvit", "color": "#76D7C4"},
            {"name": "BTS Thong Lo", "lat": 13.7242, "lon": 100.5783, "line": "Sukhumvit", "color": "#76D7C4"},
            {"name": "BTS Chong Nonsi", "lat": 13.7237, "lon": 100.5294, "line": "Silom", "color": "#1E8449"},
            {"name": "MRT Sukhumvit", "lat": 13.7375, "lon": 100.5606, "line": "MRT Blue", "color": "#2E86C1"},
            {"name": "MRT Rama 9", "lat": 13.7578, "lon": 100.5654, "line": "MRT Blue", "color": "#2E86C1"},
            {"name": "MRT Chatuchak", "lat": 13.8030, "lon": 100.5543, "line": "MRT Blue", "color": "#2E86C1"},
            {"name": "SRT Krung Thep Aphiwat", "lat": 13.8043, "lon": 100.5404, "line": "Red Line", "color": "#C0392B"},
            {"name": "ICONSIAM (Gold)", "lat": 13.7267, "lon": 100.5094, "line": "Gold Line", "color": "#D4AC0D"},
        ])
        df = pd.DataFrame(stations)
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")
        return gdf

    @st.cache_data
    def load_landmark_data(_self):
        """ข้อมูลสถานที่สำคัญ"""
        landmarks = [
            {"name": "Siam Paragon", "lat": 13.7462, "lon": 100.5347, "type": "Mall", "icon": "shopping-cart"},
            {"name": "Central World", "lat": 13.7466, "lon": 100.5393, "type": "Mall", "icon": "shopping-cart"},
            {"name": "ICONSIAM", "lat": 13.7266, "lon": 100.5103, "type": "Mall", "icon": "shopping-cart"},
            {"name": "Chulalongkorn Univ.", "lat": 13.7383, "lon": 100.5323, "type": "Education", "icon": "graduation-cap"},
            {"name": "Lumpini Park", "lat": 13.7313, "lon": 100.5416, "type": "Park", "icon": "tree"},
            {"name": "Chatuchak Market", "lat": 13.7999, "lon": 100.5505, "type": "Market", "icon": "shopping-bag"},
            {"name": "Terminal 21", "lat": 13.7376, "lon": 100.5602, "type": "Mall", "icon": "shopping-cart"},
            {"name": "Benjakitti Park", "lat": 13.7291, "lon": 100.5552, "type": "Park", "icon": "tree"},
        ]
        df = pd.DataFrame(landmarks)
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")
        return gdf

    def calculate_valuation(self, lat, lon):
        user_point = Point(lon, lat)
        user_gdf = gpd.GeoDataFrame(geometry=[user_point], crs="EPSG:4326")
        user_meter = user_gdf.to_crs(epsg=32647)
        bts_meter = self.bts_gdf.to_crs(epsg=32647)
        
        distances = bts_meter.geometry.distance(user_meter.geometry.iloc[0])
        min_dist = distances.min()
        nearest_idx = distances.idxmin()
        station_info = self.bts_gdf.iloc[nearest_idx]
        
        base_price = 200000 
        price = max(20000, min(1000000, base_price - (min_dist * 30)))
        if "Sukhumvit" in station_info['line']: price *= 1.2
        
        return min_dist, station_info, price

    def get_nearby_landmarks(self, lat, lon):
        user_point = Point(lon, lat)
        user_gdf = gpd.GeoDataFrame(geometry=[user_point], crs="EPSG:4326")
        user_meter = user_gdf.to_crs(epsg=32647)
        landmark_meter = self.landmarks_gdf.to_crs(epsg=32647)
        
        dists = landmark_meter.geometry.distance(user_meter.geometry.iloc[0])
        results = self.landmarks_gdf.copy()
        results['distance'] = dists
        
        nearby = results[results['distance'] <= 3000].sort_values('distance')
        return nearby

    def render_map(self):
        m = folium.Map(
            location=[st.session_state.selected_lat, st.session_state.selected_lon], 
            zoom_start=13, 
            tiles="OpenStreetMap" 
        )
        
        for _, row in self.bts_gdf.iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=5, color="white", weight=1,
                fill=True, fill_color=row['color'], fill_opacity=0.9,
                popup=f"{row['name']}"
            ).add_to(m)

        for _, row in self.landmarks_gdf.iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=f"{row['name']} ({row['type']})",
                icon=folium.Icon(color='orange', icon=row['icon'], prefix='fa')
            ).add_to(m)
            
        folium.Marker(
            [st.session_state.selected_lat, st.session_state.selected_lon],
            popup="Target Location",
            icon=folium.Icon(color="red", icon="home", prefix='fa')
        ).add_to(m)
        return m

    def render_sidebar(self):
        with st.sidebar:
            st.title("⚙️ ข้อมูลอ้างอิง")
            st.info("""
            **Methodology:**
            1. **Euclidean Distance:** วัดระยะทางตรงไปยังสถานี
            2. **Valuation Model:** Linear Decay (ราคาลดลงตามระยะทาง)
            """)
            st.markdown("### 🏷️ สัญลักษณ์บนแผนที่")
            st.markdown("🔴 **บ้านของคุณ** (Target)")
            st.markdown("🟢 **รถไฟฟ้า** (Transit)")
            st.markdown("🟠 **สถานที่สำคัญ** (Mall/Uni/Park)")

    def run(self):
        self.render_sidebar()
        st.title("🏙️ BKK Smart Investment Map")
        st.markdown("วิเคราะห์ศักยภาพที่ดิน เพื่อการลงทุนและอยู่อาศัย")
        
        col_map, col_result = st.columns([2, 1])
        
        with col_map:
            st.write("👇 **คลิกบนแผนที่เพื่อวิเคราะห์ทำเล**")
            m = self.render_map()
            map_data = st_folium(m, height=600, use_container_width=True)
            
            if map_data['last_clicked']:
                if map_data['last_clicked']['lat'] != st.session_state.selected_lat:
                    st.session_state.selected_lat = map_data['last_clicked']['lat']
                    st.session_state.selected_lon = map_data['last_clicked']['lng']
                    st.rerun()

        with col_result:
            dist, station_info, price = self.calculate_valuation(st.session_state.selected_lat, st.session_state.selected_lon)
            nearby_landmarks = self.get_nearby_landmarks(st.session_state.selected_lat, st.session_state.selected_lon)

            st.markdown("### 💰 ผลประเมินราคา")
            with st.container(border=True):
                st.metric("ราคาประเมินเบื้องต้น", f"฿{price:,.0f}", "บาท/ตร.ว.")
                st.caption(f"ใกล้ {station_info['name']} ({dist:,.0f} ม.)")
                if dist < 500: st.success("🌟 ทำเลทอง (Prime Area)")
                elif dist < 1000: st.info("✅ ทำเลดี (Good Potential)")
                else: st.warning("🚗 เน้นใช้รถ (Car Dependent)")

            st.write("")
            st.markdown("### 🏢 สถานที่สำคัญใกล้เคียง (รัศมี 3 กม.)")
            st.caption("ปัจจัยบวกสำหรับการลงทุน/ปล่อยเช่า")
            
            if not nearby_landmarks.empty:
                for _, row in nearby_landmarks.iterrows():
                    # สร้าง Box ด้วย HTML ที่บังคับสีตัวหนังสือแล้ว
                    st.markdown(f"""
                    <div class="nearby-box">
                        <b>{row['name']}</b> <small style="color:#666 !important;">({row['type']})</small><br>
                        🚗 ห่างออกไป <b>{row['distance']/1000:.1f} กม.</b>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("ไม่พบสถานที่สำคัญหลักในระยะ 3 กม.")

if __name__ == "__main__":
    app = LandValuationApp()
    app.run()