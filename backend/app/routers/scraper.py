from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.scrapers.runner import run_scraper

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.post("/run/{university_short}")
def trigger_scraper(
    university_short: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    background_tasks.add_task(run_scraper, university_short, db)
    return {"status": "queued", "university": university_short}


@router.get("/status")
def scraper_status(db: Session = Depends(get_db)):
    from app.models.models import ScraperRun
    runs = db.query(ScraperRun).order_by(ScraperRun.started_at.desc()).limit(20).all()
    return [
        {
            "scraper": r.scraper_name,
            "university": r.university_short,
            "status": r.status,
            "records": r.records_upserted,
            "started": r.started_at,
            "finished": r.finished_at,
            "error": r.error_message,
        }
        for r in runs
    ]
