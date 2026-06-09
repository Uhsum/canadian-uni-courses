from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Course

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/")
def list_courses(
    university_id: int | None = None,
    program_id: int | None = None,
    level: int | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Course)
    if university_id:
        q = q.filter(Course.university_id == university_id)
    if program_id:
        q = q.filter(Course.program_id == program_id)
    if level:
        q = q.filter(Course.level == level)
    if search:
        like = f"%{search}%"
        q = q.filter(
            Course.name.ilike(like) | Course.code.ilike(like) | Course.description.ilike(like)
        )
    return [_serialize_course(c) for c in q.order_by(Course.code).all()]


@router.get("/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    c = db.query(Course).filter_by(id=course_id).first()
    if not c:
        from fastapi import HTTPException
        raise HTTPException(404, "Course not found")
    result = _serialize_course(c)
    result["prerequisites"] = [
        {"id": p.id, "code": p.code, "name": p.name} for p in c.prerequisites
    ]
    return result


def _serialize_course(c: Course) -> dict:
    return {
        "id": c.id,
        "university_id": c.university_id,
        "university_name": c.university.name if c.university else None,
        "program_id": c.program_id,
        "code": c.code,
        "name": c.name,
        "description": c.description,
        "level": c.level,
        "credits": c.credits,
        "semester": c.semester,
        "url": c.url,
        "prerequisites_text": c.prerequisites_text,
        "corequisites_text": c.corequisites_text,
        "exclusions_text": c.exclusions_text,
    }
