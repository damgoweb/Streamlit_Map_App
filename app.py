import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
import json
import pandas as pd
import time

# ページ設定
st.set_page_config(
    page_title="マルチ入力対応地図アプリ",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# タイトルと説明
st.title("🗺️ マルチ入力対応地図アプリ")
st.markdown("""
このアプリは以下の3つの入力方法に対応しています：
- **IPアドレス**: IPアドレスから位置情報を取得
- **緯度・経度**: 直接座標を入力
- **都市名**: 都市名から位置情報を検索
""")

# サイドバーで入力方法を選択
st.sidebar.header("入力方法を選択")
input_method = st.sidebar.radio(
    "検索方法：",
    ["IPアドレス", "緯度・経度", "都市名", "複数地点入力"]
)

# 地図の初期設定
def create_base_map(center=[35.6762, 139.6503], zoom=10):
    """基本の地図を作成"""
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles='OpenStreetMap',
        control_scale=True
    )
    return m

# IPアドレスから位置情報を取得
def get_location_from_ip(ip_address):
    """IPアドレスから位置情報を取得"""
    try:
        # IP-API.comを使用（無料、制限あり）
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return {
                    'lat': data['lat'],
                    'lon': data['lon'],
                    'city': data['city'],
                    'country': data['country'],
                    'region': data['regionName']
                }
        return None
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        return None

# 都市名から位置情報を取得（Nominatim API直接使用）
def get_location_from_city(city_name):
    """都市名から位置情報を取得（OpenStreetMap Nominatim API使用）"""
    try:
        # Nominatim APIを直接使用
        headers = {
            'User-Agent': 'StreamlitMapApp/1.0'
        }
        params = {
            'q': city_name,
            'format': 'json',
            'limit': 1
        }
        
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params=params,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                result = data[0]
                return {
                    'lat': float(result['lat']),
                    'lon': float(result['lon']),
                    'address': result.get('display_name', city_name)
                }
        return None
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        return None

