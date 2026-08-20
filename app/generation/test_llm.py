from app.generation.llm import generate_answer


prompt = """
Explain what Retrieval-Augmented Generation is
in 3 simple sentences.
"""


answer = generate_answer(prompt)

print("\nLLM RESPONSE:")
print(answer)