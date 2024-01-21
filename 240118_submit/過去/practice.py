import streamlit as st

if 'count' not in st.session_state:
    st.session_state['count'] = 0

if st.button('カウントアップ'):
    st.session_state['count'] += 1

st.write('カウント:', st.session_state['count'])


# 各ボタンのクリック状態を初期化
if 'button_search_clicked' not in st.session_state:
    st.session_state['button_clicked'] = False

if 'button2_clicked' not in st.session_state:
    st.session_state['button2_clicked'] = False

# ボタン1
if st.button('ボタン1'):
    st.session_state['button1_clicked'] = True

# ボタン1がクリックされた場合の処理
if st.session_state['button1_clicked']:
    st.write("ボタン1がクリックされました。")

# ボタン2
if st.button('ボタン2'):
    st.session_state['button2_clicked'] = True

# ボタン2がクリックされた場合の処理
if st.session_state['button2_clicked']:
    st.write("ボタン2がクリックされました。")