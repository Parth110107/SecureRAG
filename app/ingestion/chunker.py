from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(
    text,
    document_id,
    owner,
    allowed_roles,
    classification="private",
    chunk_size=500,
    chunk_overlap=100
):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = splitter.split_text(text)

    chunk_data = []

    for index, chunk in enumerate(chunks):

        chunk_data.append({
            "chunk_id": f"{document_id}_chunk_{index}",
            "document_id": document_id,
            "text": chunk,
            "owner": owner,
            "allowed_roles": allowed_roles,
            "classification": classification
        })

    return chunk_data
if __name__ == "__main__":

    from app.ingestion.loader import extract_pages_from_pdf

    pages = extract_pages_from_pdf(
        "data/documents/Parth's Resume (1).pdf"
    )

    for page in pages:

        chunks = split_text(
            text=page["text"],
            document_id="Parth's Resume (1)",
            owner="parth",
            allowed_roles=["owner"],
            classification="private"
        )

        for chunk in chunks:

            chunk["page_number"] = page["page_number"]

            print("\n--------------------")
            print(chunk)