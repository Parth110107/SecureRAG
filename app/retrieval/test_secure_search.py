from app.retrieval.secure_search import secure_search


def run_test(username, question):

    print("\n" + "=" * 70)
    print("USER:", username)
    print("QUESTION:", question)
    print("=" * 70)

    results = secure_search(
        username=username,
        query=question,
        top_k=3
    )

    if not results:
        print("\nNO AUTHORIZED RESULTS")
        return

    for result in results:

        print("\n------------------------------")

        print(
            "Document:",
            result["document_name"]
        )

        print(
            "Similarity:",
            round(result["similarity"], 4)
        )

        print(
            "Page:",
            result["page_number"]
        )

        print(
            "Classification:",
            result["classification"]
        )

        print("Text:")

        print(result["text"])


if __name__ == "__main__":

    run_test(
       "admin_demo",
       "What is mentioned in Krupa.pdf about Experience?" 
    ) 

    run_test(
        "manager_demo",
        "What is the meal expense limit?"
    )

    run_test(
        "employee_demo",
        "What is the meal expense limit?"
    )