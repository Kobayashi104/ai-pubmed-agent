from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np

from utils.openai_client import get_embedding  # ← 必要に応じて調整


def extract_keywords(texts, top_n=5):
    """クラスタ内の要約からTF-IDFで代表キーワードを抽出"""
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf = vectorizer.fit_transform(texts)
    mean_scores = tfidf.mean(axis=0).A1
    terms = vectorizer.get_feature_names_out()
    ranked = np.argsort(mean_scores)[::-1]
    return [terms[i] for i in ranked[:top_n]]


def plot_clusters(articles: list, perplexity: int = 30, n_clusters: int = 4):
    print("📌 [クラスタリング用の埋め込み生成] ...")
    texts = [art['summary'] for art in articles]
    titles = [art['title'] for art in articles]
    embeddings = [get_embedding(text) for text in texts]

    X = np.array(embeddings)
    X_scaled = StandardScaler().fit_transform(X)

    print("📉 [次元削減 (t-SNE)] ...")
    perplexity = min(perplexity, len(articles) - 1)
    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
    X_2d = tsne.fit_transform(X_scaled)

    print(f"🎯 [クラスタリング (KMeans, {n_clusters}クラスタ)] ...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X)

    # クラスタごとの代表キーワード抽出
    cluster_keywords = {}
    for i in range(n_clusters):
        cluster_texts = [texts[j] for j in range(len(texts)) if labels[j] == i]
        cluster_keywords[i] = extract_keywords(cluster_texts)

    # ======== プロット設定 ========
    plt.figure(figsize=(12, 10))

    # 日本語フォント設定（Windows向け）
    try:
        plt.rcParams['font.family'] = 'MS Gothic'
    except:
        print("⚠️ フォントの設定に失敗しました")

    palette = sns.color_palette("Set2", n_clusters)

    for i in range(n_clusters):
        idx = labels == i
        plt.scatter(X_2d[idx, 0], X_2d[idx, 1], c=[palette[i]], label=f"Cluster {i+1}: {', '.join(cluster_keywords[i])}", s=120, alpha=0.7)

    # 注釈（タイトルの一部＋番号）
    for i, title in enumerate(titles):
        short_title = title[:30] + "..." if len(title) > 30 else title
        plt.text(X_2d[i, 0], X_2d[i, 1], f"{i+1}", fontsize=9, ha='center', va='center', weight='bold')

    plt.title("📚 PubMed要約クラスタリング可視化 (t-SNE + KMeans)", fontsize=16)
    plt.xlabel("t-SNE Dimension 1")
    plt.ylabel("t-SNE Dimension 2")
    plt.legend(loc='best', fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
