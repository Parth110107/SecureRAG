from app.retrieval.search import semantic_search
from app.generation.llm import generate_answer


def build_context(results):

    context_parts = []

    for index, result in enumerate(results, start=1):

        citation = result["citation"]

        context_parts.append(
            f"""
SOURCE {index}

Document: {citation["document"]}
Page: {citation["page"]}
Chunk ID: {citation["chunk_id"]}

Content:
{result["text"]}
"""
        )

    return "\n".join(context_parts)


def build_prompt(question, context):

    prompt = f"""
You are SecureRAG, a document question-answering system.

Answer the user's question using ONLY the information
provided in the retrieved document context.

Do not use outside knowledge.

If the answer cannot be found in the provided context,
say:

"I could not find this information in the provided documents."

Keep the answer concise and factual.

For every important claim, cite the source using the
exact document, page, and chunk information provided
in the context.

Do not write placeholder citations such as:
[Source: Document, Page, Chunk ID]

Use the actual source information from the retrieved context.

USER QUESTION:
{question}

RETRIEVED DOCUMENT CONTEXT:
{context}

ANSWER:
"""

    return prompt


def ask(question, user_role="owner", top_k=3):
    results = semantic_search(
        query=question,
        user_role=user_role,
        top_k=top_k
    )
    if not results:

        return {
            "answer": "I could not find authorized information for this question.",
            "sources": []
        }

    context = build_context(results)
    prompt = build_prompt(
        question,
        context
    )
    answer = generate_answer(prompt)

    sources = [
        result["citation"]
        for result in results
    ]

    return {
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":

    question = "Which project involved forecasting?"

    result = ask(question)

    print("\n" + "=" * 70)
    print("SECURERAG ANSWER")
    print("=" * 70)

    print(result["answer"])

    print("\n" + "=" * 70)
    print("SOURCES")
    print("=" * 70)

    for source in result["sources"]:

        print(
            f"""
Document: {source["document"]}
Page: {source["page"]}
Chunk: {source["chunk_id"]}
Similarity: {source["similarity"]:.4f}
Classification: {source["classification"]}
"""
        )