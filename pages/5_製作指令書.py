"""製作指令書 (自動発効判定)"""
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import (init_db, get_all_ankens, get_anken,
                get_quotation_response_by_anken, get_purchase_order_by_anken,
                insert_manufacturing_order, get_manufacturing_order_by_anken,
                get_all_manufacturing_orders)
from datetime import date

init_db()
st.set_page_config(page_title="製作指令書", page_icon=":factory:", layout="wide")
st.title("製作指令書")
st.caption("見積回答書 + 注文書 がそろえば自動発効")

ankens = get_all_ankens()
if not ankens:
    st.warning("案件が登録されていません。")
    st.stop()

selected = st.selectbox("案件IDを選択", [a["anken_id"] for a in ankens])
anken = get_anken(selected)

mr = get_quotation_response_by_anken(selected)
po = get_purchase_order_by_anken(selected)
mo = get_manufacturing_order_by_anken(selected)

mr_ok = mr and mr.get("amount", 0) > 0
po_ok = po and po.get("customer_po_no")
can_issue = bool(mr_ok and po_ok)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 見積回答書")
    if mr_ok:
        st.success(f"¥{mr['amount']:,}")
    else:
        st.error("未登録")
with col2:
    st.markdown("### 注文書")
    if po_ok:
        st.success(po["customer_po_no"])
    else:
        st.error("未受領")
with col3:
    st.markdown("### 製作指令書")
    if can_issue:
        st.success("発効可")
    elif not mr_ok:
        st.error("見積回答待ち")
    else:
        st.error("注文書未受領")

st.markdown("---")

if anken:
    st.subheader("製作指令書 内容")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**案件ID:** {selected}")
        st.write(f"**顧客名:** {anken['customer_name']}")
        st.write(f"**製品:** {anken['product_name']}")
        st.write(f"**図面番号:** {anken['drawing_no']}")
    with col2:
        qty = po["quantity"] if po and po.get("quantity") else anken["quantity"]
        st.write(f"**製造数量:** {qty}")
        st.write(f"**指定納期:** {po['delivery'] if po else anken['desired_delivery']}")
        st.write(f"**見積金額:** ¥{(mr['amount'] if mr else 0):,}")
        st.write(f"**注文金額:** ¥{(po['total'] if po else 0):,}")

st.markdown("---")

if can_issue:
    mo_no = mo["mo_no"] if mo else f"MO-{selected.split('-')[1]}-{selected.split('-')[2]}"
    if st.button("製作指令書を発効する", type="primary"):
        insert_manufacturing_order({
            "mo_no": mo_no, "anken_id": selected,
            "issued_date": str(date.today()), "status": "発効",
        })
        st.success(f"製作指令書 {mo_no} を発効しました! 工場に自動送信されました。")
        st.balloons()
        st.rerun()
    if mo and mo["status"] == "発効":
        st.info(f"製作指令書 {mo['mo_no']} (発効日: {mo['issued_date']}) は発効済みです。")
else:
    st.warning("見積回答書と注文書の両方が登録されると、製作指令書が発効可能になります。")

st.markdown("---")
st.subheader("発効済み製作指令一覧")
all_mo = get_all_manufacturing_orders()
if all_mo:
    import pandas as pd
    st.dataframe(pd.DataFrame(all_mo), use_container_width=True, hide_index=True)
