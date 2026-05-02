import app.db.models  # registers all models

from app.db.session import Base, engine

Base.metadata.create_all(bind=engine)