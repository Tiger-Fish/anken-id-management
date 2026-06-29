# 案件ID管理アプリ - 指月電機 営業DXプロトタイプ

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

顧客要求仕様書から製作指令書まで、**案件ID**を起点に一気通貫管理するStreamlit Webアプリです。

## セットアップ

```bash
git clone https://github.com/<your-username>/anken-id-management.git
cd anken-id-management
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
python sample_data.py
streamlit run app.py
```

ブラウザで http://localhost:8501 が開きます。

## ライセンス
[MIT License](LICENSE)

## 著者
**和田 孝雄** - 指月電機製作所 営業本部
