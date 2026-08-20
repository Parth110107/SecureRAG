from app.database import get_connection

from app.security.auth import hash_password
import os

DEMO_PASSWORD = os.getenv("DEMO_PASSWORD")

if not DEMO_PASSWORD:
    raise RuntimeError(
        "DEMO_PASSWORD environment variable is not configured."
    )

def setup_demo_users():

    connection = get_connection()
    cursor = connection.cursor()

    password_hash = hash_password(
        DEMO_PASSWORD
    )

    usernames = [
        "admin_demo",
        "manager_demo",
        "employee_demo"
    ]

    for username in usernames:

        cursor.execute(
            """
            UPDATE users

            SET password_hash = %s

            WHERE username = %s;
            """,
            (
                password_hash,
                username
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    print(
        "Demo user passwords configured."
    )


if __name__ == "__main__":

    setup_demo_users()