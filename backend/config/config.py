from pathlib import Path
import os
from dotenv import load_dotenv


def find_project_root(marker: str = ".env") -> Path | None:
    """
    Walk up from this file's location looking for the marker file.
    Returns None if not found (e.g. on Streamlit Cloud, where secrets
    are injected directly into os.environ instead of a physical .env file).
    """
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / marker).exists():
            return current
        current = current.parent
    return None


_project_root = find_project_root(marker=".env")

if _project_root is not None:
    # Local development: .env exists, load it
    BACKEND_DIR = _project_root
    BASE_DIR = BACKEND_DIR.parent
    load_dotenv(BACKEND_DIR / ".env")
else:
    # Cloud deployment (e.g. Streamlit Cloud): no .env file,
    # environment variables are already injected by the platform.
    BACKEND_DIR = Path(__file__).resolve().parent.parent
    BASE_DIR = BACKEND_DIR.parent


class Config:

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    DATABASE_URL = os.getenv("DATABASE_URL") or (
        f"postgresql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?sslmode=require"
    )

    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

    COLLECTION_NAME = os.getenv("COLLECTION_NAME")

    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    TOP_K = int(os.getenv("TOP_K", 5))

    DATASET_PATH = BASE_DIR / "datasets" / "processed"
    RAW_DATASET_PATH = BASE_DIR / "datasets" / "raw"

    RAG_REPORTS_PATH = BACKEND_DIR / "knowledge_base" / "reports"
    CHROMA_DB_PATH = BACKEND_DIR / "knowledge_base" / "chroma_db"

    LOG_PATH = BASE_DIR / "logs"

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile")

    PRECEDENTS_TOP_K = int(os.getenv("PRECEDENTS_TOP_K", 3))

    DAILY_HOLDING_COST_RATE = float(os.getenv("DAILY_HOLDING_COST_RATE", 0.0015))
    SLA_PENALTY_RATE = float(os.getenv("SLA_PENALTY_RATE", 0.01))
    DIVERGENCE_TOLERANCE = float(os.getenv("DIVERGENCE_TOLERANCE", "0.3"))
    HUMAN_APPROVAL_CARGO_THRESHOLD_USD = float(os.getenv("HUMAN_APPROVAL_CARGO_THRESHOLD_USD", "2000000"))