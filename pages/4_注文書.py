"""注文書(受領)管理"""
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import (init_db, get_all_ankens, get_anken,
                insert_purchase_order, get_all_purchase_orders,
                get_purchase_order_by_anken, get_quotation_response_by_anken)
from datetime import date

init_db()
st.set_page_config(page_title="注文書", page_icon=":package:", layout="wide")
st.title("注文書(受領)")
st.caption("顧客からの注文書を案件IDで管理。見積回答書と自動照合")

ankens = get_all_ankens()
if not ankens:
    st.warning("案件が登録されていません。")
    st.stop()

selected = st.selectbox("案件IDを選択", [a["anken_id"] for a in ankens])
anken = get_anken(selected)

if anken:
    st.info(f"**顧客:** {anken['customer_name']}  |  **製品:** {anken['product_name']}  |  **希望納期:** {anken['desired_delivery']}")

mr = get_quotation_response_by_anken(selected)
if mr and mr["amount"] > 0:
    st.success(f"見積回答済: ¥{mr['amount']:,} / 納期 {mr['delivery']}")
else:
    st.warning("見積回答書がまだ登録されていません")

existing = get_purchase_order_by_anken(selected)
if existing and existing.get("customer_po_no"):
    st.success(f"注文書 {existing['po_no']} 受領済 (顧客発注No: {existing['customer_po_no']})")

with st.form("po_form"):
    st.subheader("注文書の登録/更新")
    col1, col2 = st.columns(2)
    with col1:
        po_no = st.text_input("注文書受付No", value=existing["po_no"] if existing else f"PO-{selected.split('-')[1]}-{selected.split('-')[2]}")
        customer_po_no = st.text_input("顧客発注番号", value=existing["customer_po_no"] if existing else "")
        quantity = st.number_input("数量", min_value=0, value=existing["quantity"] if existing else (anken["quantity"] if anken else 0))
    with col2:
        unit_price = st.number_input("単価 (円)", min_value=0, value=existing["unit_price"] if existing else 0, step=1000)
        delivery = st.text_input("指定納期", value=existing["delivery"] if existing else (anken["desired_delivery"] if anken else ""))
        received_date = st.date_input("受領日", value=date.today())
    note = st.text_area("備考", value=existing["note"] if existing else "")

    total = quantity * unit_price
    st.metric("合計金額", f"¥{total:,}")

    if mr and mr["amount"] > 0 and total > 0:
        diff = total - mr["amount"]
        if diff == 0:
            st.success("見積回答と注文金額が一致")
        elif abs(diff) < mr["amount"] * 0.05:
            st.info(f"差額 ¥{diff:+,} (5%以内)")
        else:
            st.warning(f"差額 ¥{diff:+,} (要確認)")

    if st.form_submit_button("登録", type="primary"):
        insert_purchase_order({
            "po_no": po_no, "anken_id": selected,
            "customer_po_no": customer_po_no,
            "quantity": int(quantity), "unit_price": int(unit_price),
            "total": int(total), "delivery": delivery,
            "received_date": str(received_date), "note": note,
        })
        st.success(f"注文書 {po_no} を登録しました!")
        st.rerun()

st.markdown("---")
st.subheader("全注文書一覧")
all_po = get_all_purchase_orders()
if all_po:
    import pandas as pd
    st.dataframe(pd.DataFrame(all_po), use_container_width=True, hide_index=True)
