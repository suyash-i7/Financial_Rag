import requests
import chromadb

import re


def detect_quarter(question):

    match = re.search(
        r"\bQ([1-4])\s*FY(\d{2,4})\b",
        question,
        re.IGNORECASE
    )

    if not match:
        return None

    quarter = match.group(1)
    year = match.group(2)

    if len(year) == 2:
        year = "20" + year

    start_year = int(year)

    # Example:
    # FY26 → FY2025-26
    # FY27 → FY2026-27

    end_year = str(start_year)[-2:]
    start_year_full = start_year - 1

    return f"Q{quarter} FY{start_year_full}-{end_year}"
# ==================================================
# CONFIGURATION
# ==================================================

CHROMA_DIR = "chroma_db"

OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL = "embeddinggemma"

TOP_K = 4


# ==================================================
# 1. CONNECT TO CHROMADB
# ==================================================

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = client.get_collection(
    name="financial_reports"
)

print(f"Documents in database: {collection.count()}")


# ==================================================
# 2. USER QUESTION
# ==================================================

question = "What was Jio Platforms EBITDA in Q1 FY27?"

detected_quarter = detect_quarter(question)

print(f"Detected quarter: {detected_quarter}")

# ==================================================
# 3. EMBED THE QUESTION
# ==================================================

response = requests.post(
    OLLAMA_URL,
    json={
        "model": MODEL,
        "input": question,
    },
    timeout=300,
)

response.raise_for_status()

question_embedding = response.json()["embeddings"][0]

print(f"Question vector dimensions: {len(question_embedding)}")


# ==================================================
# 4. SEARCH CHROMADB
# ==================================================

if detected_quarter:

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=TOP_K,
        where={
            "quarter": detected_quarter
        },
    )

else:

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=TOP_K,
    )


# ==================================================
# 5. DISPLAY RETRIEVED CHUNKS
# ==================================================

print("\n" + "=" * 70)
print("RETRIEVED CHUNKS")
print("=" * 70)

documents = results["documents"][0]
metadatas = results["metadatas"][0]
distances = results["distances"][0]


for i, (document, metadata, distance) in enumerate(
    zip(documents, metadatas, distances),
    start=1
):

    print("\n" + "-" * 70)

    print(f"Rank     : {i}")
    print(f"Distance : {distance}")
    print(f"Source   : {metadata['source']}")
    print(f"Page     : {metadata['page']}")
    print(f"Chunk    : {metadata['chunk']}")

    print("\nText:")
    print(document)
