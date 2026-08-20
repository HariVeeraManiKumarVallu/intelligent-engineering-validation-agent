from __future__ import annotations
from pathlib import Path
from typing import Dict, List
from langchain_core.tools import tool
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1] / "knowledge" / "documents"

def _load_docs():
    docs = []
    for path in sorted(ROOT.glob("*.txt")):
        docs.append((path.name, path.read_text(encoding="utf-8")))
    return docs

@tool
def retrieve_technical_knowledge(query: str) -> Dict[str, object]:
    """Retrieve the most relevant prototype engineering knowledge."""
    docs = _load_docs()
    if not docs:
        return {"status": "FAIL", "error": "No knowledge documents found.", "results": []}
    corpus = [text for _, text in docs]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(corpus + [query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    ranked = sorted(zip(scores, docs), reverse=True, key=lambda x: x[0])[:2]
    results: List[Dict[str, object]] = [
        {"document": name, "score": float(score), "content": content}
        for score, (name, content) in ranked
    ]
    return {"status": "PASS", "results": results}
