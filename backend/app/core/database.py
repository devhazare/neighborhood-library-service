from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from app.core.config import settings

# Connection pool settings for production scalability
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_pre_ping=True,     # Verify connections before using
    pool_size=20,           # Number of permanent connections
    max_overflow=10,        # Additional connections when pool exhausted
    pool_timeout=30,        # Seconds to wait for a connection
    pool_recycle=3600,      # Recycle connections after 1 hour (prevent stale connections)
    echo=settings.DEBUG,    # Log SQL queries in debug mode
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
