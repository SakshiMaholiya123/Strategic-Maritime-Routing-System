from pathlib import Path
import os
from dotenv import load_dotenv


def find_project_root(marker: str = ".env") -> Path:
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / marker).exists():
            return current
        current = current.parent
    raise FileNotFoundError(
        f"Could not locate '{marker}' in any parent directory of {Path(__file__).resolve()}"
    )


# .env lives inside backend/, so we search for it starting from this file
BACKEND_DIR = find_project_root(marker=".env")
BASE_DIR = BACKEND_DIR.parent  # project root, one level above backend/

ENV_PATH = BACKEND_DIR / ".env"

load_dotenv(ENV_PATH)


class Config:

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    DATABASE_URL = (
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