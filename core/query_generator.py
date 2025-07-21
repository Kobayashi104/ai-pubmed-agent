# core/query_generator.py

from utils.openai_client import chat_with_gpt

def clarify_user_intent(user_input: str) -> str:
    """
    ユーザーの自然文から、検索意図を明確な日本語で要約
    """
    system_prompt = "あなたは優秀なリサーチアシスタントです。以下のユーザー入力から、検索したい内容の意図を簡潔に日本語で明確化してください。"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    response = chat_with_gpt(messages)
    return response.strip()

def generate_pubmed_query(refined_intent: str) -> str:
    """
    明確化された意図（日本語）を英語のPubMed検索クエリに変換
    """
    system_prompt = "あなたはPubMedの検索に精通した医学研究者です。以下の日本語の検索意図をもとに、PubMedで適切な論文を検索するための英語クエリを作成してください。短く端的にしてください。"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": refined_intent}
    ]
    response = chat_with_gpt(messages)
    return response.strip()

def get_pubmed_query_from_user_input(user_input: str) -> str:
    """
    ユーザー入力から最終的なPubMedクエリを取得するメイン関数
    """
    refined = clarify_user_intent(user_input)
    query = generate_pubmed_query(refined)
    return query
