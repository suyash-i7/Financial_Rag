from pathlib import Path
import pdfplumber


pdf_file = Path("data/september_2025_20251013032958_1768817579.pdf")


with pdfplumber.open(pdf_file) as pdf:

    print(f"Total pages: {len(pdf.pages)}")

    for page_number, page in enumerate(pdf.pages, start=1):

        text = page.extract_text() or ""

        print(
            f"Page {page_number:02d} "
            f"| extracted characters: {len(text)}"
        )

        if text:
            print(text[:300])
            print("-" * 70)