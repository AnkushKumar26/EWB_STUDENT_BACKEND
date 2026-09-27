"""
ChromaDB-backed vector store for semantic search over student records.

- Embeds each student's profile text with Google's Generative AI embeddings.
- Persists to a local ChromaDB client (./chroma_db by default).
- Re-synced on every app startup so it stays consistent with SQLite.
"""
import chromadb
from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction

from app.core.config import settings
from app.models.student import Student

_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

_embedding_fn = GoogleGenerativeAiEmbeddingFunction(
    api_key=settings.GEMINI_API_KEY,
    model_name=settings.GEMINI_EMBEDDING_MODEL,
)


def get_collection():
    return _client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=_embedding_fn,
    )


def _student_document(student: Student) -> str:
    """Flatten a student's fields into one text blob for embedding."""
    parts = [
        f"Name: {student.name}",
        f"Major: {student.major}" if student.major else "",
        f"Year: {student.year}" if student.year else "",
        f"Enrolled course: {student.enrolled_course}" if student.enrolled_course else "",
    ]
    return ". ".join(p for p in parts if p)


def sync_students(students: list[Student]) -> None:
    """Rebuild the collection from the current contents of SQLite."""
    collection = get_collection()

    existing_ids = collection.get()["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)

    if not students:
        return

    collection.add(
        ids=[str(s.id) for s in students],
        documents=[_student_document(s) for s in students],
        metadatas=[{"student_id": s.id, "name": s.name} for s in students],
    )


def search_students(query: str, n_results: int = 5) -> list[dict]:
    """Semantic search -- returns [{student_id, name, document, distance}, ...]."""
    collection = get_collection()
    if collection.count() == 0:
        return []

    results = collection.query(query_texts=[query], n_results=n_results)

    hits = []
    for i in range(len(results["ids"][0])):
        hits.append(
            {
                "student_id": results["metadatas"][0][i]["student_id"],
                "name": results["metadatas"][0][i]["name"],
                "document": results["documents"][0][i],
                "distance": results["distances"][0][i],
            }
        )
    return hits
