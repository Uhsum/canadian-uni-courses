"""
Seed data for 5 major Canadian universities.
Rankings from Maclean's 2024, QS World Rankings 2025.
Tuition from official university fee schedules (2024-25).
Acceptance rates from published admissions data.
"""
from sqlalchemy.orm import Session
from app.models.models import University, Program

UNIVERSITIES = [
    {
        "name": "University of Toronto",
        "short_name": "UofT",
        "province": "Ontario",
        "city": "Toronto",
        "website": "https://www.utoronto.ca",
        "established_year": 1827,
        "macleans_rank": 1,
        "qs_world_rank": 25,
        "qs_canada_rank": 1,
        "times_world_rank": 21,
        "overall_acceptance_rate": 0.43,
        "international_acceptance_rate": 0.38,
        "domestic_tuition_min": 6100.0,
        "domestic_tuition_max": 14800.0,
        "international_tuition_min": 44000.0,
        "international_tuition_max": 65000.0,
    },
    {
        "name": "University of British Columbia",
        "short_name": "UBC",
        "province": "British Columbia",
        "city": "Vancouver",
        "website": "https://www.ubc.ca",
        "established_year": 1908,
        "macleans_rank": 2,
        "qs_world_rank": 38,
        "qs_canada_rank": 2,
        "times_world_rank": 41,
        "overall_acceptance_rate": 0.52,
        "international_acceptance_rate": 0.46,
        "domestic_tuition_min": 5454.0,
        "domestic_tuition_max": 9000.0,
        "international_tuition_min": 38000.0,
        "international_tuition_max": 58000.0,
    },
    {
        "name": "McGill University",
        "short_name": "McGill",
        "province": "Quebec",
        "city": "Montreal",
        "website": "https://www.mcgill.ca",
        "established_year": 1821,
        "macleans_rank": 3,
        "qs_world_rank": 30,
        "qs_canada_rank": 3,
        "times_world_rank": 46,
        "overall_acceptance_rate": 0.47,
        "international_acceptance_rate": 0.41,
        "domestic_tuition_min": 2500.0,   # Quebec residents
        "domestic_tuition_max": 8800.0,   # out-of-province
        "international_tuition_min": 21000.0,
        "international_tuition_max": 35000.0,
    },
    {
        "name": "University of Waterloo",
        "short_name": "Waterloo",
        "province": "Ontario",
        "city": "Waterloo",
        "website": "https://uwaterloo.ca",
        "established_year": 1957,
        "macleans_rank": 7,
        "qs_world_rank": 154,
        "qs_canada_rank": 7,
        "times_world_rank": 201,
        "overall_acceptance_rate": 0.53,
        "international_acceptance_rate": 0.45,
        "domestic_tuition_min": 8000.0,
        "domestic_tuition_max": 18000.0,
        "international_tuition_min": 37000.0,
        "international_tuition_max": 58000.0,
    },
    {
        "name": "McMaster University",
        "short_name": "McMaster",
        "province": "Ontario",
        "city": "Hamilton",
        "website": "https://www.mcmaster.ca",
        "established_year": 1887,
        "macleans_rank": 5,
        "qs_world_rank": 189,
        "qs_canada_rank": 5,
        "times_world_rank": 101,
        "overall_acceptance_rate": 0.58,
        "international_acceptance_rate": 0.50,
        "domestic_tuition_min": 6500.0,
        "domestic_tuition_max": 12000.0,
        "international_tuition_min": 30000.0,
        "international_tuition_max": 48000.0,
    },
]

