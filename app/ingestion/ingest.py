from app.ingestion.loader import extract_pages_from_pdf
from app.ingestion.chunker import split_text
from app.ingestion.embedder import Embedder
from app.ingestion.store import store_chunks


PDF_PATH = "data/documents/Parth's Resume (1).pdf"


def ingest_document():

    print("Loading PDF...")

    pages = extract_pages_from_pdf(PDF_PATH)

    print(f"Found {len(pages)} page(s).")

    all_chunks = []

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

        all_chunks.extend(chunks)

    print(f"Created {len(all_chunks)} chunks.")

    print("Generating embeddings...")

    embedder = Embedder()

    texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    embeddings = embedder.generate_embeddings(texts)

    for chunk, embedding in zip(all_chunks, embeddings):

        chunk["embedding"] = embedding.tolist()

    print("Embeddings generated.")

    print("Storing chunks in PostgreSQL...")

    store_chunks(all_chunks)

    print("Ingestion complete!")


if __name__ == "__main__":
    ingest_document()