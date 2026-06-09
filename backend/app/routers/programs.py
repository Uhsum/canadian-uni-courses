from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Program, University

router = APIRouter(prefix="/programs", tags=["programs"])


@router.get("/")
def list_programs(
    university_id: int | None = None,
    field: str | None = None,
    degree_type: str | None = None,
    max_domestic_tuition: float | None = None,
    max_international_tuition: float | None = None,
    min_acceptance_rate: float | None = None,
    max_acceptance_rate: float | None = None,
    sort_by: str = Query("program_rank_national", enum=[
        "program_rank_national", "acceptance_rate", "domestic_tuition",
        "international_tuition", "typical_admission_average"
    ]),
    db: Session = Depends(get_db),
):
    q = db.query(Program)
    if university_id:
        q = q.filter(Program.university_id == university_id)
    if field:
        q = q.filter(Program.field.ilike(f"%{field}%"))
    if degree_type:
        q = q.filter(Program.degree_type.ilike(f"%{degree_type}%"))
    if max_domestic_tuition:
        q = q.filter(Program.domestic_tuition <= max_domestic_tuition)
    if max_international_tuition:
        q = q.filter(Program.international_tuition <= max_international_tuition)
    if min_acceptance_rate is not None:
        q = q.filter(Program.acceptance_rate >= min_acceptance_rate)
    if max_acceptance_rate is not None:
        q = q.filter(Program.acceptance_rate <= max_acceptance_rate)

    sort_col = getattr(Program, sort_by, Program.program_rank_national)
    q = q.order_by(sort_col)

    programs = q.all()
    return [_serialize_program(p) for p in programs]


@router.get("/{program_id}")
def get_program(program_id: int, db: Session = Depends(get_db)):
    p = db.query(Program).filter_by(id=program_id).first()
    if not p:
        from fastapi import HTTPException
        raise HTTPException(404, "Program not found")
    return _serialize_program(p)


def _serialize_program(p: Program) -> dict:
    return {
        "id": p.id,
        "university_id": p.university_id,
        "university_name": p.university.name if p.university else None,
        "university_short": p.university.short_name if p.university else None,
        "name": p.name,
        "faculty": p.faculty,
        "degree_type": p.degree_type,
        "field": p.field,
        "duration_years": p.duration_years,
        "url": p.url,
        "admissions": {
            "acceptance_rate": p.acceptance_rate,
            "min_admission_average": p.min_admission_average,
            "typical_admission_average": p.typical_admission_average,
            "required_courses": p.required_courses,
        },
        "tuition_cad": {
            "domestic": p.domestic_tuition,
            "international": p.international_tuition,
            "ancillary_fees": p.ancillary_fees,
        },
        "rankings": {
            "national": p.program_rank_national,
            "qs_subject": p.program_rank_qs_subject,
            "qs_subject_area": p.qs_subject_area,
        },
    }
