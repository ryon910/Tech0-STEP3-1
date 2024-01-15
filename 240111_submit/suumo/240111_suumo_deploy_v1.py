import os
import pandas as pd
import sqlite3
import streamlit as st

def load_data():
    # 現在のファイルのディレクトリを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # データベースファイルへのパスを構築
    db_path = os.path.join(current_dir, 'suumo.db')
    # データベースに接続
    conn = sqlite3.connect(db_path)
    # SQLクエリを実行し、結果をDataFrameに読み込む
    query = "SELECT * FROM suumo_clean"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df = load_data()

# スラッシュを入れると後々query()が正常に動作しなかったので、カラム名修正
df.rename(columns={
    'age/year':'age',
    'rent/yen':'rent',
    'floor/F':'floor',
    'admin/yen':'admin',
    'deposit/yen':'deposit',
    'gratuity/yen':'gratuity',
    'menseki/m2':'menseki',
    'access1_walk/min':'access1_walk',
    'access2_walk/min':'access2_walk',
    'access3_walk/min':'access3_walk'
    }, inplace=True)

# 徒歩時間がobject形式なので、int形式に変換。欠損値は平均値で埋めた方が良いかも。
df['access1_walk'] = pd.to_numeric(df['access1_walk'], errors='coerce')
df['access2_walk'] = pd.to_numeric(df['access2_walk'], errors='coerce')
df['access3_walk'] = pd.to_numeric(df['access3_walk'], errors='coerce')

#希望条件
#駅リスト
station_list = [
    '東京駅', '有楽町駅', '新橋駅', '浜松町駅', '田町駅', '高輪ゲートウェイ駅', '品川駅',
    '大崎駅', '五反田駅', '目黒駅', '恵比寿駅', '渋谷駅', '原宿駅', '代々木駅', '新宿駅',
    '新大久保駅', '高田馬場駅', '目白駅', '池袋駅', '大塚駅', '巣鴨駅', '駒込駅', '田端駅',
    '西日暮里駅', '鶯谷駅', '上野駅', '御徒町駅', '秋葉原駅', '神田駅'
    ]
#間取りリスト
madori_list = [
    '2DK', '2LDK', '3DK', '3SDK', '2K', '3K', '3LDK', '4K', '4LDK',
    '2SLDK', '3SLDK', '4SK', '3SK', '2SDK', '2SK', '4SLDK'
    ]
col1, col2, col3 = st.columns([9,2,2])
with col2:
    st.button('会員登録', type='secondary')
with col3:
    st.button('Login', type='secondary')

st.title('物件情報検索アプリ')
st.write('山手線沿線で、2DK以上の2人暮らし向け賃貸を、重複なく効率よく探すことができます。')

st.sidebar.title('希望条件を入力してください')

st.sidebar.text('1.最寄駅')
station_select = st.sidebar.multiselect('希望の最寄駅を選択してください（複数選択可）', station_list)

st.sidebar.text('2.賃料')
min_rent, max_rent = st.sidebar.slider(
    '賃料（万円）の範囲を入力してください',
    min_value = 0,
    max_value = 30,
    value = (0, 30))
min_rent_yen = min_rent * 10000
max_rent_yen = max_rent * 10000

st.sidebar.text('3.駅徒歩')
min_walk_time, max_walk_time = st.sidebar.slider(
    '駅徒歩時間（分）の範囲を入力してください',
    min_value = 0,
    max_value = 30,
    value = (0, 30))

st.sidebar.text('4.間取り')
madori_select = st.sidebar.multiselect('希望の間取りを選択してください（複数選択可）', madori_list)

st.sidebar.text('5.築年数')
min_age, max_age = st.sidebar.slider(
    '築年数の範囲を入力してください',
    min_value = 0,
    max_value = 100,
    value = (0, 50))

st.sidebar.text('6.占有面積')
min_menseki, max_menseki = st.sidebar.slider(
    '占有面積（m2）の範囲を入力してください',
    min_value = 0,
    max_value = 150,
    value = (0, 75))

button = st.sidebar.button('検索',type = 'primary')

# 検索条件でデータを絞り込む
df_ = df.query(
    f'(access1_station == {station_select}) and ({min_rent_yen} <= rent <= {max_rent_yen}) and ({min_walk_time} <= access1_walk <= {max_walk_time}) and (madori == {madori_select}) and ({min_age} <= age <= {max_age})  and ({min_menseki} <= menseki <= {max_menseki})')
# 検索結果のヒット件数を取得
hit = len(df_)

# 検索ボタンを押した際に、結果を表示
if button == True:
    st.write('■ 検索結果')
    st.write(f'▼ ヒット件数：{hit}件')
    st.write('▼ 物件一覧：')
    st.dataframe(df_, width=700, height=300)
    st.write('▼ マップ：')
