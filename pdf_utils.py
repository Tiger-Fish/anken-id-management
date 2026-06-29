"""
PDFテキスト抽出と項目自動抽出
"""
import re

def extract_text_from_pdf(file_like):
    try:
        import pdfplumber
    except ImportError:
        return "[エラー] pdfplumber がインストールされていません。"
    text_all = []
    try:
        with pdfplumber.open(file_like) as pdf:
            for page in pdf.pages:
                text_all.append(page.extract_text() or "")
    except Exception as e:
        return f"[エラー] PDF読込失敗: {e}"
    return "\n".join(text_all)

def extract_items_heuristic(text):
    items = {}
    m = re.search(r"(IKO[-–][A-Z0-9]+[-–]?[A-Z]?)", text)
    if m: items["仕様書番号"] = m.group(1)
    m = re.search(r"(\d+[\.,]?\d*)\s*[µu]F", text)
    if m: items["静電容量"] = f"{m.group(1)}µF"
    m = re.search(r"U[Nn]?DC[^0-9]*?(\d+)\s*V", text)
    if m: items["定格電圧 UNDC"] = f"{m.group(1)}V"
    m = re.search(r"(H[0-9A-Z]{8,10})", text)
    if m: items["図面番号"] = m.group(1)
    if re.search(r"126[,.]?000\s*時間", text):
        items["製品寿命"] = "20年 / 126,000時間"
    if "UL94" in text: items["燃焼性"] = "UL94 V-0相当"
    m = re.search(r"製品保証[^\n]*?(\d+)\s*年", text)
    if m: items["製品保証期間"] = f"納入後{m.group(1)}年"
    m = re.search(r"設計保証[^\n]*?(\d+)\s*年", text)
    if m: items["設計保証期間"] = f"納入後{m.group(1)}年"
    iec_list = re.findall(r"IEC\s*\d{4,5}(?:[-–]\d+)?", text)
    if iec_list:
        items["適用規格"] = ", ".join(sorted(set(iec_list)))
    for c in ["三菱電機","東芝","日立","川崎重工","富士電機","明電舎","JR","東洋電機"]:
        if c in text:
            items["顧客(推定)"] = c
            break
    return items
