import math
from datetime import datetime

from langchain_chroma import Chroma

from backend.config import Config
from backend.rag.embedder import EmbeddingGenerator


class MaritimeRetriever:
    """
    Retrieves the most relevant, non-superseded document chunks
    from the Chroma vector database, re-ranked by a recency-decay
    function so that a semantically similar but outdated report
    cannot outrank a newer one.
    """

    # Half-life (in days) controlling how fast older reports lose weight.
    # A report half_life days old gets its similarity score halved.
    HALF_LIFE_DAYS = 30

    def __init__(self):

        self.embedding_model = EmbeddingGenerator().get_embedding_model()

        self.collection_name = "geopolitical_intel"
        self.persist_directory = str(Config.CHROMA_DB_PATH)

        self.vector_db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model,
            collection_name=self.collection_name
        )

        print("=" * 60)
        print("Collection Name :", self.collection_name)
        print("Database Path   :", self.persist_directory)

        try:
            count = self.vector_db._collection.count()
            print("Stored Chunks  :", count)
        except Exception as e:
            print("Error:", e)

    def _age_days(self, report_date_str):
        """
        Compute the age of a report in days from its report_date
        metadata (ISO format string). Falls back to a large age
        (treated as very old) if the date is missing or malformed,
        so undated reports don't wrongly dominate ranking.
        """

        if not report_date_str:
            return 3650  # ~10 years, effectively de-prioritized

        try:
            report_date = datetime.fromisoformat(report_date_str)
            age = (datetime.now() - report_date).days
            return max(age, 0)
        except Exception:
            return 3650

    def _recency_weight(self, age_days):
        """
        Exponential decay weight: newer reports get a weight
        close to 1, older reports decay toward 0.
        """
        return math.exp(-age_days / self.HALF_LIFE_DAYS)

    def retrieve_documents(self, query, strait_id=None, top_k=None):
        """
        Retrieve the top-k most relevant, non-superseded chunks,
        re-ranked by similarity_score * recency_weight.

        Args:
            query: the search query string
            strait_id: optional filter to restrict retrieval to a
                       specific chokepoint (e.g. "Strait of Hormuz")
            top_k: number of final results to return (defaults to Config.TOP_K)
        """

        top_k = top_k or Config.TOP_K

        # Build metadata filter: exclude superseded reports.
        # superseded_by is stored as "" (empty string) when not superseded,
        # since Chroma does not accept None values.
        where_filter = {"superseded_by": ""}

        if strait_id:
            where_filter = {
                "$and": [
                    {"superseded_by": ""},
                    {"strait_id": strait_id}
                ]
            }

        # Over-fetch candidates so re-ranking has enough to work with,
        # since some will be pushed down by recency decay.
        fetch_k = max(top_k * 4, 20)

        results = self.vector_db.similarity_search_with_score(
            query,
            k=fetch_k,
            filter=where_filter
        )

        # similarity_search_with_score returns (doc, distance) where
        # LOWER distance = more similar. Convert to a similarity score
        # in (0, 1] so it combines intuitively with recency weight.
        reranked = []

        for doc, distance in results:

            similarity_score = 1 / (1 + distance)

            age_days = self._age_days(doc.metadata.get("report_date"))
            recency_weight = self._recency_weight(age_days)

            final_score = similarity_score * recency_weight

            reranked.append((doc, final_score, similarity_score, age_days))

        reranked.sort(key=lambda x: x[1], reverse=True)

        top_results = reranked[:top_k]

        # Attach ranking diagnostics to metadata for audit-trail purposes
        # (spec requires reconstructing why a report was selected).
        documents = []

        for doc, final_score, similarity_score, age_days in top_results:
            doc.metadata["retrieval_final_score"] = round(final_score, 4)
            doc.metadata["retrieval_similarity_score"] = round(similarity_score, 4)
            doc.metadata["retrieval_age_days"] = age_days
            documents.append(doc)

        return documents

    def get_retriever(self):
        """
        Kept for backward compatibility with rag_pipeline.py /
        LangChain retriever interfaces that expect a plain
        similarity retriever (no recency filtering).
        Prefer retrieve_documents() for anything feeding the
        Risk Assessor agent.
        """

        retriever = self.vector_db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": Config.TOP_K}
        )

        return retriever


if __name__ == "__main__":

    retriever = MaritimeRetriever()

    query = input("\nEnter your question:\n\n> ")

    documents = retriever.retrieve_documents(query)

    print(f"\nRetrieved {len(documents)} documents (recency-reranked).\n")

    for index, doc in enumerate(documents, start=1):

        print("=" * 80)

        print(f"\nDocument {index}")

        print("\nSource:")
        print(doc.metadata.get("source"))

        print("\nSource Type:")
        print(doc.metadata.get("source_type"))

        print("\nReport Date:")
        print(doc.metadata.get("report_date"))

        print("\nFinal Score (similarity x recency):")
        print(doc.metadata.get("retrieval_final_score"))

        print("\nAge (days):")
        print(doc.metadata.get("retrieval_age_days"))

        print("\nContent:\n")

        print(doc.page_content[:700])

        print("\n")