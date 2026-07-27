import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_PATH = BASE_DIR / ".env"

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

    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")

    COLLECTION_NAME = os.getenv("COLLECTION_NAME")


    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))

    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

    TOP_K = int(os.getenv("TOP_K", 5))

    DATASET_PATH = BASE_DIR / "datasets" / "processed"

    RAW_DATASET_PATH = BASE_DIR / "datasets" / "raw"

    RAG_DATA_PATH = BASE_DIR / "knowledge_base"

    LOG_PATH = BASE_DIR / "logs"
