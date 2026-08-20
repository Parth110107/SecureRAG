from app.ingestion.loader import extract_pages_from_pdf
from app.ingestion.chunker import split_text
from app.ingestion.embedder import Embedder


PDF_PATH = "data/documents/Parth's Resume (1).pdf"


def create_embedded_chunks():

    pages = extract_pages_from_pdf(PDF_PATH)

    embedder = Embedder()

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

    texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    embeddings = embedder.generate_embeddings(texts)

    for chunk, embedding in zip(all_chunks, embeddings):

        chunk["embedding"] = embedding.tolist()

    return all_chunks


if __name__ == "__main__":

    chunks = create_embedded_chunks()

    print("\nTotal chunks:", len(chunks))

    for chunk in chunks:

        print("\n--------------------")
        print("Chunk ID:", chunk["chunk_id"])
        print("Page:", chunk["page_number"])
        print("Text:", chunk["text"][:100])
        print("Embedding dimensions:", len(chunk["embedding"]))
        print("First 5 values:", chunk["embedding"][:5])