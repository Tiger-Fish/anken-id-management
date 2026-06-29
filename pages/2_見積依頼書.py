"""見積依頼書管理"""
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import (init_db, get_all_ankens, get_anken,
                insert_quotation_request, get_all_quotation_requests,
                get_quotation_request_by_anken)
from datetime import date

init_db()
st.set_page_config(page_title="見積依頼書", page_icon=":memo:", layout="wide")
st.title("見積依頼書")
st.caption("案件IDを起点に、見積依頼書を自動生成・管理")

ankens = get_all_ankens()
if not ankens:
    st.warning("案件が登録されていません。先に案件登録してください。")
    st.stop()

selected = st.selectbox("案件IDを選択", [a["anken_id"] for a in ankens])
anken = get_anken(selected)

if anken:
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**顧客:** {anken['customer_name']}")
        st.info(f"**製品:** {anken['product_name']}")
    with col2:
        st.info(f"**数量:** {anken['quantity']}")
        st.info(f"**希望納期:** {anken['desired_delivery']}")

st.markdown("---")
existing = get_quotation_request_by_anken(selected)
if existing:
    st.success(f"見積依頼書 {existing['mq_no']} (依頼日: {existing['request_date']}) が登録済みです")
else:
    st.warning("見積依頼書は未登録です")

with st.form("qr_form"):
    st.subheader("見積依頼書の登録/更新")
    mq_no = st.text_input("見積依頼No", value=existing["mq_no"] if existing else f"MQ-{selected.split('-')[1]}-{selected.split('-')[2]}")
    request_date = st.date_input("依頼日", value=date.today())
    note = st.text_area("備考", value=existing["note"] if existing else "初回見積依頼")
    if st.form_submit_button("登録", type="primary"):
        insert_quotation_request({
            "mq_no": mq_no, "anken_id": selected,
            "request_date": str(request_date), "note": note,
        })
        st.success(f"見積依頼書 {mq_no} を登録しました!")
        st.rerun()

st.markdown("---")
st.subheader("全見積依頼一覧")
all_mq = get_all_quotation_requests()
if all_mq:
    import pandas as pd
    st.dataframe(pd.DataFrame(all_mq), use_container_width=True, hide_index=True)
