"""注文書 受領"""
import streamlit as st
import pandas as pd
from datetime import date
from db import (init_db, get_all_ankens, get_anken,
                insert_purchase_order, get_purchase_order_by_anken,
                get_quotation_response_by_anken)

init_db()
st.set_page_config(page_title="注文書", page_icon="📦", layout="wide")
st.title("📦 注文書（受領）")
st.caption("顧客からの注文書を案件IDで管理。見積回答書と自動照合")

ankens = get_all_ankens()
if not ankens:
    st.warning("案件が登録されていません。")
    st.stop()

selected = st.selectbox("案件IDを選択", [a["anken_id"] for a in ankens],
                        format_func=lambda x: f"{x}  {st.session_state.ankens.get(x,{}).get('customer_name','')}")
anken = get_anken(selected)

mr = get_quotation_response_by_anken(selected)
if not mr or mr.get("amount", 0) == 0:
    st.warning("⚠️ 見積回答書が未登録です。先に「見積回答書」ページで登録してください。")
    st.stop()

st.success(f"✅ 見積回答済：¥{mr['amount']:,}  納期 {mr['delivery']}")

existing = get_purchase_order_by_anken(selected)
if existing and existing.get("customer_po_no"):
    st.success(f"✅ 注文書 **{existing['po_no']}** 受領済（顧客発注No: {existing['customer_po_no']}）")

st.markdown("---")
st.subheader("注文書の内容を入力")

po_no = f"PO-{selected.split('-')[1]}-{selected.split('-')[2]}" if not existing else existing["po_no"]

col1, col2 = st.columns(2)
with col1:
    customer_po_no = st.text_input("顧客発注番号", value=existing.get("customer_po_no", "") if existing else "")
    quantity       = st.number_input("数量", min_value=0,
                                     value=existing["quantity"] if existing else anken["quantity"])
    unit_price     = st.number_input("単価（円）", min_value=0,
                                     value=existing.get("unit_price", 0) if existing else 0, step=1000)
with col2:
    delivery       = st.text_input("指定納期", value=existing["delivery"] if existing else anken["desired_delivery"])
    received_date  = st.date_input("受領日", value=date.today())
    note           = st.text_area("備考", value=existing.get("note", "") if existing else "")

total = quantity * unit_price
st.metric("合計金額", f"¥{total:,}")

if mr and mr["amount"] > 0 and total > 0:
    diff = total - mr["amount"]
    if diff == 0:
        st.success("✅ 見積金額と注文金額が一致しています")
    elif abs(diff) < mr["amount"] * 0.05:
        st.info(f"ℹ️ 差額 ¥{diff:+,}（5%以内：許容範囲）")
    else:
        st.warning(f"⚠️ 差額 ¥{diff:+,}（要確認）")

if st.button("📥 注文書を受領登録する", type="primary", disabled=not customer_po_no):
    insert_purchase_order({
        "po_no": po_no, "anken_id": selected,
        "customer_po_no": customer_po_no,
        "quantity": int(quantity), "unit_price": int(unit_price),
        "total": int(total), "delivery": delivery,
        "received_date": str(received_date), "note": note,
    })
    st.success(f"🎉 注文書 **{po_no}** を受領登録しました！")
    st.info("次のステップ：「製作指令書」ページで製作指令書を発効してください ➡️")
    st.rerun()
