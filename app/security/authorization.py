from app.database import get_connection


def get_user_context(username):
    """
    Get the user's organization and assigned roles.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            u.id,
            u.organization_id,
            u.username,
            ARRAY_AGG(r.name)
        FROM users u
        LEFT JOIN user_roles ur
            ON u.id = ur.user_id
        LEFT JOIN roles r
            ON ur.role_id = r.id
        WHERE u.username = %s
        GROUP BY
            u.id,
            u.organization_id,
            u.username;
    """, (username,))

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result is None:
        return None

    return {
        "user_id": result[0],
        "organization_id": result[1],
        "username": result[2],
        "roles": result[3] or []
    }


def get_authorized_document_ids(username):
    """
    Return documents that this user is allowed to access.
    """

    user_context = get_user_context(username)

    if user_context is None:
        return None

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT d.id

        FROM documents d

        INNER JOIN document_access da
            ON d.id = da.document_id

        INNER JOIN roles r
            ON da.role_id = r.id

        INNER JOIN user_roles ur
            ON r.id = ur.role_id

        WHERE d.organization_id = %s
          AND ur.user_id = %s;
    """, (
        user_context["organization_id"],
        user_context["user_id"]
    ))

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return [row[0] for row in rows]