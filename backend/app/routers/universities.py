from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import University

router = APIRouter(prefix="/universities", tags=["universities"])


@router.get("/")
def list_universities(
    province: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(University)
    if province:
        q = q.filter(University.province.ilike(f"%{province}%"))
    unis = q.order_by(University.macleans_rank).all()
    return [_serialize_uni(u) for u in unis]


@router.get("/{uni_id}")
def get_university(uni_id: int, db: Session = Depends(get_db)):
    u = db.query(University).filter_by(id=uni_id).first()
    if not u:
        from fastapi import HTTPException
        raise HTTPException(404, "University not found")
    return _serialize_uni(u)


def _serialize_uni(u: University) -> dict:
    return {
        "id": u.id,
        "name": u.name,
        "short_name": u.short_name,
        "province": u.province,
        "city": u.city,
        "website": u.website,
        "established_year": u.established_year,
        "rankings": {
            "macleans": u.macleans_rank,
            "qs_world": u.qs_world_rank,
            "qs_canada": u.qs_canada_rank,
            "times_world": u.times_world_rank,
        },
        "admissions": {
            "acceptance_rate": u.overall_acceptance_rate,
            "international_acceptance_rate": u.international_acceptance_rate,
        },
        "tuition_cad": {
            "domestic_min": u.domestic_tuition_min,
            "domestic_max": u.domestic_tuition_max,
            "international_min": u.international_tuition_min,
            "international_max": u.international_tuition_max,
        },
    }
