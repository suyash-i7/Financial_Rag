from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


DATA_DIR = Path("data")


# --------------------------------------------------
# Load all pages
# --------------------------------------------------

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


# --------------------------------------------------
# Function to create chunks
# --------------------------------------------------

def create_chunks(chunk_size, chunk_overlap):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = []

    for document in documents:

        split_texts = splitter.split_text(document["text"])

        for chunk_number, chunk_text in enumerate(
            split_texts, start=1
        ):

            chunks.append({
                "text": chunk_text,
                "source": document["source"],
                "page": document["page"],
                "chunk": chunk_number,
            })

    return chunks


# --------------------------------------------------
# Experiment 1: 800
# --------------------------------------------------

chunks_800 = create_chunks(
    chunk_size=800,
    chunk_overlap=150,
)

print("\n" + "=" * 70)
print("800 CHARACTER EXPERIMENT")
print("=" * 70)

print(f"Total chunks: {len(chunks_800)}")


# --------------------------------------------------
# Experiment 2: 1200
# --------------------------------------------------

chunks_1200 = create_chunks(
    chunk_size=1200,
    chunk_overlap=150,
)

print("\n" + "=" * 70)
print("1200 CHARACTER EXPERIMENT")
print("=" * 70)

print(f"Total chunks: {len(chunks_1200)}")


# --------------------------------------------------
# Inspect random-ish samples
# --------------------------------------------------

print("\n" + "=" * 70)
print("SAMPLE FROM 800")
print("=" * 70)

for chunk in chunks_800[10:13]:

    print("\n" + "-" * 70)
    print(f"Source : {chunk['source']}")
    print(f"Page   : {chunk['page']}")
    print(f"Length : {len(chunk['text'])}")
    print("\n" + chunk["text"])


print("\n" + "=" * 70)
print("SAMPLE FROM 1200")
print("=" * 70)

for chunk in chunks_1200[10:13]:

    print("\n" + "-" * 70)
    print(f"Source : {chunk['source']}")
    print(f"Page   : {chunk['page']}")
    print(f"Length : {len(chunk['text'])}")
    print("\n" + chunk["text"])