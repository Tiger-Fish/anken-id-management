"""見積回答書管理"""
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import (init_db, get_all_ankens, get_anken,
                insert_quotation_response, get_all_quotation_responses,
                get_quotation_response_by_anken)
from datetime import date

init_db()
st.set_page_config(page_title="見積回答書", page_icon=":moneybag:", layout="wide")
st.title("見積回答書")
st.caption("工場・技術部門からの見積回答を案件IDで管理")

ankens = get_all_ankens()
if not ankens:
    st.warning("案件が登録されていません。")
    st.stop()

selected = st.selectbox("案件IDを選択", [a["anken_id"] for a in ankens])
anken = get_anken(selected)

if anken:
    st.info(f"**顧客:** {anken['customer_name']}  |  **製品:** {anken['product_name']}  |  **数量:** {anken['quantity']}")

existing = get_quotation_response_by_anken(selected)
if existing and existing["amount"] > 0:
    st.success(f"見積回答書 {existing['mr_no']} 登録済 (金額: ¥{existing['amount']:,})")
else:
    st.warning("見積回答書は未登録または金額未設定です")

with st.form("mr_form"):
    st.subheader("見積回答書の登録/更新")
    col1, col2 = st.columns(2)
    with col1:
        mr_no = st.text_input("見積回答No", value=existing["mr_no"] if existing else f"MR-{selected.split('-')[1]}-{selected.split('-')[2]}")
        amount = st.number_input("見積金額 (円)", min_value=0, value=existing["amount"] if existing else 0, step=10000)
        material_cost = st.number_input("MC(材料費)", min_value=0, value=existing["material_cost"] if existing else 0, step=10000)
    with col2:
        delivery = st.text_input("見積納期", value=existing["delivery"] if existing else "")
        response_date = st.date_input("回答日", value=date.today())
        note = st.text_area("備考", value=existing["note"] if existing else "")
    if st.form_submit_button("登録", type="primary"):
        insert_quotation_response({
            "mr_no": mr_no, "anken_id": selected,
            "amount": int(amount), "delivery": delivery,
            "response_date": str(response_date),
            "material_cost": int(material_cost), "note": note,
        })
        st.success(f"見積回答書 {mr_no} を登録しました!")
        st.rerun()

st.markdown("---")
st.subheader("全見積回答一覧")
all_mr = get_all_quotation_responses()
if all_mr:
    import pandas as pd
    st.dataframe(pd.DataFrame(all_mr), use_container_width=True, hide_index=True)
