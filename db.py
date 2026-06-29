"""
セッションベースのインメモリDB（Streamlit Cloud対応）
"""
import streamlit as st
from datetime import datetime

def init_db():
    if "db_initialized" not in st.session_state:
        st.session_state.ankens = {}
        st.session_state.spec_extracts = []
        st.session_state.quotation_requests = {}
        st.session_state.quotation_responses = {}
        st.session_state.purchase_orders = {}
        st.session_state.manufacturing_orders = {}
        st.session_state.db_initialized = True
        _load_sample_data()

def _load_sample_data():
    # ANK-2026-0001: 三菱電機（製作指令発効済）
    insert_anken({
        "anken_id": "ANK-2026-0001",
        "anken_name": "E10向け3レベルCI用フィルタコンデンサ",
        "customer_name": "三菱電機株式会社",
        "product_name": "ヒューズ機能付き乾式DCフィルタコンデンサ",
        "spec_no": "IKO-A71517-A",
        "drawing_no": "H7V1657001",
        "quantity": 100,
        "desired_delivery": "2026-09-30",
        "sales_rep": "和田 孝雄",
        "registered_date": "2026-06-01",
    })
    for item, val, note in [
        ("仕様書番号", "IKO-A71517-A", "改定A、2026-02-05"),
        ("静電容量", "2000µF -5/+5% x 4回路", ""),
        ("定格電圧 UNDC", "1650V DC", ""),
        ("定格電流", "297Arms / 4000µF @70℃", ""),
        ("製品保証期間", "納入後 2年", ""),
        ("設計保証期間", "納入後 5年", ""),
        ("製品寿命", "20年 / 126,000時間 @平均45℃", ""),
        ("適用規格", "IEC61881-1, IEC60077-1, IEC61287-1", ""),
    ]:
        insert_spec_extract("ANK-2026-0001", item, val, note)
    insert_quotation_request({"mq_no": "MQ-2026-0001", "anken_id": "ANK-2026-0001", "request_date": "2026-06-02", "note": "初回見積依頼"})
    insert_quotation_response({"mr_no": "MR-2026-0001", "anken_id": "ANK-2026-0001", "amount": 48000000, "delivery": "2026-09-25", "response_date": "2026-06-15", "material_cost": 32000000, "note": "IEC61881-1準拠"})
    insert_purchase_order({"po_no": "PO-2026-0001", "anken_id": "ANK-2026-0001", "customer_po_no": "MEL-PO-2026-3345", "quantity": 100, "unit_price": 480000, "total": 48000000, "delivery": "2026-09-30", "received_date": "2026-07-01", "note": "EDI受領"})
    insert_manufacturing_order({"mo_no": "MO-2026-0001", "anken_id": "ANK-2026-0001", "issued_date": "2026-07-02", "status": "発効"})

    # ANK-2026-0002: 東芝（見積回答済）
    insert_anken({
        "anken_id": "ANK-2026-0002",
        "anken_name": "AF盤向け力率改善コンデンサ",
        "customer_name": "東芝インフラシステムズ",
        "product_name": "AF用コンデンサ",
        "spec_no": "TAF-2026-015",
        "drawing_no": "H7V2001005",
        "quantity": 50,
        "desired_delivery": "2026-10-15",
        "sales_rep": "赤星 貢",
        "registered_date": "2026-06-05",
    })
    insert_spec_extract("ANK-2026-0002", "仕様書番号", "TAF-2026-015", "")
    insert_spec_extract("ANK-2026-0002", "静電容量", "300µF x 3相", "")
    insert_quotation_request({"mq_no": "MQ-2026-0002", "anken_id": "ANK-2026-0002", "request_date": "2026-06-06", "note": "初回見積依頼"})
    insert_quotation_response({"mr_no": "MR-2026-0002", "anken_id": "ANK-2026-0002", "amount": 12000000, "delivery": "2026-10-10", "response_date": "2026-06-20", "material_cost": 8000000, "note": "標準仕様"})

    # ANK-2026-0003: 日立（見積依頼中）
    insert_anken({
        "anken_id": "ANK-2026-0003",
        "anken_name": "PF盤向け高調波対策コンデンサ",
        "customer_name": "日立製作所",
        "product_name": "PF用コンデンサ",
        "spec_no": "HPF-2026-022",
        "drawing_no": "H7V3001012",
        "quantity": 200,
        "desired_delivery": "2026-11-30",
        "sales_rep": "朝田 卓麿",
        "registered_date": "2026-06-10",
    })
    insert_spec_extract("ANK-2026-0003", "仕様書番号", "HPF-2026-022", "")
    insert_quotation_request({"mq_no": "MQ-2026-0003", "anken_id": "ANK-2026-0003", "request_date": "2026-06-11", "note": "初回見積依頼"})