PROGRAMS = [
    # ── UofT ──────────────────────────────────────────────────────────────
    {
        "university_short": "UofT",
        "name": "Bachelor of Science – Computer Science",
        "faculty": "Faculty of Arts & Science",
        "degree_type": "BSc",
        "field": "Computer Science",
        "acceptance_rate": 0.30,
        "min_admission_average": 87.0,
        "typical_admission_average": 93.0,
        "required_courses": "Grade 12 English, MHF4U, MCV4U",
        "domestic_tuition": 14800.0,
        "international_tuition": 65000.0,
        "ancillary_fees": 1500.0,
        "program_rank_national": 1,
        "program_rank_qs_subject": 23,
        "qs_subject_area": "Computer Science & Information Systems",
        "url": "https://artsci.utoronto.ca/undergraduate/program-search/computer-science",
    },
    {
        "university_short": "UofT",
        "name": "Bachelor of Engineering – Electrical & Computer Engineering",
        "faculty": "Faculty of Applied Science & Engineering",
        "degree_type": "BEng",
        "field": "Electrical & Computer Engineering",
        "acceptance_rate": 0.25,
        "min_admission_average": 88.0,
        "typical_admission_average": 94.0,
        "required_courses": "Grade 12 English, MHF4U, MCV4U, SPH4U, SCH4U",
        "domestic_tuition": 14300.0,
        "international_tuition": 63000.0,
        "ancillary_fees": 1500.0,
        "program_rank_national": 2,
        "program_rank_qs_subject": 46,
        "qs_subject_area": "Engineering – Electrical & Electronic",
        "url": "https://engsci.utoronto.ca",
    },
    # ── UBC ───────────────────────────────────────────────────────────────
    {
        "university_short": "UBC",
        "name": "Bachelor of Science – Computer Science",
        "faculty": "Faculty of Science",
        "degree_type": "BSc",
        "field": "Computer Science",
        "acceptance_rate": 0.35,
        "min_admission_average": 85.0,
        "typical_admission_average": 91.0,
        "required_courses": "Grade 12 English, Pre-Calculus 12, Calculus 12 or Physics 12",
        "domestic_tuition": 5800.0,
        "international_tuition": 42000.0,
        "ancillary_fees": 1200.0,
        "program_rank_national": 2,
        "program_rank_qs_subject": 40,
        "qs_subject_area": "Computer Science & Information Systems",
        "url": "https://www.cs.ubc.ca/students/undergrad",
    },
    {
        "university_short": "UBC",
        "name": "Bachelor of Commerce",
        "faculty": "Sauder School of Business",
        "degree_type": "BCom",
        "field": "Business / Commerce",
        "acceptance_rate": 0.40,
        "min_admission_average": 83.0,
        "typical_admission_average": 89.0,
        "required_courses": "Grade 12 English, Pre-Calculus 12",
        "domestic_tuition": 6500.0,
        "international_tuition": 47000.0,
        "ancillary_fees": 1200.0,
        "program_rank_national": 3,
        "program_rank_qs_subject": 51,
        "qs_subject_area": "Business & Management Studies",
        "url": "https://mybcom.sauder.ubc.ca",
    },
    # ── McGill ────────────────────────────────────────────────────────────
    {
        "university_short": "McGill",
        "name": "Bachelor of Science – Computer Science",
        "faculty": "Faculty of Science",
        "degree_type": "BSc",
        "field": "Computer Science",
        "acceptance_rate": 0.38,
        "min_admission_average": 85.0,
        "typical_admission_average": 90.0,
        "required_courses": "High School Math including Calculus, Physics recommended",
        "domestic_tuition": 8800.0,
        "international_tuition": 28000.0,
        "ancillary_fees": 1100.0,
        "program_rank_national": 3,
        "program_rank_qs_subject": 55,
        "qs_subject_area": "Computer Science & Information Systems",
        "url": "https://www.cs.mcgill.ca/undergraduate",
    },
    {
        "university_short": "McGill",
        "name": "Bachelor of Arts – Economics",
        "faculty": "Faculty of Arts",
        "degree_type": "BA",
        "field": "Economics",
        "acceptance_rate": 0.45,
        "min_admission_average": 82.0,
        "typical_admission_average": 87.0,
        "required_courses": "High School Math, English",
        "domestic_tuition": 8800.0,
        "international_tuition": 25000.0,
        "ancillary_fees": 1100.0,
        "program_rank_national": 2,
        "program_rank_qs_subject": 38,
        "qs_subject_area": "Economics & Econometrics",
        "url": "https://www.mcgill.ca/economics/undergraduate",
    },
    # ── Waterloo ──────────────────────────────────────────────────────────
    {
        "university_short": "Waterloo",
        "name": "Bachelor of Computer Science",
        "faculty": "Faculty of Mathematics",
        "degree_type": "BCS",
        "field": "Computer Science",
        "acceptance_rate": 0.10,
        "min_admission_average": 90.0,
        "typical_admission_average": 96.0,
        "required_courses": "Grade 12 English, MHF4U, MCV4U",
        "domestic_tuition": 15600.0,
        "international_tuition": 58000.0,
        "ancillary_fees": 1400.0,
        "program_rank_national": 1,
        "program_rank_qs_subject": 30,
        "qs_subject_area": "Computer Science & Information Systems",
        "url": "https://cs.uwaterloo.ca/future-undergraduate-students",
    },
    {
        "university_short": "Waterloo",
        "name": "Bachelor of Software Engineering",
        "faculty": "Faculty of Engineering / Faculty of Mathematics",
        "degree_type": "BSE",
        "field": "Software Engineering",
        "acceptance_rate": 0.08,
        "min_admission_average": 90.0,
        "typical_admission_average": 96.0,
        "required_courses": "Grade 12 English, MHF4U, MCV4U, SPH4U",
        "domestic_tuition": 18000.0,
        "international_tuition": 58000.0,
        "ancillary_fees": 1400.0,
        "program_rank_national": 1,
        "program_rank_qs_subject": None,
        "qs_subject_area": None,
        "url": "https://uwaterloo.ca/future-students/programs/software-engineering",
    },
    # ── McMaster ──────────────────────────────────────────────────────────
    {
        "university_short": "McMaster",
        "name": "Bachelor of Engineering – Software Engineering",
        "faculty": "Faculty of Engineering",
        "degree_type": "BEng",
        "field": "Software Engineering",
        "acceptance_rate": 0.35,
        "min_admission_average": 83.0,
        "typical_admission_average": 89.0,
        "required_courses": "Grade 12 English, MHF4U, MCV4U, SPH4U",
        "domestic_tuition": 12000.0,
        "international_tuition": 42000.0,
        "ancillary_fees": 1300.0,
        "program_rank_national": 6,
        "program_rank_qs_subject": None,
        "qs_subject_area": None,
        "url": "https://www.eng.mcmaster.ca/future-students/programs/software-engineering",
    },
    {
        "university_short": "McMaster",
        "name": "Bachelor of Health Sciences",
        "faculty": "Faculty of Health Sciences",
        "degree_type": "BHSc",
        "field": "Health Sciences",
        "acceptance_rate": 0.05,
        "min_admission_average": 90.0,
        "typical_admission_average": 96.0,
        "required_courses": "Grade 12 English, Biology, Chemistry, one of Physics or Math",
        "domestic_tuition": 9500.0,
        "international_tuition": 34000.0,
        "ancillary_fees": 1300.0,
        "program_rank_national": 1,
        "program_rank_qs_subject": None,
        "qs_subject_area": "Medicine",
        "url": "https://bhsc.mcmaster.ca",
    },
]


def seed(db: Session):
    uni_map: dict[str, University] = {}

    for data in UNIVERSITIES:
        existing = db.query(University).filter_by(name=data["name"]).first()
        if not existing:
            uni = University(**data)
            db.add(uni)
            db.flush()
        else:
            for k, v in data.items():
                setattr(existing, k, v)
            uni = existing
        uni_map[data["short_name"]] = uni

    db.flush()

    for data in PROGRAMS:
        short = data.pop("university_short")
        uni = uni_map[short]
        existing = db.query(Program).filter_by(
            university_id=uni.id, name=data["name"]
        ).first()
        if not existing:
            prog = Program(university_id=uni.id, **data)
            db.add(prog)
        else:
            for k, v in data.items():
                setattr(existing, k, v)
        data["university_short"] = short  # restore for idempotency

    db.commit()
    print("Seed complete.")
