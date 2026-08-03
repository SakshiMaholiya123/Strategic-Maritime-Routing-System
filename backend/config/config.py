from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]

BACKEND_DIR = BASE_DIR / "backend"

ENV_PATH = BACKEND_DIR / ".env"

load_dotenv(ENV_PATH)


class Config:

    APP_NAME = os.getenv("APP_NAME")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL")

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
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
    model=os.getenv("model")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile")
    PRECEDENTS_TOP_K = int(os.getenv("PRECEDENTS_TOP_K", 3))
    # Financial Modeler assumptions — configurable, not hardcoded in agent logic
    DAILY_HOLDING_COST_RATE = float(os.getenv("DAILY_HOLDING_COST_RATE", 0.0015))  # % of cargo value per day
    SLA_PENALTY_RATE = float(os.getenv("SLA_PENALTY_RATE", 0.01))                   # % of cargo value, flat exposure
    DIVERGENCE_TOLERANCE = float(os.getenv("DIVERGENCE_TOLERANCE", "0.3"))
    HUMAN_APPROVAL_CARGO_THRESHOLD_USD = float(os.getenv("HUMAN_APPROVAL_CARGO_THRESHOLD_USD", "2000000"))

