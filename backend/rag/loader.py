from pathlib import Path
from datetime import datetime

from langchain_community.document_loaders import PyMuPDFLoader

from backend.config import Config


class DocumentLoader:
    """
    Loads all PDF reports from the knowledge base and attaches
    structured metadata required for recency-aware retrieval.
    """

    def __init__(self):
        self.rag_reports_path = Config.RAG_REPORTS_PATH

    def get_pdf_files(self):
        """
        Find every PDF inside the reports directory
        and all of its subfolders.
        """
        pdf_files = list(
            Path(self.rag_reports_path).rglob("*.pdf")
        )
        return pdf_files

    def _get_source_type(self, pdf_path: Path):
        """
        Derive source_type from the immediate parent folder name.
        e.g. reports/security/xyz.pdf -> 'security'
        """
        return pdf_path.parent.name

    def _get_report_date(self, pdf_path: Path, doc_metadata: dict):
        """
        Try PDF's internal creation date first, else fall back
        to file's last-modified timestamp.
        """
        raw_date = doc_metadata.get("creationdate") or doc_metadata.get("creationDate")

        if raw_date:
            try:
                cleaned = raw_date.replace("D:", "")[:8]
                return datetime.strptime(cleaned, "%Y%m%d").date().isoformat()
            except Exception:
                pass

        modified_ts = pdf_path.stat().st_mtime
        return datetime.fromtimestamp(modified_ts).date().isoformat()

    def load_documents(self):
        """
        Load every PDF into LangChain Document objects,
        enriched with strait_id, source_type, severity,
        report_date, supersedes, superseded_by metadata.
        """

        documents = []
        pdf_files = self.get_pdf_files()

        print(f"\nFound {len(pdf_files)} PDF files.\n")

        for pdf in pdf_files:

            print(f"Loading : {pdf.name}")

            loader = PyMuPDFLoader(str(pdf))
            docs = loader.load()

            source_type = self._get_source_type(pdf)

            for doc in docs:

                report_date = self._get_report_date(pdf, doc.metadata)

                doc.metadata.update({
                    "strait_id": "Strait of Hormuz",
                    "source_type": source_type,
                    "severity": 3,
                    "report_date": report_date,
                    "supersedes": None,
                    "superseded_by": None,
                })

            documents.extend(docs)

        print("\nLoading Complete.")
        print(f"Total Pages Loaded : {len(documents)}")

        return documents


if __name__ == "__main__":

    loader = DocumentLoader()
    documents = loader.load_documents()

    print("\nFirst Document Metadata:")
    print(documents[0].metadata)

    print("\nFirst 500 Characters:\n")
    print(documents[0].page_content[:500])