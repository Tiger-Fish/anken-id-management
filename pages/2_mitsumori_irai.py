"""見積依頼書 発行"""
import streamlit as st
import pandas as pd
from datetime import date
from db import init_db, get_all_ankens, get_anken, insert_quotation_request, get_quotation_request_by_anken, get_spec_extracts

init_db()
st.set_page_config(page_title="見積依頼書", page_icon="📝", layout="wide")
st.title("📝 見積依頼書")
st.caption("案件IDを起点に、工場・技術部門へ見積依頼書を発行")

ankens = get_all_ankens()
if not ankens:
    st.warning("案件が登録されていません。まず「案件登録」ページで登録してください。")
    st.stop()

selected = st.selectbox("案件IDを選択", [a["anken_id"] for a in ankens],
                        format_func=lambda x: f"{x}  {st.session_state.ankens.get(x,{}).get('customer_name','')}")
anken = get_anken(selected)
specs = get_spec_extracts(selected)

if anken:
    col1, col2, col3 = st.columns(3)
    col1.info(f"**顧客:** {anken['customer_name']}")
    col2.info(f"**製品:** {anken['product_name']}")
    col3.info(f"**希望納期:** {anken['desired_delivery']}")

existing = get_quotation_request_by_anken(selected)
if existing:
    st.success(f"✅ 見積依頼書 **{existing['mq_no']}** 発行済（{existing['request_date']}）")

st.markdown("---")
st.subheader("見積依頼書 プレビュー")

if specs:
    spec_df = pd.DataFrame([{"項目": s["item"], "内容": s["value"]} for s in specs])
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown(f"""
| 項目 | 内容 |
|------|------|
| 宛先 | 製造技術部 |
| 案件ID | {selected} |
| 顧客名 | {anken['customer_name']} |
| 製品名 | {anken['product_name']} |
| 仕様書番号 | {anken.get('spec_no', '-')} |
| 数量 | {anken['quantity']} |
| 希望納期 | {anken['desired_delivery']} |
""")
    with col_right:
        st.markdown("**抽出仕様項目**")
        st.dataframe(spec_df, hide_index=True, use_container_width=True)

mq_no = f"MQ-{selected.split('-')[1]}-{selected.split('-')[2]}" if not existing else existing["mq_no"]
note  = st.text_area("備考", value=existing["note"] if existing else "初回見積依頼")

if st.button("📤 見積依頼書を発行する", type="primary"):
    insert_quotation_request({
        "mq_no": mq_no, "anken_id": selected,
        "request_date": str(date.today()), "note": note,
    })
    st.success(f"🎉 見積依頼書 **{mq_no}** を発行しました！")
    st.info("次のステップ：「見積回答書」ページで工場からの回答を入力してください ➡️")
    st.rerun()
