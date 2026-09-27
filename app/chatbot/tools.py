"""
LangGraph tools the chatbot can call to answer questions about students.
Each tool opens its own short-lived DB session so it can be called
independently of the request/response cycle that serves /chat.
"""
from langchain_core.tools import tool

from app.chatbot.vector_store import search_students
from app.core.database import SessionLocal
from app.crud import student as crud


@tool
def get_all_students() -> str:
    """Return a list of every student in the database (name, major, year, course)."""
    db = SessionLocal()
    try:
        students = crud.get_students(db, limit=1000)
        if not students:
            return "There are no students in the database."
        lines = [
            f"- {s.name} | major: {s.major or 'n/a'} | year: {s.year or 'n/a'} "
            f"| course: {s.enrolled_course or 'n/a'} | gpa: {s.gpa or 'n/a'}"
            for s in students
        ]
        return "\n".join(lines)
    finally:
        db.close()


@tool
def get_student_by_name(name: str) -> str:
    """Look up a student (or students) by exact or partial name match."""
    db = SessionLocal()
    try:
        matches = crud.get_student_by_name(db, name)
        if not matches:
            return f"No student found matching '{name}'."
        lines = [
            f"- {s.name} (id={s.id}) | major: {s.major or 'n/a'} | year: {s.year or 'n/a'} "
            f"| course: {s.enrolled_course or 'n/a'} | gpa: {s.gpa or 'n/a'}"
            for s in matches
        ]
        return "\n".join(lines)
    finally:
        db.close()


@tool
def search_students_by_meaning(query: str) -> str:
    """
    Semantic search over student profiles. Use this for fuzzy/conceptual
    questions (e.g. "who studies something related to quantum mechanics?")
    where an exact keyword match wouldn't work.
    """
    hits = search_students(query, n_results=5)
    if not hits:
        return "No matching students found."
    lines = [f"- {h['name']}: {h['document']}" for h in hits]
    return "\n".join(lines)


ALL_TOOLS = [get_all_students, get_student_by_name, search_students_by_meaning]
