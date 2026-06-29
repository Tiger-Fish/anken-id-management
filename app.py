"""
案件ID管理アプリ - 指月電機 営業DXプロトタイプ
起動: streamlit run app.py
"""
import streamlit as st
import pandas as pd
from db import init_db, get_dashboard_data

st.set_page_config(
    page_title="案件ID管理 - 指月電機 営業DX",
    page_icon="📋",
    layout="wide",
)

init_db()

st.sidebar.title("📋 案件ID管理")
st.sidebar.markdown("**指月電機 営業DXプロトタイプ**")
st.sidebar.markdown("---")
st.sidebar.info("""
**操作フロー**
1. 📁 案件登録（PDF→自動抽出）
2. 📝 見積依頼書 発行
3. 💰 見積回答書 受領
4. 📦 注文書 受領
5. 🏭 製作指令書 自動発効
""")
st.sidebar.markdown("---")
st.sidebar.caption("⚠️ デモ版：データはセッション内のみ保持")

st.title("🏠 案件進捗ダッシュボード")
st.caption("案件IDを起点に、顧客要求仕様書から製作指令書まで一気通貫管理")

data = get_dashboard_data()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📁 総案件数",    data["total"])
c2.metric("📄 仕様受領",    data["spec_received"])
c3.metric("📝 見積依頼中",  data["quotation_requested"])
c4.metric("📦 受注済",      data["ordered"])
c5.metric("🏭 製作指令発効", data["mo_issued"])

st.markdown("---")
st.subheader("案件別進捗マップ")

if not data["ankens"]:
    st.info("案件が未登録です。左メニューの「案件登録」からPDFをアップロードしてください。")
else:
    df = pd.DataFrame(data["ankens"])
    st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")

# フロー図
st.subheader("業務フロー")
cols = st.columns(5)
steps = [
    ("📄", "①仕様受領", "顧客要求仕様書PDF\nをアップロード"),
    ("📝", "②見積依頼", "工場・技術部門へ\n見積依頼書を発行"),
    ("💰", "③見積回答", "原価・納期を\n見積回答書で受領"),
    ("📦", "④注文受領", "顧客発注書を\n案件IDで照合"),
    ("🏭", "⑤製作指令", "条件充足で\n製作指令書を自動発効"),
]
for col, (icon, title, desc) in zip(cols, steps):
    col.markdown(f"### {icon} {title}")
    col.caption(desc)

st.markdown("---")
st.caption("このアプリはプロトタイプです。本番運用には認証・監査・暗号化等の強化が必要です。")
