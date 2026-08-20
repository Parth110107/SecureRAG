import pymupdf
def extract_pages_from_pdf(file_path):
    document = pymupdf.open(file_path)
    pages = []
    for page_number, page in enumerate(document):

        text = page.get_text()

        pages.append({
            "page_number": page_number + 1,
            "text": text
        })

    document.close()
    return pages
if __name__ == "__main__":
    pages = extract_pages_from_pdf(
        "data/documents/Parth's Resume (1).pdf"
    )

    for page in pages:

        print("\n====================")
        print("PAGE:", page["page_number"])
        print("====================")

        print(page["text"])