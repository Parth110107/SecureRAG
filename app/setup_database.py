from app.database import get_connection


def setup_database():

    connection = get_connection()
    cursor = connection.cursor()

    # ==================================================
    # ENABLE PGVECTOR
    # ==================================================

    cursor.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
    """)

    # ==================================================
    # ORGANIZATIONS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (

            id SERIAL PRIMARY KEY,

            name TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        );
    """)

    # ==================================================
    # USERS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id SERIAL PRIMARY KEY,

            organization_id INTEGER NOT NULL
                REFERENCES organizations(id)
                ON DELETE CASCADE,

            username TEXT NOT NULL,

            email TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(organization_id, username)

        );
    """)
    cursor.execute("""
       ALTER TABLE users
       ADD COLUMN IF NOT EXISTS password_hash TEXT;
    """)

    # ==================================================
    # ROLES
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (

            id SERIAL PRIMARY KEY,

            organization_id INTEGER NOT NULL
                REFERENCES organizations(id)
                ON DELETE CASCADE,

            name TEXT NOT NULL,

            UNIQUE(organization_id, name)

        );
    """)

    # ==================================================
    # USER ROLES
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_roles (

            user_id INTEGER NOT NULL
                REFERENCES users(id)
                ON DELETE CASCADE,

            role_id INTEGER NOT NULL
                REFERENCES roles(id)
                ON DELETE CASCADE,

            PRIMARY KEY(user_id, role_id)

        );
    """)

    # ==================================================
    # DOCUMENTS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (

            id SERIAL PRIMARY KEY,

            organization_id INTEGER NOT NULL
                REFERENCES organizations(id)
                ON DELETE CASCADE,

            name TEXT NOT NULL,

            owner_user_id INTEGER
                REFERENCES users(id)
                ON DELETE SET NULL,

            classification TEXT DEFAULT 'internal',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        );
    """)

    # ==================================================
    # DOCUMENT ACCESS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_access (

            document_id INTEGER NOT NULL
                REFERENCES documents(id)
                ON DELETE CASCADE,

            role_id INTEGER NOT NULL
                REFERENCES roles(id)
                ON DELETE CASCADE,

            PRIMARY KEY(document_id, role_id)

        );
    """)

    # ==================================================
    # ENTERPRISE DOCUMENT CHUNKS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks_v2 (

            id SERIAL PRIMARY KEY,

            document_id INTEGER NOT NULL
                REFERENCES documents(id)
                ON DELETE CASCADE,

            chunk_index INTEGER NOT NULL,

            text TEXT NOT NULL,

            page_number INTEGER,

            embedding VECTOR(384),

            UNIQUE(document_id, chunk_index)

        );
    """)

    # ==================================================
    # AUDIT LOGS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (

            id SERIAL PRIMARY KEY,

            organization_id INTEGER
                REFERENCES organizations(id)
                ON DELETE SET NULL,

            user_id INTEGER
                REFERENCES users(id)
                ON DELETE SET NULL,

            query TEXT,

            accessed_document_ids INTEGER[],

            access_granted BOOLEAN NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        );
    """)

    connection.commit()

    cursor.close()
    connection.close()

    print("Enterprise database schema created successfully!")


if __name__ == "__main__":
    setup_database()