def next_anken_id():
    year = datetime.now().year
    prefix = f"ANK-{year}-"
    existing = [k for k in st.session_state.ankens if k.startswith(prefix)]
    nums = []
    for k in existing:
        try: nums.append(int(k.split("-")[-1]))
        except: pass
    mx = max(nums) if nums else 0
    return f"{prefix}{mx+1:04d}"

def insert_anken(d):
    st.session_state.ankens[d["anken_id"]] = dict(d)

def get_all_ankens():
    return sorted(st.session_state.ankens.values(), key=lambda x: x["anken_id"])

def get_anken(aid):
    return st.session_state.ankens.get(aid)

def insert_spec_extract(aid, item, value, note=""):
    st.session_state.spec_extracts.append({"anken_id": aid, "item": item, "value": value, "note": note})

def get_spec_extracts(aid):
    return [r for r in st.session_state.spec_extracts if r["anken_id"] == aid]

def insert_quotation_request(d):
    st.session_state.quotation_requests[d["anken_id"]] = dict(d)

def get_quotation_request_by_anken(aid):
    return st.session_state.quotation_requests.get(aid)

def get_all_quotation_requests():
    return list(st.session_state.quotation_requests.values())

def insert_quotation_response(d):
    st.session_state.quotation_responses[d["anken_id"]] = dict(d)

def get_quotation_response_by_anken(aid):
    return st.session_state.quotation_responses.get(aid)

def get_all_quotation_responses():
    return list(st.session_state.quotation_responses.values())

def insert_purchase_order(d):
    st.session_state.purchase_orders[d["anken_id"]] = dict(d)

def get_purchase_order_by_anken(aid):
    return st.session_state.purchase_orders.get(aid)

def get_all_purchase_orders():
    return list(st.session_state.purchase_orders.values())

def insert_manufacturing_order(d):
    st.session_state.manufacturing_orders[d["anken_id"]] = dict(d)

def get_manufacturing_order_by_anken(aid):
    return st.session_state.manufacturing_orders.get(aid)

def get_all_manufacturing_orders():
    return list(st.session_state.manufacturing_orders.values())

def get_dashboard_data():
    ankens = get_all_ankens()
    result = {"total": len(ankens), "spec_received": 0, "quotation_requested": 0,
              "ordered": 0, "mo_issued": 0, "ankens": []}
    for a in ankens:
        aid = a["anken_id"]
        spec = get_spec_extracts(aid)
        mq   = get_quotation_request_by_anken(aid)
        mr   = get_quotation_response_by_anken(aid)
        po   = get_purchase_order_by_anken(aid)
        mo   = get_manufacturing_order_by_anken(aid)
        s1 = "✅" if spec else "-"
        s2 = "✅" if mq   else "-"
        s3 = "✅" if (mr and mr.get("amount", 0) > 0) else "-"
        s4 = "✅" if (po and po.get("customer_po_no")) else "-"
        s5 = "✅" if (mo and mo.get("status") == "発効") else "-"
        if s1 == "✅": result["spec_received"]      += 1
        if s2 == "✅": result["quotation_requested"] += 1
        if s4 == "✅": result["ordered"]             += 1
        if s5 == "✅": result["mo_issued"]           += 1
        if   s5 == "✅": status = "🏭 製作指令発効済"
        elif s4 == "✅": status = "📦 受注済(指令待ち)"
        elif s3 == "✅": status = "💰 見積回答済(受注待ち)"
        elif s2 == "✅": status = "📝 見積依頼中"
        elif s1 == "✅": status = "📄 仕様受領"
        else:            status = "🆕 新規"
        result["ankens"].append({
            "案件ID": aid, "顧客名": a["customer_name"], "製品": a["product_name"],
            "①仕様": s1, "②見積依頼": s2, "③見積回答": s3,
            "④受注": s4, "⑤製作指令": s5, "総合状態": status,
        })
    return result
