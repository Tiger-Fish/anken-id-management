"""
SQLite データベース管理モジュール
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = "anken.db"

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS ankens (
            anken_id TEXT PRIMARY KEY, anken_name TEXT, customer_name TEXT,
            product_name TEXT, spec_no TEXT, drawing_no TEXT, quantity INTEGER,
            desired_delivery TEXT, sales_rep TEXT, registered_date TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS spec_extracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, anken_id TEXT,
            item TEXT, value TEXT, note TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS quotation_requests (
            mq_no TEXT PRIMARY KEY, anken_id TEXT, request_date TEXT, note TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS quotation_responses (
            mr_no TEXT PRIMARY KEY, anken_id TEXT, amount INTEGER DEFAULT 0,
            delivery TEXT, response_date TEXT, material_cost INTEGER DEFAULT 0, note TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS purchase_orders (
            po_no TEXT PRIMARY KEY, anken_id TEXT, customer_po_no TEXT,
            quantity INTEGER DEFAULT 0, unit_price INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0, delivery TEXT, received_date TEXT, note TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS manufacturing_orders (
            mo_no TEXT PRIMARY KEY, anken_id TEXT, issued_date TEXT, status TEXT)""")

def insert_anken(d):
    with get_conn() as conn:
        conn.execute("""INSERT INTO ankens VALUES
            (:anken_id, :anken_name, :customer_name, :product_name, :spec_no,
             :drawing_no, :quantity, :desired_delivery, :sales_rep, :registered_date)""", d)

def get_all_ankens():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM ankens ORDER BY anken_id").fetchall()]

def get_anken(aid):
    with get_conn() as conn:
        r = conn.execute("SELECT * FROM ankens WHERE anken_id=?", (aid,)).fetchone()
        return dict(r) if r else None

def next_anken_id():
    with get_conn() as conn:
        year = datetime.now().year
        prefix = f"ANK-{year}-"
        rows = conn.execute("SELECT anken_id FROM ankens WHERE anken_id LIKE ?", (prefix+"%",)).fetchall()
        mx = 0
        for r in rows:
            try: mx = max(mx, int(r["anken_id"].split("-")[-1]))
            except: pass
        return f"{prefix}{mx+1:04d}"

def insert_spec_extract(aid, item, value, note=""):
    with get_conn() as conn:
        conn.execute("INSERT INTO spec_extracts (anken_id, item, value, note) VALUES (?,?,?,?)",
                     (aid, item, value, note))

def get_spec_extracts(aid):
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM spec_extracts WHERE anken_id=?", (aid,)).fetchall()]

def insert_quotation_request(d):
    with get_conn() as conn:
        conn.execute("INSERT OR REPLACE INTO quotation_requests VALUES (:mq_no,:anken_id,:request_date,:note)", d)

def get_quotation_request_by_anken(aid):
    with get_conn() as conn:
        r = conn.execute("SELECT * FROM quotation_requests WHERE anken_id=?", (aid,)).fetchone()
        return dict(r) if r else None

def get_all_quotation_requests():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM quotation_requests").fetchall()]

def insert_quotation_response(d):
    with get_conn() as conn:
        conn.execute("""INSERT OR REPLACE INTO quotation_responses VALUES
            (:mr_no,:anken_id,:amount,:delivery,:response_date,:material_cost,:note)""", d)

def get_quotation_response_by_anken(aid):
    with get_conn() as conn:
        r = conn.execute("SELECT * FROM quotation_responses WHERE anken_id=?", (aid,)).fetchone()
        return dict(r) if r else None

def get_all_quotation_responses():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM quotation_responses").fetchall()]

def insert_purchase_order(d):
    with get_conn() as conn:
        conn.execute("""INSERT OR REPLACE INTO purchase_orders VALUES
            (:po_no,:anken_id,:customer_po_no,:quantity,:unit_price,:total,:delivery,:received_date,:note)""", d)

def get_purchase_order_by_anken(aid):
    with get_conn() as conn:
        r = conn.execute("SELECT * FROM purchase_orders WHERE anken_id=?", (aid,)).fetchone()
        return dict(r) if r else None

def get_all_purchase_orders():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM purchase_orders").fetchall()]

def insert_manufacturing_order(d):
    with get_conn() as conn:
        conn.execute("INSERT OR REPLACE INTO manufacturing_orders VALUES (:mo_no,:anken_id,:issued_date,:status)", d)

def get_manufacturing_order_by_anken(aid):
    with get_conn() as conn:
        r = conn.execute("SELECT * FROM manufacturing_orders WHERE anken_id=?", (aid,)).fetchone()
        return dict(r) if r else None

def get_all_manufacturing_orders():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM manufacturing_orders").fetchall()]

def get_dashboard_data():
    ankens = get_all_ankens()
    result = {"total": len(ankens), "spec_received": 0, "quotation_requested": 0,
              "ordered": 0, "mo_issued": 0, "ankens": []}
    for a in ankens:
        aid = a["anken_id"]
        spec = get_spec_extracts(aid)
        mq = get_quotation_request_by_anken(aid)
        mr = get_quotation_response_by_anken(aid)
        po = get_purchase_order_by_anken(aid)
        mo = get_manufacturing_order_by_anken(aid)
        s1 = "OK" if spec else "-"
        s2 = "OK" if mq else "-"
        s3 = "OK" if (mr and mr.get("amount",0) > 0) else "-"
        s4 = "OK" if (po and po.get("customer_po_no")) else "-"
        s5 = "OK" if (mo and mo.get("status")=="発効") else "-"
        if s1=="OK": result["spec_received"] += 1
        if s2=="OK": result["quotation_requested"] += 1
        if s4=="OK": result["ordered"] += 1
        if s5=="OK": result["mo_issued"] += 1
        if s5=="OK": status = "製作指令発効済"
        elif s4=="OK": status = "受注済(指令待ち)"
        elif s3=="OK": status = "見積回答済(受注待ち)"
        elif s2=="OK": status = "見積依頼中"
        elif s1=="OK": status = "仕様受領"
        else: status = "新規"
        result["ankens"].append({
            "案件ID": aid, "顧客名": a["customer_name"], "製品": a["product_name"],
            "①仕様受領": s1, "②見積依頼": s2, "③見積回答": s3,
            "④受注": s4, "⑤製作指令": s5, "総合状態": status,
        })
    return result
