import json
import minsearch
from prep import fetch_documents  # fetch documents from prep.py


def build_minsearch_index():
    """Build MinSearch index once and cache it."""
    documents = fetch_documents()  # load documents once
    index = minsearch.Index(
        text_fields=['section', 'text'],
        keyword_fields=['id', 'city']
    )
    index.fit(documents)
    print(f"MinSearch index built with {len(documents)} documents.")
    return index

# Create a global cached index
minsearch_index = build_minsearch_index()
