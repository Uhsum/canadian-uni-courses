from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
from app.db.seed import seed
from app.db.database import SessionLocal
from app.routers import universities, programs, courses, scraper

Base.metadata.create_all(bind=engine)

# Seed on startup
with SessionLocal() as db:
    seed(db)

app = FastAPI(
    title="Canadian University Courses API",
    description="Undergraduate courses, programs, rankings, fees and admissions for Canadian universities.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(universities.router)
app.include_router(programs.router)
app.include_router(courses.router)
app.include_router(scraper.router)


@app.get("/")
def root():
    return {"message": "Canadian University Courses API", "docs": "/docs"}
