from app.database import get_connection


def log_query(
    username,
    query,
    accessed_document_ids,
    access_granted
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO audit_logs (
            organization_id,
            user_id,
            query,
            accessed_document_ids,
            access_granted
        )

        SELECT
            u.organization_id,
            u.id,
            %s,
            %s,
            %s

        FROM users u

        WHERE u.username = %s;
    """, (
        query,
        accessed_document_ids,
        access_granted,
        username
    ))

    connection.commit()

    cursor.close()
    connection.close()