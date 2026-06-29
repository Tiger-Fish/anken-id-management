# システム構成 / Architecture

## 概要

本アプリは、顧客要求仕様書から製作指令書までを案件ID起点で管理するStreamlitアプリです。

## 案件IDフロー

```
顧客要求仕様書(PDF)
    ↓ アップロード
案件マスタ登録 (ANK-YYYY-NNNN)
    ↓
見積依頼書 (MQ-YYYY-NNNN)
    ↓
見積回答書 (MR-YYYY-NNNN)
    ↓
注文書受領 (PO-YYYY-NNNN)
    ↓
製作指令書 (MO-YYYY-NNNN) ← 見積回答書+注文書がそろうと発効
    ↓
工場へ製造指示送信
```

## データベーステーブル

| テーブル名 | 主な役割 |
|---|---|
| ankens | 案件マスタ |
| spec_extracts | 仕様書から抽出した項目 |
| quotation_requests | 見積依頼書 |
| quotation_responses | 見積回答書 |
| purchase_orders | 注文書 |
| manufacturing_orders | 製作指令書 |

## 技術スタック

| レイヤ | 採用技術 |
|---|---|
| UI | Streamlit |
| アプリロジック | Python 3.10+ |
| データベース | SQLite |
| PDF解析 | pdfplumber |
| AI抽出(オプション) | Azure OpenAI |

## 製作指令書 発効ロジック

```python
mr_ok = mr and mr.get("amount", 0) > 0      # 見積金額あり
po_ok = po and po.get("customer_po_no")     # 注文書あり
can_issue = bool(mr_ok and po_ok)           # 両方あれば発効可
```
