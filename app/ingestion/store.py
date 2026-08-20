from app.database import get_connection


def store_chunks(chunks):

    connection = get_connection()

    cursor = connection.cursor()

    for chunk in chunks:

        cursor.execute(
            """
            INSERT INTO document_chunks (
                chunk_id,
                document_id,
                text,
                owner,
                allowed_roles,
                classification,
                page_number,
                embedding
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            ON CONFLICT (chunk_id)
            DO UPDATE SET
                text = EXCLUDED.text,
                owner = EXCLUDED.owner,
                allowed_roles = EXCLUDED.allowed_roles,
                classification = EXCLUDED.classification,
                page_number = EXCLUDED.page_number,
                embedding = EXCLUDED.embedding;
            """,
            (
                chunk["chunk_id"],
                chunk["document_id"],
                chunk["text"],
                chunk["owner"],
                chunk["allowed_roles"],
                chunk["classification"],
                chunk["page_number"],
                chunk["embedding"]
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    print(f"Stored {len(chunks)} chunks in PostgreSQL.")