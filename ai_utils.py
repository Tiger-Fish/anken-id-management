"""
Azure OpenAI 連携 (オプション)
"""
import os, json

def has_azure_openai():
    return bool(os.getenv("AZURE_OPENAI_ENDPOINT")) and bool(os.getenv("AZURE_OPENAI_KEY"))

def extract_items_with_llm(text):
    if not has_azure_openai():
        return {}
    try:
        from openai import AzureOpenAI
    except ImportError:
        return {}
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION","2024-06-01"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT","gpt-4o-mini")
    prompt = """あなたは購買仕様書を読み取り構造化するAIです。以下の項目をJSONで抽出してください。
- 仕様書番号, 顧客名, 製品名, 静電容量, 定格電圧, 図面番号, 数量, 希望納期
- 製品保証期間, 設計保証期間, 製品寿命, 適用規格

仕様書テキスト:
""" + text[:6000]
    try:
        res = client.chat.completions.create(
            model=deployment,
            messages=[{"role":"system","content":"JSONのみ返してください。"},
                      {"role":"user","content":prompt}],
            response_format={"type":"json_object"},
            temperature=0.0,
        )
        return json.loads(res.choices[0].message.content)
    except Exception as e:
        print(f"[AI抽出エラー] {e}")
        return {}
