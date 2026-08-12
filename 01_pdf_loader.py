from pathlib import Path
from pypdf import PdfReader


DATA_DIR = Path("data")

pdf_files = list(DATA_DIR.glob("*.pdf"))

for pdf_file in pdf_files:

    print("\n" + "=" * 70)
    print(f"FILE: {pdf_file.name}")
    print("=" * 70)

    reader = PdfReader(pdf_file)

    print(f"Total pages: {len(reader.pages)}")

    total=0
    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()
        total=total+len(text)

        print(
            f"Page {page_number:02d} "
            f"| extracted characters: {len(text or '')}"
        )
    print(f"total text: {total}")