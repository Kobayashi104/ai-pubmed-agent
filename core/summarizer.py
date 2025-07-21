# core/summarizer.py

from utils.openai_client import chat_with_gpt

def summarize_abstract(abstract: str, language: str = "ja") -> str:
    """
    GPTを使って論文のabstractを要約。language: 'ja'（日本語） or 'en'（英語）
    """
    prompt_lang = "日本語で" if language == "ja" else "in English"
    messages = [
        {"role": "system", "content": f"You are a helpful assistant that summarizes academic abstracts {prompt_lang}."},
        {"role": "user", "content": f"Please summarize the following abstract {prompt_lang}:\n\n{abstract}"}
    ]

    summary = chat_with_gpt(messages)
    return summary


def summarize_articles(articles: list, language: str = "ja") -> list:
    """
    複数の論文に対して、abstractの要約を行う
    """
    for article in articles:
        abstract = article.get("abstract", "")
        if abstract and abstract != "No Abstract":
            article["summary"] = summarize_abstract(abstract, language)
        else:
            article["summary"] = "要約できる要旨がありません。"

    return articles
