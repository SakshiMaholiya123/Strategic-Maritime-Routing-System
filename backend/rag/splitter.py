from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import Config


class DocumentSplitter:
    """
    Splits LangChain Document objects into smaller chunks.
    """

    def __init__(self):
        self.chunk_size = Config.CHUNK_SIZE
        self.chunk_overlap = Config.CHUNK_OVERLAP

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

    def split_documents(self, documents):
        """
        Split the documents into chunks.
        """

        chunks = self.text_splitter.split_documents(documents)

        print(f"\nOriginal Documents : {len(documents)}")
        print(f"Total Chunks Created : {len(chunks)}")

        return chunks


if __name__ == "__main__":

    from backend.rag.loader import DocumentLoader

    loader = DocumentLoader()

    documents = loader.load_documents()

    splitter = DocumentSplitter()

    chunks = splitter.split_documents(documents)

    print("\nFirst Chunk Metadata:")
    print(chunks[0].metadata)

    print("\nFirst Chunk:\n")
    print(chunks[0].page_content)