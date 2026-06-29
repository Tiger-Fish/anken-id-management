"""
サンプルデータ投入スクリプト
実行: python sample_data.py
"""
from db import (init_db, insert_anken, insert_spec_extract,
                insert_quotation_request, insert_quotation_response,
                insert_purchase_order, insert_manufacturing_order)

def main():
    init_db()
    print("サンプルデータを投入中...")

    # ANK-2026-0001: 三菱電機 (全プロセス完了)
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
        ("静電容量", "2000uF -5/+5% x 4回路", ""),
        ("定格電圧 UNDC", "1650V DC", ""),
        ("定格電流", "297Arms / 4000uF @70C", ""),
        ("量産用図面", "H7V1657001", ""),
        ("製品保証期間", "納入後 2年", ""),
        ("設計保証期間", "納入後 5年", ""),
        ("製品寿命", "20年 / 126,000時間 @平均45C", ""),
        ("燃焼性", "UL94 V-0 相当", ""),
        ("適用規格", "IEC61881-1, 60077-1, 61287-1, 61373, 62497-1", ""),
    ]:
        insert_spec_extract("ANK-2026-0001", item, val, note)

    insert_quotation_request({"mq_no": "MQ-2026-0001", "anken_id": "ANK-2026-0001",
                              "request_date": "2026-06-02", "note": "初回見積依頼"})
    insert_quotation_response({"mr_no": "MR-2026-0001", "anken_id": "ANK-2026-0001",
                               "amount": 48000000, "delivery": "2026-09-25",
                               "response_date": "2026-06-15", "material_cost": 32000000,
                               "note": "IEC61881-1準拠"})
    insert_purchase_order({"po_no": "PO-2026-0001", "anken_id": "ANK-2026-0001",
                           "customer_po_no": "MEL-PO-2026-3345", "quantity": 100,
                           "unit_price": 480000, "total": 48000000,
                           "delivery": "2026-09-30", "received_date": "2026-07-01",
                           "note": "EDI受領"})
    insert_manufacturing_order({"mo_no": "MO-2026-0001", "anken_id": "ANK-2026-0001",
                                "issued_date": "2026-07-02", "status": "発効"})

    # ANK-2026-0002: 東芝 (見積回答済、受注待ち)
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
    insert_spec_extract("ANK-2026-0002", "静電容量", "300uF x 3相", "")
    insert_quotation_request({"mq_no": "MQ-2026-0002", "anken_id": "ANK-2026-0002",
                              "request_date": "2026-06-06", "note": "初回見積依頼"})
    insert_quotation_response({"mr_no": "MR-2026-0002", "anken_id": "ANK-2026-0002",
                               "amount": 12000000, "delivery": "2026-10-10",
                               "response_date": "2026-06-20", "material_cost": 8000000,
                               "note": "標準仕様"})

    # ANK-2026-0003: 日立 (見積依頼中)
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
    insert_quotation_request({"mq_no": "MQ-2026-0003", "anken_id": "ANK-2026-0003",
                              "request_date": "2026-06-11", "note": "初回見積依頼"})

    print("サンプルデータ投入完了!")
    print("  - ANK-2026-0001: 三菱電機 (製作指令発効済)")
    print("  - ANK-2026-0002: 東芝 (見積回答済、受注待ち)")
    print("  - ANK-2026-0003: 日立 (見積依頼中)")

if __name__ == "__main__":
    main()
