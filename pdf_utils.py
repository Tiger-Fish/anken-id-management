"""
PDF抽出 + モックデモデータ対応
"""
import re

DEMO_EXTRACTED = {
    "仕様書番号": "IKO-B82034-C",
    "顧客(推定)": "富士電機株式会社",
    "製品名": "乾式DCフィルタコンデンサ",
    "静電容量": "1500µF",
    "定格電圧 UNDC": "1200V",
    "図面番号": "H7V9900123",
    "数量": "60",
    "希望納期": "2026-12-28",
    "製品保証期間": "納入後2年",
    "設計保証期間": "納入後5年",
    "製品寿命": "20年 / 126,000時間",
    "適用規格": "IEC61881-1, IEC60077-1",
}

def extract_text_from_pdf(file_like):
    try:
        import pdfplumber
        text_all = []
        with pdfplumber.open(file_like) as pdf:
            for page in pdf.pages:
                text_all.append(page.extract_text() or "")
        return "\n".join(text_all)
    except Exception:
        return ""

def extract_items_heuristic(text):
    if not text.strip():
        return {}
    items = {}
    m = re.search(r"(IKO[-–][A-Z0-9]+[-–]?[A-Z]?)", text)
    if m: items["仕様書番号"] = m.group(1)
    m = re.search(r"(\d+[\.,]?\d*)\s*[µu]F", text)
    if m: items["静電容量"] = f"{m.group(1)}µF"
    m = re.search(r"U[Nn]?DC[^0-9]*?(\d+)\s*V", text)
    if m: items["定格電圧 UNDC"] = f"{m.group(1)}V"
    m = re.search(r"(H[0-9A-Z]{8,10})", text)
    if m: items["図面番号"] = m.group(1)
    for c in ["三菱電機","東芝","日立","川崎重工","富士電機","明電舎","JR","東洋電機"]:
        if c in text:
            items["顧客(推定)"] = c
            break
    return items

def extract_items_demo(filename=""):
    """デモ用：ファイル名に応じてモックデータを返す"""
    result = dict(DEMO_EXTRACTED)
    if "富士" in filename:
        result["顧客(推定)"] = "富士電機株式会社"
    elif "川崎" in filename:
        result["顧客(推定)"] = "川崎重工業株式会社"
    return result
