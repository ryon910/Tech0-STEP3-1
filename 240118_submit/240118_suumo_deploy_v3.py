#-----------------------------------------準備-----------------------------------------
import folium
import os
import pandas as pd
import sqlite3
import streamlit as st
import streamlit.components.v1 as components

def load_data():
    # 現在のファイルのディレクトリを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # データベースファイルへのパスを構築
    db_path = os.path.join(current_dir, 'suumo_v3.db')
    # データベースに接続
    conn = sqlite3.connect(db_path)
    # SQLクエリを実行し、結果をDataFrameに読み込む
    query = "SELECT * FROM suumo_v3"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df = load_data()

#徒歩時間を数値データに変換。
df['access1_walk'] = pd.to_numeric(df['access1_walk'], errors='coerce')
df['access2_walk'] = pd.to_numeric(df['access2_walk'], errors='coerce')
df['access3_walk'] = pd.to_numeric(df['access3_walk'], errors='coerce')

# 希望条件
# 駅リスト
station_list = [
    '東京駅', '有楽町駅', '新橋駅', '浜松町駅', '田町駅', '高輪ゲートウェイ駅', '品川駅',
    '大崎駅', '五反田駅', '目黒駅', '恵比寿駅', '渋谷駅', '原宿駅', '代々木駅', '新宿駅',
    '新大久保駅', '高田馬場駅', '目白駅', '池袋駅', '大塚駅', '巣鴨駅', '駒込駅', '田端駅',
    '西日暮里駅', '鶯谷駅', '上野駅', '御徒町駅', '秋葉原駅', '神田駅'
    ]
# 間取りリスト
madori_list = [
    '2K', '2DK', '2LDK', '2SK', '2SDK', '2SLDK',
    '3K', '3DK', '3LDK', '3SK', '3SDK', '3SLDK',
    '4K', '4LDK', '4SK',  '4SLDK'
    ]

#-----------------------------------------サイドバー-----------------------------------------
# サイドバーで希望の条件を入力する枠を用意
st.sidebar.title('希望条件を入力してください')

# 最寄駅
st.sidebar.text('1.最寄駅')
station_select = st.sidebar.multiselect('希望の最寄駅を選択してください（複数選択可）', station_list)

# 賃料
st.sidebar.text('2.賃料')
min_rent, max_rent = st.sidebar.slider(
    '賃料（万円）の範囲を入力してください',
    min_value = 0,
    max_value = 30,
    value = (0, 30))
min_rent_yen = min_rent * 10000
max_rent_yen = max_rent * 10000

# 駅徒歩
st.sidebar.text('3.駅徒歩')
min_walk_time, max_walk_time = st.sidebar.slider(
    '駅徒歩時間（分）の範囲を入力してください',
    min_value = 0,
    max_value = 30,
    value = (0, 30))

# 間取り
st.sidebar.text('4.間取り')
madori_select = st.sidebar.multiselect('希望の間取りを選択してください（複数選択可）', madori_list)

# 築年数
st.sidebar.text('5.築年数')
min_age, max_age = st.sidebar.slider(
    '築年数の範囲を入力してください。「99」には「99年以上」も含まれます。',
    min_value = 0,
    max_value = 99,
    value = (0, 50))

# 占有面積
st.sidebar.text('6.占有面積')
min_menseki, max_menseki = st.sidebar.slider(
    '占有面積（m2）の範囲を入力してください',
    min_value = 0,
    max_value = 150,
    value = (0, 75))

#-----------------------------------------ボタン類-----------------------------------------
# 会員登録・Loginボタンを画面右上に配置
col1, col2, col3 = st.columns([9,2,2])
with col2:
    st.button('会員登録', type='secondary')
with col3:
    st.button('Login', type='secondary')

#-----------------------------------------メイン画面１(検索)-----------------------------------------
# タイトル
st.title('物件情報検索アプリ')
# アプリ概要説明
st.write('山手線沿線で、2K以上の2人暮らし向け賃貸を、重複なく効率よく探すことができます。')
st.markdown("---")

# 各ボタンのクリック状態を初期化
if 'button1_clicked' not in st.session_state:
    st.session_state['button1_clicked'] = False
if 'button2_clicked' not in st.session_state:
    st.session_state['button2_clicked'] = False

# 検索ボタンを設置
btn_search = st.sidebar.button('検索',type = 'primary')
# ボタン1(検索ボタン）を押すとボタン１セッションがTrueに。一度クリックされたセッションはTrueに維持される。
if btn_search == True:
    st.session_state['button1_clicked'] = True
