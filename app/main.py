from fastapi import FastAPI
from app.api import routes_docs, routes_qa

# 👇 ADD THIS (CRITICAL FIX)
from app.db.session import Base, engine
from app.db import models   # <-- THIS IS REQUIRED

app = FastAPI(
    title="Smart Document Q&A System",
    version="1.0.0"
)

app.include_router(routes_docs.router, prefix="/documents", tags=["Documents"])
app.include_router(routes_qa.router, prefix="/chat", tags=["Q&A"])


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def health_check():
    return {"status": "running"}