from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests


# ==================================================
# CONFIGURATION
# ==================================================

DATA_DIR = Path("data")

OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL = "embeddinggemma"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150

BATCH_SIZE = 32


# ==================================================
# 1. LOAD AND CHUNK DOCUMENTS
# ==================================================

documents = []

for pdf_file in DATA_DIR.glob("*.pdf"):

    reader = PdfReader(pdf_file)

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        if not text.strip():
            continue

        documents.append({
            "text": text,
            "source": pdf_file.name,
            "page": page_number,
        })


print(f"Pages with text: {len(documents)}")


# ==================================================
# 2. CREATE CHUNKS
# ==================================================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)


chunks = []

for document in documents:

    split_texts = splitter.split_text(document["text"])

    for chunk_number, chunk_text in enumerate(
        split_texts,
        start=1
    ):

        chunks.append({
            "text": chunk_text,
            "source": document["source"],
            "page": document["page"],
            "chunk": chunk_number,
        })


print(f"Total chunks: {len(chunks)}")


# ==================================================
# 3. PREPARE TEXT FOR EMBEDDING
# ==================================================

texts_to_embed = []

for chunk in chunks:

    text = f"""
SOURCE: {chunk["source"]}
PAGE: {chunk["page"]}

{chunk["text"]}
""".strip()

    texts_to_embed.append(text)


# ==================================================
# 4. EMBEDDING FUNCTION
# ==================================================

def embed_batch(texts):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "input": texts,
        },
        timeout=300,
    )

    response.raise_for_status()

    return response.json()["embeddings"]


# ==================================================
# 5. BATCH EMBEDDING
# ==================================================

all_embeddings = []

total = len(texts_to_embed)

for start in range(0, total, BATCH_SIZE):

    end = min(start + BATCH_SIZE, total)

    batch = texts_to_embed[start:end]

    print(
        f"Embedding chunks {start + 1}-{end} "
        f"of {total}..."
    )

    embeddings = embed_batch(batch)

    all_embeddings.extend(embeddings)


# ==================================================
# 6. VALIDATE
# ==================================================

print("\n" + "=" * 60)
print("EMBEDDING COMPLETE")
print("=" * 60)

print(f"Total chunks: {len(chunks)}")
print(f"Total embeddings: {len(all_embeddings)}")

if all_embeddings:

    print(
        f"Vector dimensions: "
        f"{len(all_embeddings[0])}"
    )

    print(
        f"First 5 values: "
        f"{all_embeddings[0][:5]}"
    )

    print(
        f"\nChunk 1 source: "
        f"{chunks[0]['source']}"
    )

    print(
        f"Chunk 1 page: "
        f"{chunks[0]['page']}"
    )
    