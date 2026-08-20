from app.security.authorization import (
    get_user_context,
    get_authorized_document_ids
)


def test_user(username):

    print("\n" + "=" * 60)
    print("USER:", username)
    print("=" * 60)

    context = get_user_context(username)

    print("\nUSER CONTEXT:")
    print(context)

    documents = get_authorized_document_ids(username)

    print("\nAUTHORIZED DOCUMENT IDS:")
    print(documents)


if __name__ == "__main__":

    test_user("admin_demo")

    test_user("manager_demo")

    test_user("employee_demo")