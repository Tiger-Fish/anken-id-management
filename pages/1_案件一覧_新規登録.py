"""案件一覧/新規登録ページ"""
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import (init_db, get_all_ankens, insert_anken, next_anken_id,
                insert_spec_extract)
from pdf_utils import extract_text_from_pdf, extract_items_heuristic
from ai_utils import has_azure_openai, extract_items_with_llm
from datetime import date

init_db()
st.set_page_config(page_title="案件一覧/新規登録", page_icon=":file_folder:", layout="wide")
st.title("案件一覧 / 新規登録")

tab1, tab2 = st.tabs(["案件一覧", "新規登録 (PDFアップロード)"])

with tab1:
    st.subheader("登録済み案件")
    ankens = get_all_ankens()
    if ankens:
        import pandas as pd
        df = pd.DataFrame(ankens)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("案件が未登録です。隣のタブから登録するか、python sample_data.py を実行してください。")

with tab2:
    st.subheader("顧客要求仕様書から新規案件を登録")
    st.caption("PDFをアップロードすると、AIが項目を抽出してフォームに自動入力します。")

    uploaded = st.file_uploader("顧客要求仕様書 PDFをアップロード", type=["pdf"])

    extracted = {}
    if uploaded:
        with st.spinner("PDFを解析中..."):
            text = extract_text_from_pdf(uploaded)
            if has_azure_openai():
                st.info("Azure OpenAIで構造化抽出中...")
                extracted = extract_items_with_llm(text)
            if not extracted:
                extracted = extract_items_heuristic(text)

        with st.expander("抽出した項目を確認", expanded=True):
            st.json(extracted)

    st.markdown("---")
    st.subheader("案件情報")
    next_id = next_anken_id()

    col1, col2 = st.columns(2)
    with col1:
        anken_id = st.text_input("案件ID (自動採番)", value=next_id)
        customer_name = st.text_input("顧客名", value=extracted.get("顧客名") or extracted.get("顧客(推定)", ""))
        product_name = st.text_input("製品名", value=extracted.get("製品名", ""))
        spec_no = st.text_input("仕様書番号", value=extracted.get("仕様書番号", ""))
        drawing_no = st.text_input("図面番号", value=extracted.get("図面番号", ""))
    with col2:
        anken_name = st.text_input("案件名", value=f"{customer_name}向け{product_name}" if customer_name and product_name else "")
        try:
            qty = int(str(extracted.get("数量", "0")).replace(",", "") or 0)
        except ValueError:
            qty = 0
        quantity = st.number_input("数量", min_value=0, value=qty)
        desired_delivery = st.text_input("希望納期", value=extracted.get("希望納期", ""))
        sales_rep = st.text_input("営業担当", value="和田 孝雄")
        registered_date = st.date_input("登録日", value=date.today())

    if st.button("案件を登録", type="primary"):
        try:
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
            st.success(f"案件 {anken_id} を登録しました!")
            st.balloons()
        except Exception as e:
            st.error(f"登録エラー: {e}")
