"""見積回答書 受領"""
import streamlit as st
import pandas as pd
from datetime import date
from db import init_db, get_all_ankens, get_anken, insert_quotation_response, get_quotation_response_by_anken, get_quotation_request_by_anken

init_db()
st.set_page_config(page_title="見積回答書", page_icon="💰", layout="wide")
st.title("💰 見積回答書")
st.caption("工場・技術部門からの見積回答を案件IDで管理")

ankens = get_all_ankens()
if not ankens:
    st.warning("案件が登録されていません。")
    st.stop()

selected = st.selectbox("案件IDを選択", [a["anken_id"] for a in ankens],
                        format_func=lambda x: f"{x}  {st.session_state.ankens.get(x,{}).get('customer_name','')}")
anken = get_anken(selected)

mq = get_quotation_request_by_anken(selected)
if not mq:
    st.warning("⚠️ 見積依頼書が未発行です。先に「見積依頼書」ページで発行してください。")
    st.stop()

if anken:
    col1, col2, col3 = st.columns(3)
    col1.info(f"**顧客:** {anken['customer_name']}")
    col2.info(f"**製品:** {anken['product_name']}")
    col3.info(f"**数量:** {anken['quantity']}")

existing = get_quotation_response_by_anken(selected)
if existing and existing.get("amount", 0) > 0:
    st.success(f"✅ 見積回答書 **{existing['mr_no']}** 登録済（¥{existing['amount']:,}）")

st.markdown("---")
st.subheader("見積回答を入力")

mr_no = f"MR-{selected.split('-')[1]}-{selected.split('-')[2]}" if not existing else existing["mr_no"]

col1, col2 = st.columns(2)
with col1:
    amount        = st.number_input("見積金額（円）", min_value=0,
                                    value=existing["amount"] if existing else 0, step=100000)
    material_cost = st.number_input("材料費 MC（円）", min_value=0,
                                    value=existing.get("material_cost", 0) if existing else 0, step=100000)
with col2:
    delivery      = st.text_input("見積納期", value=existing["delivery"] if existing else anken["desired_delivery"])
    response_date = st.date_input("回答日", value=date.today())
    note          = st.text_area("備考", value=existing.get("note", "") if existing else "")

if amount > 0:
    margin = amount - material_cost
    margin_rate = margin / amount * 100 if amount else 0
    m1, m2, m3 = st.columns(3)
    m1.metric("見積金額", f"¥{amount:,}")
    m2.metric("粗利",     f"¥{margin:,}")
    m3.metric("粗利率",   f"{margin_rate:.1f}%")

if st.button("💾 見積回答書を登録する", type="primary"):
    insert_quotation_response({
        "mr_no": mr_no, "anken_id": selected,
        "amount": int(amount), "delivery": delivery,
        "response_date": str(response_date),
        "material_cost": int(material_cost), "note": note,
    })
    st.success(f"🎉 見積回答書 **{mr_no}** を登録しました！")
    st.info("次のステップ：営業活動で受注後、「注文書」ページで注文書を受領してください ➡️")
    st.rerun()
