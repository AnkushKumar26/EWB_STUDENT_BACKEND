"""
Database operations for the Student model. Kept separate from the routes
so both the REST API and the chatbot tools can share the same logic.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


def create_student(db: Session, student: StudentCreate) -> Student:
    db_student = Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_student(db: Session, student_id: int) -> Optional[Student]:
    return db.get(Student, student_id)


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    return db.query(Student).filter(Student.email == email).first()


def get_student_by_name(db: Session, name: str) -> list[Student]:
    """Case-insensitive partial name match -- used by both the API and the chatbot."""
    return db.query(Student).filter(Student.name.ilike(f"%{name}%")).all()


def get_students(db: Session, skip: int = 0, limit: int = 100) -> list[Student]:
    return db.query(Student).offset(skip).limit(limit).all()


def update_student(
    db: Session, student_id: int, student_update: StudentUpdate
) -> Optional[Student]:
    db_student = get_student(db, student_id)
    if db_student is None:
        return None

    update_data = student_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_student, field, value)

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: int) -> bool:
    db_student = get_student(db, student_id)
    if db_student is None:
        return False

    db.delete(db_student)
    db.commit()
    return True
