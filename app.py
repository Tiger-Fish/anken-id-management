"""
案件ID管理アプリ - 指月電機 営業DXプロトタイプ
メインエントリ(ダッシュボード)
起動: streamlit run app.py
"""
import streamlit as st
import pandas as pd
from db import init_db, get_dashboard_data

st.set_page_config(
    page_title="案件ID管理 - 指月電機 営業DX",
    page_icon=":clipboard:",
    layout="wide",
)

init_db()

st.sidebar.title(":clipboard: 案件ID管理")
st.sidebar.markdown("**指月電機 営業DXプロトタイプ**")
st.sidebar.markdown("---")
st.sidebar.markdown("### メニュー")
st.sidebar.markdown("""
- ダッシュボード (このページ)
- 案件一覧/新規登録
- 見積依頼書
- 見積回答書
- 注文書
- 製作指令書
""")
st.sidebar.info("左のpagesメニューから各機能にアクセスできます。")

st.title(":house: 案件進捗ダッシュボード")
st.caption("案件IDを起点に、顧客要求仕様書から製作指令書まで一気通貫管理")

data = get_dashboard_data()
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("総案件数", data["total"])
c2.metric("仕様受領", data["spec_received"])
c3.metric("見積依頼中", data["quotation_requested"])
c4.metric("受注済", data["ordered"])
c5.metric("製作指令発効", data["mo_issued"])

st.markdown("---")
st.subheader("案件別進捗")
if not data["ankens"]:
    st.warning("案件が登録されていません。サンプル投入: python sample_data.py")
else:
    df = pd.DataFrame(data["ankens"])
    st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("このアプリはプロトタイプです。本番運用には認証・監査・暗号化等の強化が必要です。")
