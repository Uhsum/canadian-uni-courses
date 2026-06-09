from sqlalchemy import (
    Column, Integer, String, Float, Text, ForeignKey, Table, DateTime
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

# Many-to-many: course prerequisites
course_prerequisites = Table(
    "course_prerequisites",
    Base.metadata,
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
    Column("prerequisite_id", Integer, ForeignKey("courses.id"), primary_key=True),
)


class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    short_name = Column(String(50))          # e.g. "UofT", "UBC"
    province = Column(String(100))
    city = Column(String(100))
    website = Column(String(500))
    established_year = Column(Integer)

    # Rankings
    macleans_rank = Column(Integer)          # Maclean's overall rank
    qs_world_rank = Column(Integer)          # QS World University Ranking
    qs_canada_rank = Column(Integer)
    times_world_rank = Column(Integer)       # Times Higher Education

    # Admissions (university-wide)
    overall_acceptance_rate = Column(Float)  # e.g. 0.43 = 43%
    international_acceptance_rate = Column(Float)

    # Fees (annual, CAD)
    domestic_tuition_min = Column(Float)
    domestic_tuition_max = Column(Float)
    international_tuition_min = Column(Float)
    international_tuition_max = Column(Float)

    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    programs = relationship("Program", back_populates="university")
    courses = relationship("Course", back_populates="university")


class Program(Base):
    """An undergraduate degree program (e.g. BSc Computer Science)."""
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    name = Column(String(255), nullable=False)        # e.g. "Bachelor of Computer Science"
    faculty = Column(String(255))                     # e.g. "Faculty of Science"
    degree_type = Column(String(50))                  # BSc, BA, BEng, BComm, etc.
    field = Column(String(255))                       # e.g. "Computer Science"
    duration_years = Column(Integer, default=4)
    url = Column(String(500))

    # Admissions
    acceptance_rate = Column(Float)
    min_admission_average = Column(Float)             # e.g. 85.0 (percent)
    typical_admission_average = Column(Float)         # median/typical admitted student
    required_courses = Column(Text)                   # text list of required HS courses

    # Fees (annual, CAD)
    domestic_tuition = Column(Float)
    international_tuition = Column(Float)
    ancillary_fees = Column(Float)                    # student union, health plan, etc.

    # Rankings
    program_rank_national = Column(Integer)
    program_rank_qs_subject = Column(Integer)         # QS subject ranking
    qs_subject_area = Column(String(255))

    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    university = relationship("University", back_populates="programs")
    courses = relationship("Course", back_populates="program")


class Course(Base):
    """An individual undergraduate course (e.g. CSC108H1)."""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)

    code = Column(String(50))              # e.g. "CSC108H1"
    name = Column(String(500), nullable=False)
    description = Column(Text)
    level = Column(Integer)               # 100, 200, 300, 400 (year level)
    credits = Column(Float)               # credit hours / units
    semester = Column(String(50))         # Fall, Winter, Summer, Year-long
    url = Column(String(500))

    # Prerequisites (text form for display, relation for graph queries)
    prerequisites_text = Column(Text)
    corequisites_text = Column(Text)
    exclusions_text = Column(Text)

    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    university = relationship("University", back_populates="courses")
    program = relationship("Program", back_populates="courses")
    prerequisites = relationship(
        "Course",
        secondary=course_prerequisites,
        primaryjoin=lambda: Course.id == course_prerequisites.c.course_id,
        secondaryjoin=lambda: Course.id == course_prerequisites.c.prerequisite_id,
        backref="required_by",
    )


class ScraperRun(Base):
    """Tracks when each scraper last ran and its status."""
    __tablename__ = "scraper_runs"

    id = Column(Integer, primary_key=True, index=True)
    scraper_name = Column(String(100))
    university_short = Column(String(50))
    status = Column(String(20))           # success, error, partial
    records_upserted = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
