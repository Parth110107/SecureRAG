from sentence_transformers import SentenceTransformer


class Embedder:

    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def generate_embedding(self, text):
        return self.model.encode(text)

    def generate_embeddings(self, texts):
        return self.model.encode(texts)
if __name__ == "__main__":

    embedder = Embedder()

    text = "I built a sales forecasting project using Python."

    vector = embedder.generate_embedding(text)

    print("Vector type:", type(vector))
    print("Vector shape:", vector.shape)
    print("First 10 values:", vector[:10])