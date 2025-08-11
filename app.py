import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

# Set page config for wide layout
st.set_page_config(page_title="Map App", layout="wide")

st.title('Streamlit Map App')

# Initialize session state
if 'ip_location' not in st.session_state:
    st.session_state.ip_location = None
if 'search_ip' not in st.session_state:
    st.session_state.search_ip = None

# Function to get location from IP address
def get_location_from_ip(ip_address):
    try:
        # Using ip-api.com for IP geolocation (free service, more reliable)
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=10)
        st.write(f"Debug: Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            st.write(f"Debug: API Response: {data}")
            
            if data.get('status') == 'success' and 'lat' in data and 'lon' in data:
                return {
                    'lat': data['lat'],
                    'lon': data['lon'],
                    'city': data.get('city', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'isp': data.get('isp', 'Unknown')
                }
            else:
                st.error(f"API Error: {data.get('message', 'Unknown error')}")
        else:
            st.error(f"HTTP Error: {response.status_code}")
            
    except Exception as e:
        st.error(f"Error getting location: {e}")
    return None

# IP address input
st.sidebar.header("IP位置情報検索")
ip_input = st.sidebar.text_input("IPアドレスを入力してください", placeholder="例: 8.8.8.8")
col1, col2 = st.sidebar.columns(2)
with col1:
    search_button = st.button("位置を検索")
with col2:
    reset_button = st.button("リセット")

if reset_button:
    st.session_state.ip_location = None
    st.session_state.search_ip = None
    st.rerun()

# Display current IP location info in sidebar
if st.session_state.ip_location:
    st.sidebar.markdown("### 検索結果")
    st.sidebar.write(f"**IP:** {st.session_state.search_ip}")
    st.sidebar.write(f"**国:** {st.session_state.ip_location['country']}")
    st.sidebar.write(f"**地域:** {st.session_state.ip_location['region']}")
    st.sidebar.write(f"**都市:** {st.session_state.ip_location['city']}")
    st.sidebar.write(f"**ISP:** {st.session_state.ip_location['isp']}")
    st.sidebar.write(f"**座標:** {st.session_state.ip_location['lat']:.4f}, {st.session_state.ip_location['lon']:.4f}")

# Debug info
if ip_input:
    st.write(f"入力されたIP: {ip_input}")
if search_button:
    st.write("検索ボタンが押されました")

# Default location (Tokyo Station)
default_lat, default_lon = 35.681236, 139.767125
map_center = [default_lat, default_lon]
zoom_level = 15

# Create a folium map
m = folium.Map(location=map_center, zoom_start=zoom_level)

# Add Tokyo Station marker
folium.Marker(
    [default_lat, default_lon],
    popup="<b>東京駅</b><br>Tokyo Station<br>日本の鉄道の中心駅",
    tooltip="東京駅 (Tokyo Station)",
    icon=folium.Icon(color='red', icon='train', prefix='fa')
).add_to(m)

# Handle IP search
if search_button and ip_input:
    st.write(f"検索開始: {ip_input}")
    with st.spinner('IP位置を検索中...'):
        ip_location_data = get_location_from_ip(ip_input)
        if ip_location_data:
            st.session_state.ip_location = ip_location_data
            st.session_state.search_ip = ip_input
            st.success(f"IP {ip_input} の位置: {ip_location_data['city']}, {ip_location_data['country']}")
        else:
            st.error("IPアドレスの位置情報を取得できませんでした")

# Create map based on stored search result
if st.session_state.ip_location:
    # Center map on IP location
    map_center = [st.session_state.ip_location['lat'], st.session_state.ip_location['lon']]
    zoom_level = 10
    m = folium.Map(location=map_center, zoom_start=zoom_level)
    
    # Add IP location marker
    folium.Marker(
        [st.session_state.ip_location['lat'], st.session_state.ip_location['lon']],
        popup=f"<b>IP: {st.session_state.search_ip}</b><br>都市: {st.session_state.ip_location['city']}<br>国: {st.session_state.ip_location['country']}<br>地域: {st.session_state.ip_location['region']}<br>ISP: {st.session_state.ip_location['isp']}",
        tooltip=f"IP: {st.session_state.search_ip}",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)
    
    st.info(f"現在表示中: IP {st.session_state.search_ip} の位置")
else:
    # Default map (Tokyo Station)
    m = folium.Map(location=map_center, zoom_start=zoom_level)

# Always add Tokyo Station marker
folium.Marker(
    [default_lat, default_lon],
    popup="<b>東京駅</b><br>Tokyo Station<br>日本の鉄道の中心駅",
    tooltip="東京駅 (Tokyo Station)",
    icon=folium.Icon(color='red', icon='info-sign')
).add_to(m)

# Display the map in Streamlit using streamlit-folium
st_folium(m, width=None, height=600, use_container_width=True)

# You can add more Streamlit components here, like text or data display
st.write("Interactive Folium Map - IP位置検索機能付き")

# Add a section for general information or instructions
st.markdown("""
---
### このアプリについて

このStreamlitアプリは、Foliumライブラリを使用してインタラクティブな地図を表示します。
サイドバーにIPアドレスを入力して「位置を検索」ボタンをクリックすると、そのIPアドレスの地理的な位置が地図上に表示されます。
デフォルトでは東京駅が地図の中心に表示されます。

**機能:**
- IPアドレスからの位置情報検索
- 検索結果の地図上へのマーカー表示
- 検索結果のサイドバーへの詳細表示
- 地図のズームとパン

**使用技術:**
- Streamlit: ウェブアプリケーションフレームワーク
- Folium: Pythonでの地図作成ライブラリ
- `streamlit_folium`: StreamlitでFoliumマップを表示するためのブリッジ
- `requests`: 外部API（ip-api.com）からのデータ取得

**注意:**
- IPアドレスからの位置情報は、必ずしも正確な物理的な場所を示すものではありません。
- 無料のIPジオロケーションサービスを使用しているため、APIの制限や一時的な問題が発生する可能性があります。
""")
