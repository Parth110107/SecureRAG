from app.retrieval.secure_search import secure_search
from app.generation.llm import generate_answer
from app.security.audit import log_query

def build_context(results):

    context_parts = []

    for index, result in enumerate(results, start=1):

        context_parts.append(
            f"""
SOURCE {index}

Document: {result['document_name']}
Page: {result['page_number']}
Chunk: {result['chunk_index']}

Content:
{result['text']}
"""
        )

    return "\n".join(context_parts)


def build_prompt(question, context):

    return f"""
You are a retrieval-based question answering system.

Your job is to answer the USER QUESTION using ONLY the
RETRIEVED DOCUMENT CONTEXT.

The retrieved context is authoritative.

RULES:

- Read the context carefully.
- Find the exact information that answers the question.
- Answer directly and concisely.
- Do not use outside knowledge.
- Do not invent facts.
- Do not mention unauthorized documents.
- Do not create or invent citations.
- Do not write SOURCE numbers.
- Do not write document names or page numbers as citations.
- The application will provide verified source information separately.

If the answer is explicitly present in the retrieved context,
answer it directly.

If the answer is not present in the retrieved context, say:

"I could not find this information in the documents you are authorized to access."

USER QUESTION:
{question}

RETRIEVED DOCUMENT CONTEXT:
{context}

ANSWER:
"""


def ask_secure_rag(
    username,
    question,
    top_k=3
):

    # --------------------------------------------------
    # SECURE RETRIEVAL
    # --------------------------------------------------

    results = secure_search(
        username=username,
        query=question,
        top_k=top_k
    )
    accessed_document_ids = list({
    result["document_id"]
    for result in results
    })

    log_query(
    username=username,
    query=question,
    accessed_document_ids=accessed_document_ids,
    access_granted=bool(results)
    )
    # --------------------------------------------------
    # NO AUTHORIZED RESULTS
    # --------------------------------------------------

    if not results:

        return {
            "answer": (
                "I could not find this information in "
                "the documents you are authorized to access."
            ),
            "sources": []
        }

    # --------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------

    context = build_context(results)

    # --------------------------------------------------
    # BUILD LLM PROMPT
    # --------------------------------------------------

    prompt = build_prompt(
        question=question,
        context=context
    )

    # --------------------------------------------------
    # GENERATE ANSWER
    # --------------------------------------------------
    
    answer = generate_answer(prompt)
    answer = answer.strip()

    # --------------------------------------------------
    # BUILD SOURCES
    # --------------------------------------------------

    sources = []

    for result in results:

        sources.append({
            "document": result["document_name"],
            "page": result["page_number"],
            "chunk": result["chunk_index"],
            "similarity": result["similarity"],
            "classification": result["classification"]
        })

    return {
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":

    username = "admin_demo"

    question = "What is the meal expense limit?"

    result = ask_secure_rag(
        username=username,
        question=question
    )

    print("\n" + "=" * 70)
    print("SECURERAG ANSWER")
    print("=" * 70)

    print(result["answer"])

    print("\n" + "=" * 70)
    print("SOURCES")
    print("=" * 70)

    for source in result["sources"]:

        print("\n------------------------------")

        print(
            f"Document: {source['document']}"
        )

        print(
            f"Page: {source['page']}"
        )

        print(
            f"Chunk: {source['chunk']}"
        )

        print(
            f"Similarity: "
            f"{source['similarity']:.4f}"
        )

        print(
            f"Classification: "
            f"{source['classification']}"
        )