"""案件一覧 / 新規登録（PDFアップロード→自動抽出）"""
import streamlit as st
import pandas as pd
from datetime import date
from db import init_db, get_all_ankens, insert_anken, next_anken_id, insert_spec_extract
from pdf_utils import extract_text_from_pdf, extract_items_heuristic, extract_items_demo

init_db()
st.set_page_config(page_title="案件登録", page_icon="📁", layout="wide")
st.title("📁 案件一覧 / 新規登録")

tab1, tab2 = st.tabs(["📋 案件一覧", "➕ 新規登録（PDFアップロード）"])

with tab1:
    ankens = get_all_ankens()
    if ankens:
        df = pd.DataFrame(ankens)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("案件が未登録です。「新規登録」タブからPDFをアップロードしてください。")

with tab2:
    st.subheader("顧客要求仕様書から新規案件を登録")

    col_upload, col_demo = st.columns([2, 1])
    with col_upload:
        uploaded = st.file_uploader(
            "顧客要求仕様書 PDF をドラッグ＆ドロップ",
            type=["pdf"],
            help="PDFをアップロードすると仕様項目を自動抽出します"
        )
    with col_demo:
        st.markdown("#### 🎯 デモ用クイック入力")
        demo_customer = st.selectbox("顧客を選択", ["富士電機株式会社", "川崎重工業株式会社", "明電舎"])
        use_demo = st.button("📋 デモデータを読込む", type="secondary")

    extracted = {}
    source_label = ""

    if uploaded:
        with st.spinner("PDFを解析中..."):
            text = extract_text_from_pdf(uploaded)
            extracted = extract_items_heuristic(text)
            if not extracted:
                extracted = extract_items_demo(uploaded.name)
                source_label = "⚡ デモデータで代替（PDF解析不可）"
            else:
                source_label = "✅ PDFから自動抽出"

        st.success(f"{source_label}")
        with st.expander("抽出した項目を確認", expanded=True):
            st.json(extracted)

    elif use_demo:
        extracted = extract_items_demo(demo_customer)
        extracted["顧客(推定)"] = demo_customer
        source_label = f"🎯 デモデータ（{demo_customer}）"
        st.success(source_label)
        with st.expander("抽出した項目を確認", expanded=True):
            st.json(extracted)

    st.markdown("---")
    st.subheader("案件情報を確認・編集して登録")

    next_id = next_anken_id()
    col1, col2 = st.columns(2)
    with col1:
        anken_id      = st.text_input("案件ID（自動採番）", value=next_id, disabled=True)
        customer_name = st.text_input("顧客名", value=extracted.get("顧客(推定)") or extracted.get("顧客名", ""))
        product_name  = st.text_input("製品名", value=extracted.get("製品名", "乾式DCフィルタコンデンサ"))
        spec_no       = st.text_input("仕様書番号", value=extracted.get("仕様書番号", ""))
        drawing_no    = st.text_input("図面番号",   value=extracted.get("図面番号", ""))
    with col2:
        anken_name = st.text_input("案件名", value=f"{customer_name}向け{product_name}" if customer_name else "")
        try:
            qty = int(str(extracted.get("数量", "0")).replace(",", "") or 0)
        except ValueError:
            qty = 0
        quantity         = st.number_input("数量", min_value=0, value=qty or 1)
        desired_delivery = st.text_input("希望納期", value=extracted.get("希望納期", ""))
        sales_rep        = st.text_input("営業担当", value="和田 孝雄")
        registered_date  = st.date_input("登録日", value=date.today())

    if st.button("✅ 案件を登録する", type="primary", disabled=not customer_name):
        insert_anken({
            "anken_id": anken_id, "anken_name": anken_name,
            "customer_name": customer_name, "product_name": product_name,
            "spec_no": spec_no, "drawing_no": drawing_no,
            "quantity": int(quantity), "desired_delivery": desired_delivery,
            "sales_rep": sales_rep, "registered_date": str(registered_date),
        })
        for k, v in extracted.items():
            if v:
                insert_spec_extract(anken_id, k, str(v))
        st.success(f"🎉 案件 **{anken_id}** を登録しました！")
        st.balloons()
        st.info("次のステップ：左メニューの「見積依頼書」へ進んでください ➡️")
