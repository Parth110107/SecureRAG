from app.database import get_connection
from app.ingestion.embedder import Embedder
from app.retrieval.citations import create_citation


def semantic_search(
    query,
    user_role="owner",
    top_k=5
):

    embedder = Embedder()

    query_embedding = embedder.generate_embeddings([query])[0]

    query_embedding = query_embedding.tolist()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            chunk_id,
            document_id,
            text,
            owner,
            allowed_roles,
            classification,
            page_number,

            1 - (embedding <=> %s::vector) AS similarity

        FROM document_chunks

        WHERE %s = ANY(allowed_roles)

        ORDER BY embedding <=> %s::vector

        LIMIT %s;
        """,
        (
            query_embedding,
            user_role,
            query_embedding,
            top_k
        )
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    results = []

    for row in rows:

        citation = create_citation(row)

        results.append({
            "text": row[2],
            "citation": citation
        })

    return results


if __name__ == "__main__":

    query = "Which project involved forecasting?"

    results = semantic_search(query)

    print("\n" + "=" * 60)
    print("QUERY")
    print("=" * 60)

    print(query)

    for result in results:

        print("\n------------------------------")

        print("Text:")
        print(result["text"])

        print("\nCitation:")
        print(result["citation"])