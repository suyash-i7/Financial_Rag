import re
from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests
import chromadb


def extract_quarter(filename):

    match = re.search(
        r"(Q[1-4]_FY\d{4}-\d{2})",
        filename
    )

    if match:
        return match.group(1).replace("_", " ")

    return "UNKNOWN"

# ==================================================
# CONFIGURATION
# ==================================================

DATA_DIR = Path("data")

CHROMA_DIR = "chroma_db"

OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL = "embeddinggemma"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150

BATCH_SIZE = 32


# ==================================================
# 1. LOAD PDF PAGES
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
            "quarter": extract_quarter(pdf_file.name),
        })


print(f"Pages with text: {len(documents)}")


# ==================================================
# 2. CHUNK DOCUMENTS
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
            "quarter": document["quarter"],
        })


print(f"Total chunks: {len(chunks)}")


# ==================================================
# 3. PREPARE TEXT FOR EMBEDDING
# ==================================================

texts_to_embed = []

for chunk in chunks:

    text = (
        f"SOURCE: {chunk['source']}\n"
        f"PAGE: {chunk['page']}\n\n"
        f"{chunk['text']}"
    )

    texts_to_embed.append(text)


# ==================================================
# 4. OLLAMA EMBEDDING FUNCTION
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
# 5. CREATE CHROMADB CLIENT
# ==================================================

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)


# ==================================================
# 6. CREATE COLLECTION
# ==================================================

collection = client.get_or_create_collection(
    name="financial_reports"
)


print("\nChromaDB collection ready.")


# ==================================================
# 7. EMBED + STORE IN BATCHES
# ==================================================

total = len(texts_to_embed)

for start in range(0, total, BATCH_SIZE):

    end = min(start + BATCH_SIZE, total)

    batch_texts = texts_to_embed[start:end]

    print(
        f"Processing chunks {start + 1}-{end} "
        f"of {total}..."
    )

    embeddings = embed_batch(batch_texts)


    ids = [
        f"chunk_{i}"
        for i in range(start, end)
    ]


    metadatas = [
        {
            "source": chunks[i]["source"],
            "page": chunks[i]["page"],
            "chunk": chunks[i]["chunk"],
            "quarter": chunks[i]["quarter"],
        }
        for i in range(start, end)
    ]


    collection.add(
        ids=ids,
        documents=batch_texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )


# ==================================================
# 8. VERIFY
# ==================================================

print("\n" + "=" * 60)
print("CHROMADB INDEXING COMPLETE")
print("=" * 60)

print(
    f"Documents stored: "
    f"{collection.count()}"
)

print(
    f"Database location: "
    f"{CHROMA_DIR}"
)