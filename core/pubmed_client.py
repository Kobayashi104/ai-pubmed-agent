# core/pubmed_client.py

import requests
import xml.etree.ElementTree as ET

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def search_pubmed(query: str, max_results: int = 10) -> list:
    """
    PubMedでクエリ検索を行い、PMIDリストを取得
    """
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "xml"
    }
    response = requests.get(BASE_URL + "esearch.fcgi", params=params)
    response.raise_for_status()
    
    root = ET.fromstring(response.text)
    ids = [id_elem.text for id_elem in root.findall(".//Id")]
    return ids

def fetch_details(pmids: list) -> list:
    """
    PMIDのリストから、各論文のタイトル・要旨などの詳細情報を取得
    """
    ids_str = ",".join(pmids)
    params = {
        "db": "pubmed",
        "id": ids_str,
        "retmode": "xml"
    }
    response = requests.get(BASE_URL + "efetch.fcgi", params=params)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    articles = []
    for article in root.findall(".//PubmedArticle"):
        title_elem = article.find(".//ArticleTitle")
        abstract_elem = article.find(".//Abstract/AbstractText")
        pmid_elem = article.find(".//PMID")
        journal_elem = article.find(".//Journal/Title")
        pubdate_elem = article.find(".//PubDate/Year")
        author_list = article.findall(".//AuthorList/Author")
        
        first_author = "Unknown"
        if author_list:
            last_name = author_list[0].findtext("LastName", "")
            initials = author_list[0].findtext("Initials", "")
            first_author = f"{last_name} {initials}".strip()

        pub_year = pubdate_elem.text if pubdate_elem is not None else "N/A"
        journal = journal_elem.text if journal_elem is not None else "N/A"
        pmid = pmid_elem.text if pmid_elem is not None else "N/A"

        articles.append({
            "pmid": pmid,
            "title": title_elem.text if title_elem is not None else "No Title",
            "abstract": abstract_elem.text if abstract_elem is not None else "No Abstract",
            "author": first_author,
            "year": pub_year,
            "journal": journal,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        })

    return articles
