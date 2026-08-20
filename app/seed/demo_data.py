from app.database import get_connection


def seed_demo_data():

    connection = get_connection()
    cursor = connection.cursor()

    # ==================================================
    # ORGANIZATION
    # ==================================================

    cursor.execute("""
        INSERT INTO organizations (name)
        VALUES ('Acme Corporation')
        ON CONFLICT DO NOTHING
        RETURNING id;
    """)

    result = cursor.fetchone()

    if result:
        organization_id = result[0]
    else:
        cursor.execute("""
            SELECT id
            FROM organizations
            WHERE name = 'Acme Corporation';
        """)

        organization_id = cursor.fetchone()[0]

    # ==================================================
    # ROLES
    # ==================================================

    roles = [
        "Admin",
        "Manager",
        "Employee"
    ]

    role_ids = {}

    for role_name in roles:

        cursor.execute("""
            INSERT INTO roles (
                organization_id,
                name
            )

            VALUES (%s, %s)

            ON CONFLICT (
                organization_id,
                name
            )

            DO UPDATE SET name = EXCLUDED.name

            RETURNING id;
        """, (
            organization_id,
            role_name
        ))

        role_ids[role_name] = cursor.fetchone()[0]

    # ==================================================
    # USERS
    # ==================================================

    users = [
        ("admin_demo", "admin@acme-demo.local"),
        ("manager_demo", "manager@acme-demo.local"),
        ("employee_demo", "employee@acme-demo.local")
    ]

    user_ids = {}

    for username, email in users:

        cursor.execute("""
            INSERT INTO users (
                organization_id,
                username,
                email
            )

            VALUES (%s, %s, %s)

            ON CONFLICT (
                organization_id,
                username
            )

            DO UPDATE SET email = EXCLUDED.email

            RETURNING id;
        """, (
            organization_id,
            username,
            email
        ))

        user_ids[username] = cursor.fetchone()[0]

    # ==================================================
    # USER → ROLE ASSIGNMENTS
    # ==================================================

    assignments = [
        ("admin_demo", "Admin"),
        ("manager_demo", "Manager"),
        ("employee_demo", "Employee")
    ]

    for username, role_name in assignments:

        cursor.execute("""
            INSERT INTO user_roles (
                user_id,
                role_id
            )

            VALUES (%s, %s)

            ON CONFLICT DO NOTHING;
        """, (
            user_ids[username],
            role_ids[role_name]
        ))

    # ==================================================
    # DEMO DOCUMENTS
    # ==================================================

    documents = [
        (
            "Employee Handbook",
            user_ids["admin_demo"],
            "internal"
        ),
        (
            "Engineering Policy",
            user_ids["manager_demo"],
            "internal"
        ),
        (
            "Expense Policy",
            user_ids["admin_demo"],
            "confidential"
        )
    ]

    document_ids = {}

    for name, owner_id, classification in documents:

        cursor.execute("""
            INSERT INTO documents (
                organization_id,
                name,
                owner_user_id,
                classification
            )

            VALUES (%s, %s, %s, %s)

            RETURNING id;
        """, (
            organization_id,
            name,
            owner_id,
            classification
        ))

        document_ids[name] = cursor.fetchone()[0]

    # ==================================================
    # DOCUMENT ACCESS
    # ==================================================

    access_rules = [

        (
            "Employee Handbook",
            ["Admin", "Manager", "Employee"]
        ),

        (
            "Engineering Policy",
            ["Admin", "Manager"]
        ),

        (
            "Expense Policy",
            ["Admin"]
        )
    ]

    for document_name, allowed_roles in access_rules:

        document_id = document_ids[document_name]

        for role_name in allowed_roles:

            cursor.execute("""
                INSERT INTO document_access (
                    document_id,
                    role_id
                )

                VALUES (%s, %s)

                ON CONFLICT DO NOTHING;
            """, (
                document_id,
                role_ids[role_name]
            ))

    connection.commit()

    cursor.close()
    connection.close()

    print("Demo organization created successfully!")


if __name__ == "__main__":
    seed_demo_data()