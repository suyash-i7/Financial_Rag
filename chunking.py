from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


DATA_DIR = Path("data")


# --------------------------------------------------
# 1. Load PDF pages
# --------------------------------------------------

documents = []

for pdf_file in DATA_DIR.glob("*.pdf"):

    reader = PdfReader(pdf_file)

    for page_number, page in enumerate(reader.pages, start=1):   #  start=1 as by default in py start=0;

        text = page.extract_text() or ""

        if not text.strip():   #if not "" ->> true so it will continue if not text is extracted
            continue

        documents.append(
            {
                "text": text,
                "source": pdf_file.name,
                "page": page_number,
            }
        )


print(f"Pages with text: {len(documents)}")


# --------------------------------------------------
# 2. Create text splitter
# --------------------------------------------------

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
)


# --------------------------------------------------
# 3. Create chunks
# --------------------------------------------------

chunks = []

for document in documents:

    split_texts = splitter.split_text(document["text"])

    for chunk_number, chunk_text in enumerate(split_texts, start=1):

        chunks.append(
            {
                "text": chunk_text,
                "source": document["source"],
                "page": document["page"],
                "chunk": chunk_number,
            }
        )


# --------------------------------------------------
# 4. Inspect results
# --------------------------------------------------

print(f"Total chunks: {len(chunks)}")

print("\n" + "=" * 70)
print("FIRST 5 CHUNKS")
print("=" * 70)

for chunk in chunks[:5]:

    print("\n" + "-" * 70)

    print(f"Source : {chunk['source']}")
    print(f"Page   : {chunk['page']}")
    print(f"Chunk  : {chunk['chunk']}")
    print(f"Length : {len(chunk['text'])}")

    print("\nText:")
    print(chunk["text"])
