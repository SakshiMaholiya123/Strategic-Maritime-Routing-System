from langchain_chroma import Chroma

from backend.config import Config
from backend.rag.loader import DocumentLoader
from backend.rag.splitter import DocumentSplitter
from backend.rag.embedder import EmbeddingGenerator

class MaritimeVectorStore:

    def __init__(self):

        self.persist_directory = str(Config.CHROMA_DB_PATH)
        self.collection_name = "geopolitical_intel"

    def build_vector_store(self):

        print("\nLoading Reports...")
        loader = DocumentLoader()
        documents = loader.load_documents()

        print("\nSplitting Reports...")
        splitter = DocumentSplitter()
        chunks = splitter.split_documents(documents)

        # Sanitize metadata: Chroma does not accept None values
        for chunk in chunks:
            for key, value in chunk.metadata.items():
                if value is None:
                    chunk.metadata[key] = ""

        print("\nLoading Embedding Model...")
        embedding_model = EmbeddingGenerator().get_embedding_model()

        print("\nCreating Chroma Vector Store...")

        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name
        )

        print("\nVector Store Created Successfully.")

        print(f"\nTotal Chunks Stored : {len(chunks)}")

        return vector_db


if __name__ == "__main__":

    vector_store = MaritimeVectorStore()

    db = vector_store.build_vector_store()