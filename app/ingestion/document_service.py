from sentence_transformers import SentenceTransformer

from app.database import get_connection
from app.ingestion.loader import extract_pages_from_pdf
from app.ingestion.chunker import split_text


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def create_document(
    username,
    document_name,
    classification="internal",
    allowed_roles=None
):

    if allowed_roles is None:
        allowed_roles = ["Admin"]

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------
    # FIND USER
    # --------------------------------------------------

    cursor.execute(
        """
        SELECT id, organization_id
        FROM users
        WHERE username = %s;
        """,
        (username,)
    )

    user = cursor.fetchone()

    if user is None:

        cursor.close()
        connection.close()

        raise ValueError(
            "User does not exist."
        )

    user_id = user[0]
    organization_id = user[1]

    # --------------------------------------------------
    # CREATE DOCUMENT
    # --------------------------------------------------

    cursor.execute(
        """
        INSERT INTO documents (
            organization_id,
            name,
            owner_user_id,
            classification
        )

        VALUES (
            %s,
            %s,
            %s,
            %s
        )

        RETURNING id;
        """,
        (
            organization_id,
            document_name,
            user_id,
            classification
        )
    )

    document_id = cursor.fetchone()[0]

    # --------------------------------------------------
    # ASSIGN DOCUMENT ACCESS
    # --------------------------------------------------

    for role_name in allowed_roles:

        cursor.execute(
            """
            INSERT INTO document_access (
                document_id,
                role_id
            )

            SELECT
                %s,
                id

            FROM roles

            WHERE organization_id = %s
            AND name = %s

            ON CONFLICT DO NOTHING;
            """,
            (
                document_id,
                organization_id,
                role_name
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    return document_id


def index_document(
    document_id,
    file_path
):

    print(
        f"\nIndexing document {document_id}..."
    )

    # ----------------------------------------------
    # LOAD PDF
    # ----------------------------------------------

    pages = extract_pages_from_pdf(
        file_path
    )

    # ----------------------------------------------
    # CREATE CHUNKS
    # ----------------------------------------------

    chunks = []

    chunk_index = 0

    for page in pages:

        page_chunks = split_text(
            text=page["text"],
            document_id=str(document_id),
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

    print(
        f"Created {len(chunks)} chunks."
    )

    if not chunks:

        raise ValueError(
            "No text could be extracted from document."
        )

    # ----------------------------------------------
    # GENERATE EMBEDDINGS
    # ----------------------------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True
    )

    print("Embeddings generated.")

    # ----------------------------------------------
    # STORE CHUNKS
    # ----------------------------------------------

    connection = get_connection()
    cursor = connection.cursor()

    # Remove previous chunks if re-indexing
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
        f"Stored {len(chunks)} chunks."
    )

    return len(chunks)
def ingest_document(
    username,
    document_name,
    file_path,
    classification="internal",
    allowed_roles=None
):

    if allowed_roles is None:
        allowed_roles = ["Admin"]

    # ----------------------------------------------
    # CREATE DOCUMENT + PERMISSIONS
    # ----------------------------------------------

    document_id = create_document(
        username=username,
        document_name=document_name,
        classification=classification,
        allowed_roles=allowed_roles
    )

    try:

        # ------------------------------------------
        # EXTRACT + CHUNK + EMBED + STORE
        # ------------------------------------------

        chunks_created = index_document(
            document_id=document_id,
            file_path=file_path
        )

        return {
            "document_id": document_id,
            "chunks_created": chunks_created
        }

    except Exception:

        # ------------------------------------------
        # REMOVE DOCUMENT IF INDEXING FAILS
        # ------------------------------------------

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM document_access
            WHERE document_id = %s;
            """,
            (document_id,)
        )

        cursor.execute(
            """
            DELETE FROM documents
            WHERE id = %s;
            """,
            (document_id,)
        )

        connection.commit()

        cursor.close()
        connection.close()

        raise