# 逆ジオコーディング（緯度経度から住所を取得）
def get_address_from_coords(lat, lon):
    """緯度経度から住所を取得（OpenStreetMap Nominatim API使用）"""
    try:
        headers = {
            'User-Agent': 'StreamlitMapApp/1.0'
        }
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json'
        }
        
        response = requests.get(
            'https://nominatim.openstreetmap.org/reverse',
            params=params,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('display_name', '住所情報なし')
        return "住所情報を取得できませんでした"
    except:
        return "住所情報を取得できませんでした"

# メインの処理
if input_method == "IPアドレス":
    st.header("📍 IPアドレスから位置を検索")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        ip_address = st.text_input(
            "IPアドレスを入力してください",
            placeholder="例: 8.8.8.8",
            help="パブリックIPアドレスを入力してください"
        )
    
    with col2:
        st.write("")
        st.write("")
        search_button = st.button("🔍 検索", type="primary", use_container_width=True)
    
    if search_button and ip_address:
        with st.spinner("位置情報を取得中..."):
            location_data = get_location_from_ip(ip_address)
            
        if location_data:
            # 地図を作成
            m = create_base_map(
                center=[location_data['lat'], location_data['lon']],
                zoom=12
            )
            
            # マーカーを追加
            folium.Marker(
                [location_data['lat'], location_data['lon']],
                popup=folium.Popup(f"""
                <b>IPアドレス:</b> {ip_address}<br>
                <b>都市:</b> {location_data.get('city', 'N/A')}<br>
                <b>地域:</b> {location_data.get('region', 'N/A')}<br>
                <b>国:</b> {location_data.get('country', 'N/A')}<br>
                <b>緯度:</b> {location_data['lat']}<br>
                <b>経度:</b> {location_data['lon']}
                """, max_width=300),
                tooltip=f"IP: {ip_address}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
            
            # 円を追加（おおよその範囲を示す）
            folium.Circle(
                [location_data['lat'], location_data['lon']],
                radius=1000,
                color='blue',
                fill=True,
                fillColor='lightblue',
                fillOpacity=0.3
            ).add_to(m)
            
            # 地図を表示 - 修正済み
            st.components.v1.html(m._repr_html_(), height=600)
            
            # 詳細情報を表示
            st.success("✅ 位置情報を取得しました")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("都市", location_data.get('city', 'N/A'))
            with col2:
                st.metric("緯度", f"{location_data['lat']:.4f}")
            with col3:
                st.metric("経度", f"{location_data['lon']:.4f}")
        else:
            st.error("❌ 指定されたIPアドレスの位置情報を取得できませんでした")

elif input_method == "緯度・経度":
    st.header("🌐 緯度・経度から位置を表示")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        latitude = st.number_input(
            "緯度",
            min_value=-90.0,
            max_value=90.0,
            value=35.6762,
            step=0.0001,
            format="%.4f"
        )
    
    with col2:
        longitude = st.number_input(
            "経度",
            min_value=-180.0,
            max_value=180.0,
            value=139.6503,
            step=0.0001,
            format="%.4f"
        )
    
    with col3:
        st.write("")
        st.write("")
        show_button = st.button("📍 地図に表示", type="primary", use_container_width=True)
    
    if show_button:
        with st.spinner("住所情報を取得中..."):
            # API呼び出しの間隔を空ける（レート制限対策）
            time.sleep(1)
            address = get_address_from_coords(latitude, longitude)
        
        # 地図を作成
        m = create_base_map(center=[latitude, longitude], zoom=15)
        
        # マーカーを追加
        folium.Marker(
            [latitude, longitude],
            popup=f"""
            <b>緯度:</b> {latitude}<br>
            <b>経度:</b> {longitude}<br>
            <b>住所:</b> {address}
            """,
            tooltip=f"座標: {latitude:.4f}, {longitude:.4f}",
            icon=folium.Icon(color='green', icon='map-marker')
        ).add_to(m)
        
        # 十字線を追加
        folium.PolyLine(
            [[latitude-0.001, longitude], [latitude+0.001, longitude]],
            color='red',
            weight=2,
            opacity=0.5
        ).add_to(m)
        folium.PolyLine(
            [[latitude, longitude-0.001], [latitude, longitude+0.001]],
            color='red',
            weight=2,
            opacity=0.5
        ).add_to(m)
        
        # 地図を表示 - 修正済み
        st.components.v1.html(m._repr_html_(), height=600)
        
        # 詳細情報を表示
        st.success("✅ 地図に位置を表示しました")
        st.info(f"📍 **住所**: {address}")

elif input_method == "都市名":
    st.header("🏙️ 都市名から位置を検索")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        city_name = st.text_input(
            "都市名を入力してください",
            placeholder="例: 東京, Tokyo, New York, Paris",
            help="日本語または英語で都市名を入力してください"
        )
    
    with col2:
        st.write("")
        st.write("")
        search_button = st.button("🔍 検索", type="primary", use_container_width=True)
    
    if search_button and city_name:
        with st.spinner("位置情報を検索中..."):
            # API呼び出しの間隔を空ける（レート制限対策）
            time.sleep(1)
            location_data = get_location_from_city(city_name)
        
        if location_data:
            # 地図を作成
            m = create_base_map(
                center=[location_data['lat'], location_data['lon']],
                zoom=12
            )
            
            # マーカーを追加
            folium.Marker(
                [location_data['lat'], location_data['lon']],
                popup=f"""
                <b>検索キーワード:</b> {city_name}<br>
                <b>住所:</b> {location_data['address']}<br>
                <b>緯度:</b> {location_data['lat']}<br>
                <b>経度:</b> {location_data['lon']}
                """,
                tooltip=city_name,
                icon=folium.Icon(color='blue', icon='star')
            ).add_to(m)
            
            # 地図を表示 - 修正済み
            st.components.v1.html(m._repr_html_(), height=600)
            
            # 詳細情報を表示
            st.success("✅ 都市の位置情報を取得しました")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("緯度", f"{location_data['lat']:.4f}")
            with col2:
                st.metric("経度", f"{location_data['lon']:.4f}")
            st.info(f"📍 **詳細住所**: {location_data['address']}")
        else:
            st.error(f"❌ '{city_name}' の位置情報を見つけることができませんでした")

else:  # 複数地点入力
    st.header("📍 複数地点を一括表示")
    st.markdown("複数の地点を異なる方法で入力して、一つの地図に表示します。")
    
    # セッション状態でデータを管理
    if 'points_data' not in st.session_state:
        st.session_state.points_data = pd.DataFrame(
            columns=['名前', 'タイプ', '値', '緯度', '経度']
        )
    
    # 新しい地点を追加
    with st.expander("➕ 新しい地点を追加", expanded=True):
        col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
        
        with col1:
            point_name = st.text_input("地点名", placeholder="例: 本社")
        
        with col2:
            point_type = st.selectbox(
                "入力タイプ",
                ["都市名", "IPアドレス", "緯度経度"]
            )
        
        with col3:
            if point_type == "都市名":
                point_value = st.text_input("都市名", placeholder="例: Tokyo")
            elif point_type == "IPアドレス":
                point_value = st.text_input("IPアドレス", placeholder="例: 8.8.8.8")
            else:
                col3_1, col3_2 = st.columns(2)
                with col3_1:
                    lat_input = st.number_input("緯度", format="%.4f", value=35.6762)
                with col3_2:
                    lon_input = st.number_input("経度", format="%.4f", value=139.6503)
                point_value = f"{lat_input},{lon_input}"
        
        with col4:
            st.write("")
            st.write("")
            if st.button("追加", type="primary", use_container_width=True):
                if point_name and point_value:
                    # 位置情報を取得
                    if point_type == "都市名":
                        time.sleep(1)  # レート制限対策
                        loc = get_location_from_city(point_value)
                        if loc:
                            new_row = pd.DataFrame([{
                                '名前': point_name,
                                'タイプ': point_type,
                                '値': point_value,
                                '緯度': loc['lat'],
                                '経度': loc['lon']
                            }])
                            st.session_state.points_data = pd.concat(
                                [st.session_state.points_data, new_row],
                                ignore_index=True
                            )
                            st.success(f"✅ '{point_name}' を追加しました")
                            st.rerun()
                    elif point_type == "IPアドレス":
                        loc = get_location_from_ip(point_value)
                        if loc:
                            new_row = pd.DataFrame([{
                                '名前': point_name,
                                'タイプ': point_type,
                                '値': point_value,
                                '緯度': loc['lat'],
                                '経度': loc['lon']
                            }])
                            st.session_state.points_data = pd.concat(
                                [st.session_state.points_data, new_row],
                                ignore_index=True
                            )
                            st.success(f"✅ '{point_name}' を追加しました")
                            st.rerun()
                    else:  # 緯度経度
                        lat, lon = point_value.split(',')
                        new_row = pd.DataFrame([{
                            '名前': point_name,
                            'タイプ': point_type,
                            '値': point_value,
                            '緯度': float(lat),
                            '経度': float(lon)
                        }])
                        st.session_state.points_data = pd.concat(
                            [st.session_state.points_data, new_row],
                            ignore_index=True
                        )
                        st.success(f"✅ '{point_name}' を追加しました")
                        st.rerun()
    
    # 登録された地点を表示
    if not st.session_state.points_data.empty:
        st.subheader("登録済みの地点")
        
        # データテーブルを表示
        edited_df = st.data_editor(
            st.session_state.points_data,
            hide_index=True,
            use_container_width=True,
            disabled=['緯度', '経度']
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🗺️ 地図に表示", type="primary", use_container_width=True):
                if not edited_df.empty:
                    # 中心座標を計算
                    center_lat = edited_df['緯度'].mean()
                    center_lon = edited_df['経度'].mean()
                    
                    # 地図を作成
                    m = create_base_map(center=[center_lat, center_lon], zoom=10)
                    
                    # 各地点にマーカーを追加
                    colors = ['red', 'blue', 'green', 'purple', 'orange', 
                             'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
                    
                    for idx, row in edited_df.iterrows():
                        color = colors[idx % len(colors)]
                        
                        # アイコンを設定
                        if row['タイプ'] == 'IPアドレス':
                            icon = 'wifi'
                        elif row['タイプ'] == '都市名':
                            icon = 'home'
                        else:
                            icon = 'map-marker'
                        
                        folium.Marker(
                            [row['緯度'], row['経度']],
                            popup=f"""
                            <b>{row['名前']}</b><br>
                            <b>タイプ:</b> {row['タイプ']}<br>
                            <b>値:</b> {row['値']}<br>
                            <b>緯度:</b> {row['緯度']:.4f}<br>
                            <b>経度:</b> {row['経度']:.4f}
                            """,
                            tooltip=row['名前'],
                            icon=folium.Icon(color=color, icon=icon)
                        ).add_to(m)
                    
                    # すべての地点を含むように境界を調整
                    sw = edited_df[['緯度', '経度']].min().values.tolist()
                    ne = edited_df[['緯度', '経度']].max().values.tolist()
                    m.fit_bounds([sw, ne])
                    
                    # 地図を表示 - 修正済み
                    st.components.v1.html(m._repr_html_(), height=600)
        
        with col2:
            if st.button("🗑️ すべてクリア", use_container_width=True):
                st.session_state.points_data = pd.DataFrame(
                    columns=['名前', 'タイプ', '値', '緯度', '経度']
                )
                st.rerun()
        
        with col3:
            # CSVダウンロード機能
            csv = edited_df.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 CSVとしてダウンロード",
                data=csv.encode('utf-8'),
                file_name="locations.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("👆 上のフォームから地点を追加してください")

# フッター
st.sidebar.markdown("---")
st.sidebar.info("""
### 📝 使い方のヒント
- **IPアドレス**: パブリックIPアドレスのみ対応
- **都市名**: 日本語・英語両対応
- **緯度経度**: 小数点4桁まで入力可能
- **複数地点**: 異なる入力方法を組み合わせ可能

### ⚠️ 注意
- OpenStreetMapのAPIを使用しています
- 連続リクエストには1秒の遅延があります
""")

st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ using Streamlit")