# ボタン１（検索ボタン）がクリックされた状態（ボタン１セッションがTrue）の場合の処理を実行
if st.session_state['button1_clicked'] == True:

    # 検索条件でデータを絞り込み、結果を df_search に代入
    try:
        df_search = df.query(f'(access1_station == {station_select}) and ({min_rent_yen} <= rent <= {max_rent_yen}) and ({min_walk_time} <= access1_walk <= {max_walk_time}) and (madori == {madori_select}) and ({min_age} <= age <= {max_age})  and ({min_menseki} <= menseki <= {max_menseki})')
        # 検索結果のヒット件数を取得
        hit = len(df_search)

        # 地図を作成。地図の初期中央位置は df_searchの緯度・経度の平均値。
        m = folium.Map(location = [df_search['lat'].mean(), df_search['lng'].mean()], zoom_start=13)

        # 地図にDataFrame内の各位置のマーカーを追加
        for index, row in df_search.iterrows():
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={row['lat']},{row['lng']}"
            popup_html = f'<a href="{google_maps_url}" target="_blank">Google Mapsで開く</a>'
            popup = folium.Popup(f"物件名：{row['name']}<br>家賃：{row['rent']}円<br>間取り：{row['madori']}・{row['menseki']}m2<br>{popup_html}", max_width=300)
            folium.Marker(
                location=[row['lat'], row['lng']],
                popup = popup
            ).add_to(m)

        # Folium地図をStreamlitに表示
        map_html = m._repr_html_()

        # 以下、検索結果
        st.write('■ 検索結果')
        st.write(f'▼ ヒット件数：{hit}件')
        st.download_button(label='検索結果一覧をダウンロードする', data=df_search.to_csv(index=False), file_name='build_list', mime='text/csv')
        # 以下、マップの情報
        st.write('▼ マップ：')
        components.html(map_html, height=400)
        st.markdown("---")
        #-----------------------------------------メイン画面２(詳細)-----------------------------------------
        # 物件idを入力すると、外観や間取りを確認できるようにする。まず、df_detailに入力したidのDataFrameを代入。
        st.write('▼詳細情報：')
        for i in range(0, len(df_search)):
            name = df_search.iloc[i]['name']
            address = df_search.iloc[i]['address']
            age = df_search.iloc[i]['age']
            structure = df_search.iloc[i]['structure']
            build_img_url = df_search.iloc[i]['build_img_url']
            floor = df_search.iloc[i]['floor']
            rent = df_search.iloc[i]['rent']
            admin = df_search.iloc[i]['admin']
            deposit = df_search.iloc[i]['deposit']
            gratuity = df_search.iloc[i]['gratuity']
            madori = df_search.iloc[i]['madori']
            menseki = df_search.iloc[i]['menseki']
            madori_img_url = df_search.iloc[i]['madori_img_url']
            detail_url = df_search.iloc[i]['detail_url']
            access1_line = df_search.iloc[i]['access1_line']
            access1_station = df_search.iloc[i]['access1_station']
            access1_walk = df_search.iloc[i]['access1_walk']
            access2_line = df_search.iloc[i]['access2_line']
            access2_station = df_search.iloc[i]['access2_station']
            access2_walk = df_search.iloc[i]['access2_walk']
            access3_line = df_search.iloc[i]['access3_line']
            access3_station = df_search.iloc[i]['access3_station']
            access3_walk = df_search.iloc[i]['access3_walk']

            st.markdown(f'<span style="font-size: 20px; text-decoration: underline;">{i+1}. {name}</span>', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(build_img_url, use_column_width='auto')
            with col2:
                st.write('▼物件情報')
                st.write(f'住所：{address}')
                try:
                    st.write(f'最寄駅：  \n  {access1_line} {access1_station} {str(int(access1_walk))}分  \n  {access2_line} {access2_station} {str(int(access3_walk))}分  \n  {access3_line} {access3_station} {str(int(access3_walk))}分')
                except Exception as e:
                    st.write(f'最寄駅：  \n  {access1_line} {access1_station} {str(int(access1_walk))}分')
                st.write(f'その他：築{age}年・{structure}階建')
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(madori_img_url, use_column_width='auto')
            with col2:
                st.write('▼部屋情報')
                st.write(f'家賃：{rent}円・管理費：{admin}円')
                st.write(f'敷金：{deposit}円・礼金：{gratuity}円')
                st.write(f'間取：{madori}・{menseki}m2')
                st.markdown(f'<a href="{detail_url}" target="_blank">賃貸情報サイトから問い合わせる</a>', unsafe_allow_html=True)
            st.markdown("---")
    except Exception as e:
        st.write('条件に未入力の項目があるか、条件に一致する物件がありません。')