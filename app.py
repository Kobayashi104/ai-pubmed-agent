# app.py

import streamlit as st
import pandas as pd
from datetime import datetime

from core.query_generator import get_pubmed_query_from_user_input
from core.pubmed_client import search_pubmed, fetch_details
from core.summarizer import summarize_articles
from core.relevance_filter import filter_relevant_articles

st.set_page_config(page_title="PubMed Research Assistant", page_icon="🔬")
st.title("🔬 PubMed Research Assistant")
st.markdown("AIによってPubMedから関連論文を検索・要約・絞り込みます。")

# 入力フォーム
user_input = st.text_area("🎯 あなたの調査目的・関心のあるテーマを入力してください", height=100)
max_results = st.slider("📚 最大取得論文数", min_value=5, max_value=30, value=10)
threshold = st.slider("📈 関連性スコアの閾値（フィルタリング）", min_value=0, max_value=100, value=50)

# 検索ボタン
if st.button("🚀 検索を実行"):
    if not user_input.strip():
        st.warning("入力が空です。調査テーマを入力してください。")
        st.stop()

    with st.spinner("🧠 検索クエリを生成中..."):
        query = get_pubmed_query_from_user_input(user_input)
        st.success(f"生成された検索クエリ: `{query}`")

    with st.spinner("🔎 PubMedから論文を取得中..."):
        pmids = search_pubmed(query, max_results=max_results)
        if not pmids:
            st.error("論文が見つかりませんでした。")
            st.stop()
        articles = fetch_details(pmids)

    with st.spinner("✍️ 要約を生成中..."):
        summaries = summarize_articles(articles)

    with st.spinner("🧮 関連性スコアを評価中..."):
        filtered = filter_relevant_articles(summaries, user_input, threshold=threshold)

    # セッション状態に保存（チェック管理用）
    st.session_state.filtered_articles = filtered
    st.session_state.selected_articles = [False] * len(filtered)

# 結果表示
if 'filtered_articles' in st.session_state:
    filtered = st.session_state.filtered_articles
    if not filtered:
        st.info("関連する論文は見つかりませんでした。")
    else:
        st.subheader("✅ 関連性の高い論文")

        # 全選択ボタン
        if st.button("✅ すべてを選択"):
            st.session_state.selected_articles = [True] * len(filtered)

        selected_articles = []
        for i, art in enumerate(sorted(filtered, key=lambda x: x['relevance_score'], reverse=True)):
            is_checked = st.checkbox(
                f"{i+1}. {art['title']} ([Link]({art['url']}))",
                key=f"check_{i}",
                value=st.session_state.selected_articles[i]
            )
            st.session_state.selected_articles[i] = is_checked

            st.write(f"**Score:** {art['relevance_score']:.1f}")
            st.write(f"**Author:** {art['author']} | **Year:** {art['year']} | **Journal:** {art['journal']}")
            with st.expander("🔍 要約を表示"):
                st.write(art['summary'])
            st.markdown("---")

            if is_checked:
                selected_articles.append({
                    "Title": art["title"],
                    "Author": art["author"],
                    "Year": art["year"],
                    "Journal": art["journal"],
                    "Score": art["relevance_score"],
                    "Summary": art["summary"],
                    "URL": art["url"]
                })

        # Excel ダウンロードボタン
        if selected_articles:
            df = pd.DataFrame(selected_articles)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            file_name = f"pubmed_results_{timestamp}.xlsx"

            with pd.ExcelWriter(file_name, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Results")

            with open(file_name, "rb") as f:
                st.download_button(
                    label="⬇️ 選択した論文をExcelでダウンロード",
                    data=f,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("✅ 論文を選択してください（チェックボックス）。")
