def create_citation(result):
    (
        chunk_id,
        document_id,
        text,
        owner,
        allowed_roles,
        classification,
        page_number,
        similarity
    ) = result

    return {
        "document": document_id,
        "page": page_number,
        "chunk_id": chunk_id,
        "similarity": float(similarity),
        "classification": classification
    }