from pathlib import Path

from sentence_transformers import SentenceTransformer

from app.database import get_connection
from app.ingestion.loader import extract_pages_from_pdf
from app.ingestion.chunker import split_text


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def get_document_id(document_name, organization_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM documents
        WHERE name = %s
        AND organization_id = %s;
        """,
        (
            document_name,
            organization_id
        )
    )

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result is None:
        raise ValueError(
            f"Document '{document_name}' "
            f"was not found for organization "
            f"{organization_id}."
        )

    return result[0]


def ingest_enterprise_document(
    file_path,
    document_name,
    organization_id
):

    print("\n" + "=" * 60)
    print(f"INGESTING: {document_name}")
    print("=" * 60)

    # --------------------------------------------------
    # FIND DOCUMENT
    # --------------------------------------------------

    document_id = get_document_id(
        document_name,
        organization_id
    )

    print(f"Document ID: {document_id}")

    # --------------------------------------------------
    # LOAD PDF
    # --------------------------------------------------

    pages = extract_pages_from_pdf(file_path)

    print(f"Pages found: {len(pages)}")

    # --------------------------------------------------
    # CREATE CHUNKS
    # --------------------------------------------------

    chunks = []

    chunk_index = 0

    for page in pages:

        page_chunks = split_text(
            text=page["text"],
            document_id=document_name,
            owner="system",
            allowed_roles=[],
            classification="internal"
        )

        for chunk in page_chunks:

            chunks.append({
                "chunk_index": chunk_index,
                "text": chunk["text"],
                "page_number": page["page_number"]
            })

            chunk_index += 1

    print(f"Chunks created: {len(chunks)}")

    # --------------------------------------------------
    # GENERATE EMBEDDINGS
    # --------------------------------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True
    )

    print("Embeddings generated.")

    # --------------------------------------------------
    # STORE IN DATABASE
    # --------------------------------------------------

    connection = get_connection()
    cursor = connection.cursor()

    # Remove old chunks if the document
    # is being ingested again.
    cursor.execute(
        """
        DELETE FROM document_chunks_v2
        WHERE document_id = %s;
        """,
        (document_id,)
    )

    for chunk, embedding in zip(
        chunks,
        embeddings
    ):

        cursor.execute(
            """
            INSERT INTO document_chunks_v2 (
                document_id,
                chunk_index,
                text,
                page_number,
                embedding
            )

            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s::vector
            );
            """,
            (
                document_id,
                chunk["chunk_index"],
                chunk["text"],
                chunk["page_number"],
                embedding.tolist()
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    print(
        f"Stored {len(chunks)} chunks "
        f"for document {document_id}."
    )


def ingest_all_demo_documents():

    organization_id = 1

    documents = [
        (
            "data/demo/acme/employee_handbook.pdf",
            "Employee Handbook"
        ),
        (
            "data/demo/acme/engineering_policy.pdf",
            "Engineering Policy"
        ),
        (
            "data/demo/acme/expense_policy.pdf",
            "Expense Policy"
        )
    ]

    for file_path, document_name in documents:

        if not Path(file_path).exists():

            print(
                f"WARNING: File not found: "
                f"{file_path}"
            )

            continue

        ingest_enterprise_document(
            file_path=file_path,
            document_name=document_name,
            organization_id=organization_id
        )


if __name__ == "__main__":

    ingest_all_demo_documents()

    print("\nEnterprise ingestion complete!")