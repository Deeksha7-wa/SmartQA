from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 🧠 IMPORTANT: production-safe engine config
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # fixes stale DB connections (VERY IMPORTANT)
    pool_recycle=300,     # avoids connection timeout issues
    echo=False
)

# 🔥 session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 🧱 base for all models
Base = declarative_base()


# ⚡ FASTAPI DEPENDENCY (CRITICAL)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()