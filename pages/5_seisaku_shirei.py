"""製作指令書 自動発効"""
import streamlit as st
import pandas as pd
from datetime import date
from db import (init_db, get_all_ankens, get_anken,
                get_quotation_response_by_anken, get_purchase_order_by_anken,
                insert_manufacturing_order, get_manufacturing_order_by_anken,
                get_all_manufacturing_orders, get_spec_extracts)

init_db()
st.set_page_config(page_title="製作指令書", page_icon="🏭", layout="wide")
st.title("🏭 製作指令書")
st.caption("見積回答書 ＋ 注文書 がそろうと自動発効可能になります")

ankens = get_all_ankens()
if not ankens:
    st.warning("案件が登録されていません。")
    st.stop()

selected = st.selectbox("案件IDを選択", [a["anken_id"] for a in ankens],
                        format_func=lambda x: f"{x}  {st.session_state.ankens.get(x,{}).get('customer_name','')}")
anken = get_anken(selected)
specs = get_spec_extracts(selected)
mr = get_quotation_response_by_anken(selected)
po = get_purchase_order_by_anken(selected)
mo = get_manufacturing_order_by_anken(selected)

mr_ok = bool(mr and mr.get("amount", 0) > 0)
po_ok = bool(po and po.get("customer_po_no"))
can_issue = mr_ok and po_ok

# 発効条件ステータス
st.subheader("発効条件チェック")
col1, col2, col3 = st.columns(3)
with col1:
    if mr_ok:
        st.success(f"✅ 見積回答書\n¥{mr['amount']:,}")
    else:
        st.error("❌ 見積回答書\n未登録")
with col2:
    if po_ok:
        st.success(f"✅ 注文書\n{po['customer_po_no']}")
    else:
        st.error("❌ 注文書\n未受領")
with col3:
    if mo and mo["status"] == "発効":
        st.success(f"✅ 製作指令書\n発効済（{mo['issued_date']}）")
    elif can_issue:
        st.warning("⚡ 製作指令書\n**発効可能**")
    else:
        st.error("⏳ 製作指令書\n条件未充足")

st.markdown("---")

if anken:
    st.subheader("製作指令書 内容")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
| 項目 | 内容 |
|------|------|
| 製作指令No | MO-{selected.split('-')[1]}-{selected.split('-')[2]} |
| 案件ID | {selected} |
| 顧客名 | {anken['customer_name']} |
| 製品名 | {anken['product_name']} |
| 図面番号 | {anken.get('drawing_no', '-')} |
| 製造数量 | {po['quantity'] if po else anken['quantity']} |
| 指定納期 | {po['delivery'] if po else anken['desired_delivery']} |
| 見積金額 | ¥{mr['amount']:,} |
| 注文金額 | ¥{po['total']:,} |
""" if (mr and po) else f"""
| 項目 | 内容 |
|------|------|
| 案件ID | {selected} |
| 顧客名 | {anken['customer_name']} |
| 製品名 | {anken['product_name']} |
""")
    with col2:
        if specs:
            st.markdown("**仕様項目**")
            st.dataframe(
                pd.DataFrame([{"項目": s["item"], "内容": s["value"]} for s in specs]),
                hide_index=True, use_container_width=True
            )

st.markdown("---")

if mo and mo["status"] == "発効":
    st.info(f"ℹ️ 製作指令書 **{mo['mo_no']}** は {mo['issued_date']} に発効済みです。")

elif can_issue:
    st.markdown("### ⚡ 発効条件が揃いました！")
    mo_no = f"MO-{selected.split('-')[1]}-{selected.split('-')[2]}"
    if st.button("🚀 製作指令書を発効する", type="primary"):
        insert_manufacturing_order({
            "mo_no": mo_no, "anken_id": selected,
            "issued_date": str(date.today()), "status": "発効",
        })
        st.success(f"🎉 製作指令書 **{mo_no}** を発効しました！工場へ製造指示を送信しました。")
        st.balloons()
        st.rerun()
else:
    missing = []
    if not mr_ok: missing.append("見積回答書の登録")
    if not po_ok: missing.append("注文書の受領")
    st.warning(f"発効には以下が必要です：{' / '.join(missing)}")

st.markdown("---")
st.subheader("発効済み製作指令一覧")
all_mo = get_all_manufacturing_orders()
if all_mo:
    st.dataframe(pd.DataFrame(all_mo), use_container_width=True, hide_index=True)
else:
    st.info("発効済みの製作指令書はありません。")
