# core/relevance_filter.py

from utils.openai_client import load_api_key
from openai import OpenAI
import os

client = OpenAI(api_key=load_api_key())


def get_relevance_score(article: dict, user_intent: str) -> float:
    """
    GPTで関連性スコア（0〜100点）を出す。
    """
    title = article.get("title", "")
    summary = article.get("summary", "")

    messages = [
        {"role": "system", "content": "You are a helpful assistant that evaluates the relevance of academic articles."},
        {"role": "user", "content": f"""Evaluate how relevant the following article is to the user's intent.
Respond only with a score between 0 and 100.

User intent:
{user_intent}

Article title:
{title}

Article summary:
{summary}

Relevance score (0 to 100):
"""}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
    )

    try:
        score_str = response.choices[0].message.content.strip()
        score = float(score_str)
        if 0 <= score <= 100:
            return score
    except:
        pass
    return 0.0


def filter_relevant_articles(articles: list, user_intent: str, threshold: float = 50.0) -> list:
    """
    指定スコア以上の論文だけを残す
    """
    filtered = []
    for article in articles:
        score = get_relevance_score(article, user_intent)
        print(f"[{score:.1f}] {article.get('title', '')[:80]}")
        if score >= threshold:
            article["relevance_score"] = score
            filtered.append(article)
    return filtered
