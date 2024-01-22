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
    db_path = os.path.join(current_dir, 'suumo_v2.db')
    # データベースに接続
    conn = sqlite3.connect(db_path)
    # SQLクエリを実行し、結果をDataFrameに読み込む
    query = "SELECT * FROM suumo_v2"
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

# 検索ボタンを設置
btn_search = st.sidebar.button('検索',type = 'primary')

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
        # 緯度・経度は欠損値を含むため、map用に緯度あるいは経度に欠損値のあるレコードを削除したものを df_search_drop に代入
        df_search_drop = df_search.dropna(subset=['latitude', 'longitude'])

        # 地図を作成。地図の初期中央位置は df_search_drop の緯度・経度の平均値。
        m = folium.Map(location = [df_search_drop['latitude'].mean(), df_search_drop['longitude'].mean()], zoom_start=13)

        # 地図にDataFrame内の各位置のマーカーを追加
        for index, row in df_search_drop.iterrows():
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={row['latitude']},{row['longitude']}"
            popup_html = f'<a href="{google_maps_url}" target="_blank">Google Mapsで開く</a>'
            popup = folium.Popup(f"id：{row['id']}<br>物件名：{row['name']}<br>家賃：{row['rent']}円<br>間取り：{row['madori']}・{row['menseki']}m2<br>{popup_html}", max_width=300)
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup = popup
            ).add_to(m)
        # df_searchのカラム名を全て日本語に直す
        df_search.columns = ['id','物件名', '住所', '築年数', '構造', '階数', '賃料(円)', '管理費(円)', '敷金(円)', '礼金(円)', '間取り', '占有面積(m2)', '最寄駅路線1', '最寄駅1', '駅徒歩1(分)', '最寄駅路線2', '最寄駅2', '駅徒歩2(分)', '最寄駅路線3', '最寄駅3', '駅徒歩3(分)', '緯度', '経度','物件画像URL','間取り画像URL','詳細情報URL' ]

        # Folium地図をStreamlitに表示
        map_html = m._repr_html_()

        # 以下、検索結果
        st.write('■ 検索結果')
        st.write(f'▼ ヒット件数：{hit}件')
        st.write('▼ 物件一覧：')
        # 検索結果のDataFrameとCSVダウンロードボタンを設置
        st.dataframe(df_search, height=300)
        st.download_button(label='Download CSV', data=df_search.to_csv(index=False), file_name='build_list', mime='text/csv')
        st.markdown("---")
        # 以下、マップの情報
        st.write('▼ マップ：')
        components.html(map_html, height=400)
        st.write('※位置情報の取得に失敗した物件は表示されていません。')
        st.markdown("---")
        #-----------------------------------------メイン画面２(詳細)-----------------------------------------
        # 物件idを入力すると、外観や間取りを確認できるようにする。まず、df_detailに入力したidのDataFrameを代入。
        st.write('▼詳細情報：')
        id_input_str = st.text_input('物件のidを入力してください。コンマなし、半角数字でお願いします。')
        # ボタン２(確認ボタン）を押すとボタン２セッションがTrueに。一度クリックされたセッションはTrueに維持される。
        if st.button('確認') == True:
            st.session_state['button2_clicked'] = True
        # ボタン2（確認ボタン）がクリックされた状態（ボタン２セッションがTrue）の場合の処理を実行
        if st.session_state['button2_clicked'] == True:
            try:
                if 0 <= int(id_input_str) <= int(len(df))-1:
                    id_input = int(id_input_str)
                    df_detail = df[df['id'] == id_input]
                    df_detail.columns = ['id','物件名', '住所', '築年数', '構造', '階数', '賃料(円)', '管理費(円)', '敷金(円)', '礼金(円)', '間取り', '占有面積(m2)', '最寄駅路線1', '最寄駅1', '駅徒歩1(分)', '最寄駅路線2', '最寄駅2', '駅徒歩2(分)', '最寄駅路線3', '最寄駅3', '駅徒歩3(分)', '緯度', '経度','物件画像URL','間取り画像URL','詳細情報URL' ]
                    # 物件の情報一覧
                    st.dataframe(df_detail)
                    # 縦2列に外観画像と間取り画像を配置する。画像は存在しないものもあるため、例外処理を用意しておく。
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        try:
                            st.image(df_detail['物件画像URL'].to_list()[0], use_column_width='auto',caption='物件の外観')
                        except Exception as e:
                            st.write('外観の画像がありません')
                    with col2:
                        try:
                            st.image(df_detail['間取り画像URL'].to_list()[0], use_column_width='auto', caption='間取り')
                        except Exception as e:
                            st.write('間取りの画像がありません')
                    st.markdown("---")
                    #SUUMOで確認できるようにリンクを設置
                    st.write('▼賃貸情報サイトから問い合わせる：')
                    st.write(df_detail["詳細情報URL"].to_list()[0])
                else:
                    st.write(f'idが存在しません。0-{str(int(len(df))-1)}の間で入力してください。')
            except Exception as e:
                st.write(f'idが存在しません。0-{str(int(len(df))-1)}の間で入力してください。')
    except Exception as e:
        st.write('条件に未入力の項目があるか、条件に一致する物件がありません。')