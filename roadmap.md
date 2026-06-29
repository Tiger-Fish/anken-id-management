# ロードマップ / Roadmap

## Phase 0: 本プロトタイプ (現在)

Streamlit + SQLite による単体動作プロトタイプ。
社内デモ・概念検証用。

## Phase 1: SharePointリスト化

- SQLite → SharePointリスト/Dataverseに移行
- 複数人同時編集、履歴管理、権限管理を有効化
- Microsoft 365 SSOで認証

## Phase 2: Power Apps画面

- Streamlit UI → Power Apps Canvas Apps に置き換え
- モバイル対応
- Teamsアプリとして統合

## Phase 3: Azure AI Document Intelligence 統合

- PDF抽出を本格AIで高精度化
- 顧客仕様書テンプレートの学習
- 表組みや画像も抽出

## Phase 4: Power Automate で自動化

- 顧客メール受信 → 案件自動登録
- 見積回答書受領 → 営業に承認依頼
- 注文書受領 → 自動照合 → 製作指令発効
- 工場への製造指示自動送信

## Phase 5: Copilot Studio でナレッジ化

- 過去案件をRAG化
- 営業ナレッジエージェント
- ベテラン知見の若手継承

## Phase 6: 既存EDPシステム連携

- RPA で EDP に書き込み
- 品質記録・J-SOX監査ログ自動保管
- 基幹システムとの完全統合
