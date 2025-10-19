import os
import time
import uuid
import json
import pandas as pd
import requests
from qdrant_client import QdrantClient, models
from prep import fetch_documents, fetch_ground_truth


# ==============================
# Configuration
# ==============================
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
MODEL_HANDLE = os.getenv("MODEL_HANDLE")


# ==============================
# Initialize Qdrant Client
# ==============================
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    timeout=120.0,
    check_compatibility=False
)
print(f"✅ Connected to Qdrant at {QDRANT_URL}")


# ==============================
# Collection Initialization
# ==============================
def init_collection(collection_name: str):
    """Create a Qdrant collection if it doesn’t exist."""
    if qdrant_client.collection_exists(collection_name):
        print(f"🗑 Deleting existing collection: {collection_name}")
        qdrant_client.delete_collection(collection_name)
        time.sleep(3)

    try:
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config={
                'jina-small': models.VectorParams(size=512, distance=models.Distance.COSINE),
            },
            sparse_vectors_config={
                "bm25": models.SparseVectorParams(modifier=models.Modifier.IDF)
            },
        )
        print(f"Created new collection: {collection_name}")
    except Exception as e:
        print("Error creating collection:", e)


# ==============================
# Indexing Function
# ==============================
def index_documents(documents: list, collection_name: str):
    """Insert or update documents into Qdrant."""
    if not documents:
        print("No documents to index.")
        return

    print(f"📥 Indexing {len(documents)} documents...")

    points = [
        models.PointStruct(
            id=uuid.uuid4().hex,
            vector={
                "jina-small": models.Document(
                    text=doc["text"],
                    model=MODEL_HANDLE,
                ),
                "bm25": models.Document(
                    text=doc["text"],
                    model="Qdrant/bm25",
                ),
            },
            payload={
                "id": doc.get("id"),
                "text": doc.get("text"),
                "city": doc.get("city"),
                "section": doc.get("section"),
                "subsection": doc.get("subsection"),
            }
        )
        for doc in documents
    ]

    qdrant_client.upsert(collection_name=collection_name, points=points)
    print(f"Successfully indexed {len(points)} points.")


# ==============================
# Main Workflow
# ==============================
def main(reindex: bool = True):
    print("Starting Qdrant indexing process...")

    # Step 1: Fetch data
    documents = fetch_documents()
    ground_truth = fetch_ground_truth()

    # Step 2: Initialize or reuse collection
    if reindex:
        init_collection(QDRANT_COLLECTION_NAME)
        index_documents(documents, QDRANT_COLLECTION_NAME)
    else:
        print("Skipping re-indexing (using existing collection).")

    print("Indexing process completed successfully!")


if __name__ == "__main__":
    main(reindex=True)
