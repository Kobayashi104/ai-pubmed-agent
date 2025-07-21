# ✅ utils/openai_client.py（修正後）
import os
from openai import OpenAI

def load_api_key():
    return os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=load_api_key())

def chat_with_gpt(messages, model="gpt-4o-mini", temperature=0.7):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content

def get_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    """
    テキストから埋め込みベクトル（リスト）を取得
    """
    response = client.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding