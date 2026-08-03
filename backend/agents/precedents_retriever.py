from typing import List

from backend.config import Config
from backend.rag.embedder import EmbeddingGenerator


def get_similar_precedents(strait_id: str, top_k: int = None) -> List[str]:
    """
    Query the past_routing_precedents ChromaDB collection for similar
    past decisions on this strait. Returns an empty list gracefully if
    the collection is empty or doesn't exist yet.
    """

    top_k = top_k or Config.PRECEDENTS_TOP_K

    try:
        from langchain_chroma import Chroma

        embedding_model = EmbeddingGenerator().get_embedding_model()

        vector_db = Chroma(
            persist_directory=str(Config.CHROMA_DB_PATH),
            embedding_function=embedding_model,
            collection_name="past_routing_precedents"
        )

        if vector_db._collection.count() == 0:
            return []

        results = vector_db.similarity_search(
            query=f"routing decisions for {strait_id}",
            k=top_k,
            filter={"strait_id": strait_id}
        )

        return [doc.page_content for doc in results]

    except Exception as e:
        print(f"Warning: could not query past_routing_precedents ({e})")
        return []