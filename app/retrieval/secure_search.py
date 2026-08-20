from sentence_transformers import SentenceTransformer

from app.database import get_connection
from app.security.authorization import get_authorized_document_ids


MODEL_NAME = "all-MiniLM-L6-v2"

SIMILARITY_THRESHOLD = 0.25

model = SentenceTransformer(MODEL_NAME)


def secure_search(
    username,
    query,
    top_k=5,
    similarity_threshold=SIMILARITY_THRESHOLD
):
    """
    Perform vector search only on documents
    the user is authorized to access.

    Results below the similarity threshold
    are removed before being returned.
    """

    authorized_document_ids = get_authorized_document_ids(
        username
    )

    # Unknown user
    if authorized_document_ids is None:
        return []

    # User has no accessible documents
    if not authorized_document_ids:
        return []

    # ----------------------------------------------
    # CREATE QUERY EMBEDDING
    # ----------------------------------------------

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    )

    connection = get_connection()
    cursor = connection.cursor()

    embedding = query_embedding.tolist()

    # ----------------------------------------------
    # SECURE VECTOR SEARCH
    # ----------------------------------------------

    cursor.execute("""
        SELECT
            dc.id,
            dc.document_id,
            dc.chunk_index,
            dc.text,
            dc.page_number,
            d.name,
            d.classification,

            1 - (
                dc.embedding <=> %s::vector
            ) AS similarity

        FROM document_chunks_v2 dc

        INNER JOIN documents d
            ON dc.document_id = d.id

        WHERE d.organization_id = (
            SELECT organization_id
            FROM users
            WHERE username = %s
        )

        AND dc.document_id = ANY(%s)

        ORDER BY dc.embedding <=> %s::vector

        LIMIT %s;
    """, (
        embedding,
        username,
        authorized_document_ids,
        embedding,
        top_k
    ))

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    # ----------------------------------------------
    # BUILD RESULTS
    # ----------------------------------------------

    results = []

    for row in rows:

        similarity = float(row[7])

        # ------------------------------------------
        # SIMILARITY THRESHOLD
        # ------------------------------------------

        if similarity < similarity_threshold:
            continue

        results.append({
            "chunk_id": row[0],
            "document_id": row[1],
            "chunk_index": row[2],
            "text": row[3],
            "page_number": row[4],
            "document_name": row[5],
            "classification": row[6],
            "similarity": similarity
        })

    return results