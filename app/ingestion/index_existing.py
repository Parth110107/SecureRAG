from app.ingestion.document_service import index_document


if __name__ == "__main__":

    index_document(
        document_id=4,
        file_path="data/documents/Krupa.pdf"
    )

    print("\nIndexing complete!")