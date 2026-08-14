from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests


DATA_DIR = Path("data")

OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL = "embeddinggemma"


# --------------------------------------------------
# 1. Find the first PDF
# --------------------------------------------------

pdf_files = list(DATA_DIR.glob("*.pdf"))

if not pdf_files:
    raise FileNotFoundError("No PDF files found in data/")


pdf_file = pdf_files[0]

print(f"Using PDF: {pdf_file.name}")


# --------------------------------------------------
# 2. Extract first page containing text
# --------------------------------------------------

reader = PdfReader(pdf_file)

page_text = None
page_number = None

for number, page in enumerate(reader.pages, start=1):

    text = page.extract_text() or ""

    if text.strip():
        page_text = text
        page_number = number
        break


if page_text is None:
    raise ValueError("No extractable text found.")


print(f"Using page: {page_number}")


# --------------------------------------------------
# 3. Create one 1200-character chunk
# --------------------------------------------------

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=150,
)

chunks = splitter.split_text(page_text)

chunk = chunks[0]


# --------------------------------------------------
# 4. Add source information
# --------------------------------------------------

text_to_embed = f"""
SOURCE: {pdf_file.name}
PAGE: {page_number}

{chunk}
"""


# --------------------------------------------------
# 5. Send to Ollama
# --------------------------------------------------

response = requests.post(
    OLLAMA_URL,
    json={
        "model": MODEL,
        "input": text_to_embed,
    },
)

response.raise_for_status()

data = response.json()

embedding = data["embeddings"][0]


# --------------------------------------------------
# 6. Inspect result
# --------------------------------------------------

print("\nEmbedding created successfully.")

print(f"Vector dimensions: {len(embedding)}")

print(f"First 5 values: {embedding[:5]}")

print("\nText that was embedded:")
print(text_to_embed[:1000])