"""
App entrypoint: creates the FastAPI app, wires up routers, and initializes
the SQLite database + ChromaDB vector store on startup.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import chat, students
from app.chatbot.vector_store import sync_students
from app.core.database import SessionLocal, init_db
from app.core.config import settings
from app.crud.student import get_students


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables, then sync ChromaDB from whatever is in SQLite.
    init_db()
    db = SessionLocal()
    try:
        sync_students(get_students(db, limit=1000))
    finally:
        db.close()
    yield
    # (No teardown needed -- SQLite/Chroma persist to disk.)


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(students.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"message": f"{settings.PROJECT_NAME} is running. See /docs for the API."}
