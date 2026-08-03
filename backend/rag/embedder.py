from langchain_huggingface import HuggingFaceEmbeddings

from backend.config import Config


class EmbeddingGenerator:


    def __init__(self):

        self.embedding_model_name = Config.EMBEDDING_MODEL

        self.embedding_model = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={
                "device": "cpu"
            },
            encode_kwargs={
                "normalize_embeddings": True
            }
        )

    def get_embedding_model(self):

        return self.embedding_model


if __name__ == "__main__":

    embedder = EmbeddingGenerator()

    embedding_model = embedder.get_embedding_model()

    sample_text = [
        "The Port of Singapore is one of the busiest ports in the world."
    ]

    embedding = embedding_model.embed_documents(sample_text)

    print("\nEmbedding Model Loaded Successfully.")

    print(f"\nEmbedding Dimension : {len(embedding[0])}")

    print("\nFirst 10 Values:\n")

    print(embedding[0][:10])