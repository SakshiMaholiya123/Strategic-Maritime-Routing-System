from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import Config

engine = create_engine(
    Config.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
     connect_args={
        "connect_timeout": 10
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """
    Returns a database session.

    Used by:
    - FastAPI
    - CrewAI Tools
    - ETL Scripts
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()