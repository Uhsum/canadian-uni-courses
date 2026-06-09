"""
Seed data for 13 major Canadian universities.
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
    {
        "name": "University of Alberta",
        "short_name": "UAlberta",
        "province": "Alberta",
        "city": "Edmonton",
        "website": "https://www.ualberta.ca",
        "established_year": 1908,
        "macleans_rank": 4,
        "qs_world_rank": 111,
        "qs_canada_rank": 4,
        "times_world_rank": 201,
        "overall_acceptance_rate": 0.58,
        "international_acceptance_rate": 0.50,
        "domestic_tuition_min": 5800.0,
        "domestic_tuition_max": 10500.0,
        "international_tuition_min": 26000.0,
        "international_tuition_max": 42000.0,
    },
    {
        "name": "Queen's University",
        "short_name": "Queens",
        "province": "Ontario",
        "city": "Kingston",
        "website": "https://www.queensu.ca",
        "established_year": 1841,
        "macleans_rank": 6,
        "qs_world_rank": 381,
        "qs_canada_rank": 8,
        "times_world_rank": 401,
        "overall_acceptance_rate": 0.42,
        "international_acceptance_rate": 0.35,
        "domestic_tuition_min": 6500.0,
        "domestic_tuition_max": 15000.0,
        "international_tuition_min": 37000.0,
        "international_tuition_max": 55000.0,
    },
    {
        "name": "Simon Fraser University",
        "short_name": "SFU",
        "province": "British Columbia",
        "city": "Burnaby",
        "website": "https://www.sfu.ca",
        "established_year": 1965,
        "macleans_rank": 8,
        "qs_world_rank": 323,
        "qs_canada_rank": 9,
        "times_world_rank": 351,
        "overall_acceptance_rate": 0.63,
        "international_acceptance_rate": 0.55,
        "domestic_tuition_min": 5800.0,
        "domestic_tuition_max": 8500.0,
        "international_tuition_min": 24000.0,
        "international_tuition_max": 38000.0,
    },
    {
        "name": "University of Western Ontario",
        "short_name": "Western",
        "province": "Ontario",
        "city": "London",
        "website": "https://www.uwo.ca",
        "established_year": 1878,
        "macleans_rank": 10,
        "qs_world_rank": 411,
        "qs_canada_rank": 11,
        "times_world_rank": 251,
        "overall_acceptance_rate": 0.57,
        "international_acceptance_rate": 0.48,
        "domestic_tuition_min": 7000.0,
        "domestic_tuition_max": 14000.0,
        "international_tuition_min": 30000.0,
        "international_tuition_max": 52000.0,
    },
    {
        "name": "University of Guelph",
        "short_name": "UGuelph",
        "province": "Ontario",
        "city": "Guelph",
        "website": "https://www.uoguelph.ca",
        "established_year": 1964,
        "macleans_rank": 11,
        "qs_world_rank": 601,
        "qs_canada_rank": 12,
        "times_world_rank": 601,
        "overall_acceptance_rate": 0.73,
        "international_acceptance_rate": 0.62,
        "domestic_tuition_min": 6500.0,
        "domestic_tuition_max": 10500.0,
        "international_tuition_min": 28000.0,
        "international_tuition_max": 40000.0,
    },
    {
        "name": "Dalhousie University",
        "short_name": "Dal",
        "province": "Nova Scotia",
        "city": "Halifax",
        "website": "https://www.dal.ca",
        "established_year": 1818,
        "macleans_rank": 12,
        "qs_world_rank": 501,
        "qs_canada_rank": 13,
        "times_world_rank": 401,
        "overall_acceptance_rate": 0.67,
        "international_acceptance_rate": 0.58,
        "domestic_tuition_min": 8800.0,
        "domestic_tuition_max": 13000.0,
        "international_tuition_min": 22000.0,
        "international_tuition_max": 35000.0,
    },
    {
        "name": "Memorial University of Newfoundland",
        "short_name": "MUN",
        "province": "Newfoundland and Labrador",
        "city": "St. John's",
        "website": "https://www.mun.ca",
        "established_year": 1925,
        "macleans_rank": 18,
        "qs_world_rank": 801,
        "qs_canada_rank": 19,
        "times_world_rank": 801,
        "overall_acceptance_rate": 0.78,
        "international_acceptance_rate": 0.70,
        "domestic_tuition_min": 2550.0,   # lowest in Canada
        "domestic_tuition_max": 5500.0,
        "international_tuition_min": 11000.0,
        "international_tuition_max": 22000.0,
    },
    {
        "name": "University of Ottawa",
        "short_name": "UOttawa",
        "province": "Ontario",
        "city": "Ottawa",
        "website": "https://www.uottawa.ca",
        "established_year": 1848,
        "macleans_rank": 9,
        "qs_world_rank": 400,
        "qs_canada_rank": 10,
        "times_world_rank": 401,
        "overall_acceptance_rate": 0.60,
        "international_acceptance_rate": 0.52,
        "domestic_tuition_min": 6500.0,
        "domestic_tuition_max": 11000.0,
        "international_tuition_min": 28000.0,
        "international_tuition_max": 44000.0,
    },
]

PROGRAMS = [
    # ── UofT ──────────────────────────────────────────────────────────────
    {"university_short":"UofT","name":"Bachelor of Science – Computer Science","faculty":"Faculty of Arts & Science","degree_type":"BSc","field":"Computer Science","acceptance_rate":0.30,"min_admission_average":87.0,"typical_admission_average":93.0,"domestic_tuition":14800.0,"international_tuition":65000.0,"program_rank_national":1,"url":"https://artsci.utoronto.ca/undergraduate/program-search/computer-science"},
    {"university_short":"UofT","name":"Bachelor of Engineering – Electrical & Computer Engineering","faculty":"Faculty of Applied Science & Engineering","degree_type":"BEng","field":"Electrical & Computer Engineering","acceptance_rate":0.25,"min_admission_average":88.0,"typical_admission_average":94.0,"domestic_tuition":14300.0,"international_tuition":63000.0,"program_rank_national":2,"url":"https://engsci.utoronto.ca"},
    {"university_short":"UofT","name":"Bachelor of Science – Biology","faculty":"Faculty of Arts & Science","degree_type":"BSc","field":"Biology","acceptance_rate":0.45,"min_admission_average":82.0,"typical_admission_average":88.0,"domestic_tuition":14800.0,"international_tuition":65000.0,"url":"https://artsci.utoronto.ca/undergraduate/program-search/biological-sciences"},
    {"university_short":"UofT","name":"Bachelor of Science – Ecology & Evolutionary Biology","faculty":"Faculty of Arts & Science","degree_type":"BSc","field":"Ecology","acceptance_rate":0.45,"min_admission_average":82.0,"typical_admission_average":88.0,"domestic_tuition":14800.0,"international_tuition":65000.0,"url":"https://eeb.utoronto.ca/undergraduate"},
    {"university_short":"UofT","name":"Bachelor of Commerce","faculty":"Rotman School of Management","degree_type":"BCom","field":"Business / Commerce","acceptance_rate":0.35,"min_admission_average":85.0,"typical_admission_average":91.0,"domestic_tuition":14800.0,"international_tuition":65000.0,"program_rank_national":1,"url":"https://www.rotman.utoronto.ca/Degrees/BCom"},
    {"university_short":"UofT","name":"Bachelor of Science – Statistics","faculty":"Faculty of Arts & Science","degree_type":"BSc","field":"Mathematics & Statistics","acceptance_rate":0.40,"min_admission_average":84.0,"typical_admission_average":90.0,"domestic_tuition":14800.0,"international_tuition":65000.0,"url":"https://www.statistics.utoronto.ca/undergraduate"},
    {"university_short":"UofT","name":"Bachelor of Science – Psychology","faculty":"Faculty of Arts & Science","degree_type":"BSc","field":"Psychology","acceptance_rate":0.48,"min_admission_average":81.0,"typical_admission_average":87.0,"domestic_tuition":14800.0,"international_tuition":65000.0,"url":"https://www.psychology.utoronto.ca/undergraduate"},
    {"university_short":"UofT","name":"Bachelor of Arts – Economics","faculty":"Faculty of Arts & Science","degree_type":"BA","field":"Economics","acceptance_rate":0.40,"min_admission_average":84.0,"typical_admission_average":90.0,"domestic_tuition":14800.0,"international_tuition":65000.0,"url":"https://www.economics.utoronto.ca/undergraduate"},
    # ── UBC ───────────────────────────────────────────────────────────────
    {"university_short":"UBC","name":"Bachelor of Science – Computer Science","faculty":"Faculty of Science","degree_type":"BSc","field":"Computer Science","acceptance_rate":0.35,"min_admission_average":85.0,"typical_admission_average":91.0,"domestic_tuition":5800.0,"international_tuition":42000.0,"program_rank_national":2,"url":"https://www.cs.ubc.ca/students/undergrad"},
    {"university_short":"UBC","name":"Bachelor of Commerce","faculty":"Sauder School of Business","degree_type":"BCom","field":"Business / Commerce","acceptance_rate":0.40,"min_admission_average":83.0,"typical_admission_average":89.0,"domestic_tuition":6500.0,"international_tuition":47000.0,"program_rank_national":3,"url":"https://mybcom.sauder.ubc.ca"},
    {"university_short":"UBC","name":"Bachelor of Science – Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Biology","acceptance_rate":0.50,"min_admission_average":80.0,"typical_admission_average":86.0,"domestic_tuition":5800.0,"international_tuition":42000.0,"url":"https://www.biology.ubc.ca/undergraduate"},
    {"university_short":"UBC","name":"Bachelor of Science – Applied Animal Biology","faculty":"Faculty of Land and Food Systems","degree_type":"BSc","field":"Animal Biology","acceptance_rate":0.60,"min_admission_average":78.0,"typical_admission_average":83.0,"domestic_tuition":5800.0,"international_tuition":38000.0,"url":"https://lfs.ubc.ca/undergraduate/applied-animal-biology"},
    {"university_short":"UBC","name":"Bachelor of Science – Marine Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Marine Biology","acceptance_rate":0.55,"min_admission_average":79.0,"typical_admission_average":85.0,"domestic_tuition":5800.0,"international_tuition":42000.0,"url":"https://www.zoology.ubc.ca/undergraduate"},
    {"university_short":"UBC","name":"Bachelor of Science – Conservation","faculty":"Faculty of Forestry","degree_type":"BSc","field":"Conservation","acceptance_rate":0.60,"min_admission_average":76.0,"typical_admission_average":82.0,"domestic_tuition":5800.0,"international_tuition":38000.0,"url":"https://forestry.ubc.ca/undergraduate/conservation"},
    {"university_short":"UBC","name":"Bachelor of Engineering – Civil Engineering","faculty":"Faculty of Applied Science","degree_type":"BEng","field":"Engineering","acceptance_rate":0.45,"min_admission_average":83.0,"typical_admission_average":89.0,"domestic_tuition":6500.0,"international_tuition":44000.0,"url":"https://civil.ubc.ca/undergraduate"},
    {"university_short":"UBC","name":"Bachelor of Science – Psychology","faculty":"Faculty of Arts","degree_type":"BSc","field":"Psychology","acceptance_rate":0.52,"min_admission_average":79.0,"typical_admission_average":85.0,"domestic_tuition":5800.0,"international_tuition":42000.0,"url":"https://psych.ubc.ca/undergraduate"},
    # ── McGill ────────────────────────────────────────────────────────────
    {"university_short":"McGill","name":"Bachelor of Science – Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Biology","acceptance_rate":0.42,"min_admission_average":84.0,"typical_admission_average":89.0,"domestic_tuition":8800.0,"international_tuition":28000.0,"url":"https://www.mcgill.ca/biology/undergraduate"},
    {"university_short":"McGill","name":"Bachelor of Science – Computer Science","faculty":"Faculty of Science","degree_type":"BSc","field":"Computer Science","acceptance_rate":0.38,"min_admission_average":85.0,"typical_admission_average":90.0,"domestic_tuition":8800.0,"international_tuition":28000.0,"program_rank_national":3,"url":"https://www.cs.mcgill.ca/undergraduate"},
    {"university_short":"McGill","name":"Bachelor of Arts – Economics","faculty":"Faculty of Arts","degree_type":"BA","field":"Economics","acceptance_rate":0.45,"min_admission_average":82.0,"typical_admission_average":87.0,"domestic_tuition":8800.0,"international_tuition":25000.0,"program_rank_national":2,"url":"https://www.mcgill.ca/economics/undergraduate"},
    {"university_short":"McGill","name":"Bachelor of Science – Microbiology & Immunology","faculty":"Faculty of Science","degree_type":"BSc","field":"Microbiology","acceptance_rate":0.44,"min_admission_average":83.0,"typical_admission_average":88.0,"domestic_tuition":8800.0,"international_tuition":28000.0,"url":"https://www.mcgill.ca/mimm/undergraduate"},
    {"university_short":"McGill","name":"Bachelor of Science – Environmental Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Environment","acceptance_rate":0.48,"min_admission_average":81.0,"typical_admission_average":86.0,"domestic_tuition":8800.0,"international_tuition":28000.0,"url":"https://www.mcgill.ca/nrs/undergraduate"},
    {"university_short":"McGill","name":"Bachelor of Science – Anatomy & Cell Biology","faculty":"Faculty of Medicine","degree_type":"BSc","field":"Health Sciences","acceptance_rate":0.40,"min_admission_average":85.0,"typical_admission_average":90.0,"domestic_tuition":8800.0,"international_tuition":28000.0,"url":"https://www.mcgill.ca/anatomy/undergraduate"},
    {"university_short":"McGill","name":"Bachelor of Commerce","faculty":"Desautels Faculty of Management","degree_type":"BCom","field":"Business / Commerce","acceptance_rate":0.35,"min_admission_average":85.0,"typical_admission_average":91.0,"domestic_tuition":8800.0,"international_tuition":28000.0,"program_rank_national":2,"url":"https://www.mcgill.ca/desautels/undergraduate"},
    {"university_short":"McGill","name":"Bachelor of Science – Physiology","faculty":"Faculty of Science","degree_type":"BSc","field":"Health Sciences","acceptance_rate":0.43,"min_admission_average":84.0,"typical_admission_average":89.0,"domestic_tuition":8800.0,"international_tuition":28000.0,"url":"https://www.mcgill.ca/physiology/undergraduate"},
    # ── Waterloo ──────────────────────────────────────────────────────────
    {"university_short":"Waterloo","name":"Bachelor of Computer Science","faculty":"Faculty of Mathematics","degree_type":"BCS","field":"Computer Science","acceptance_rate":0.10,"min_admission_average":90.0,"typical_admission_average":96.0,"domestic_tuition":15600.0,"international_tuition":58000.0,"program_rank_national":1,"url":"https://cs.uwaterloo.ca/future-undergraduate-students"},
    {"university_short":"Waterloo","name":"Bachelor of Software Engineering","faculty":"Faculty of Engineering","degree_type":"BEng","field":"Software Engineering","acceptance_rate":0.08,"min_admission_average":90.0,"typical_admission_average":96.0,"domestic_tuition":18000.0,"international_tuition":58000.0,"url":"https://uwaterloo.ca/future-students/programs/software-engineering"},
    {"university_short":"Waterloo","name":"Bachelor of Science – Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Biology","acceptance_rate":0.55,"min_admission_average":78.0,"typical_admission_average":84.0,"domestic_tuition":11000.0,"international_tuition":40000.0,"url":"https://uwaterloo.ca/future-students/programs/biology"},
    {"university_short":"Waterloo","name":"Bachelor of Mathematics – Statistics","faculty":"Faculty of Mathematics","degree_type":"BMath","field":"Mathematics & Statistics","acceptance_rate":0.30,"min_admission_average":85.0,"typical_admission_average":91.0,"domestic_tuition":13000.0,"international_tuition":48000.0,"url":"https://uwaterloo.ca/future-students/programs/statistics"},
    {"university_short":"Waterloo","name":"Bachelor of Applied Science – Mechanical Engineering","faculty":"Faculty of Engineering","degree_type":"BASc","field":"Engineering","acceptance_rate":0.35,"min_admission_average":85.0,"typical_admission_average":91.0,"domestic_tuition":17000.0,"international_tuition":57000.0,"url":"https://uwaterloo.ca/future-students/programs/mechanical-engineering"},
    {"university_short":"Waterloo","name":"Bachelor of Arts – Psychology","faculty":"Faculty of Arts","degree_type":"BA","field":"Psychology","acceptance_rate":0.55,"min_admission_average":78.0,"typical_admission_average":84.0,"domestic_tuition":10000.0,"international_tuition":37000.0,"url":"https://uwaterloo.ca/future-students/programs/psychology"},
    {"university_short":"Waterloo","name":"Bachelor of Environmental Studies – Environment & Business","faculty":"Faculty of Environment","degree_type":"BES","field":"Environment","acceptance_rate":0.60,"min_admission_average":76.0,"typical_admission_average":82.0,"domestic_tuition":10000.0,"international_tuition":37000.0,"url":"https://uwaterloo.ca/future-students/programs/environment-and-business"},
    # ── McMaster ──────────────────────────────────────────────────────────
    {"university_short":"McMaster","name":"Bachelor of Health Sciences","faculty":"Faculty of Health Sciences","degree_type":"BHSc","field":"Health Sciences","acceptance_rate":0.05,"min_admission_average":90.0,"typical_admission_average":96.0,"domestic_tuition":9500.0,"international_tuition":34000.0,"program_rank_national":1,"url":"https://bhsc.mcmaster.ca"},
    {"university_short":"McMaster","name":"Bachelor of Science – Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Biology","acceptance_rate":0.55,"min_admission_average":78.0,"typical_admission_average":84.0,"domestic_tuition":8500.0,"international_tuition":30000.0,"url":"https://www.science.mcmaster.ca/biology/undergraduate"},
    {"university_short":"McMaster","name":"Bachelor of Engineering – Software Engineering","faculty":"Faculty of Engineering","degree_type":"BEng","field":"Software Engineering","acceptance_rate":0.35,"min_admission_average":83.0,"typical_admission_average":89.0,"domestic_tuition":12000.0,"international_tuition":42000.0,"url":"https://www.eng.mcmaster.ca/future-students/programs/software-engineering"},
    {"university_short":"McMaster","name":"Bachelor of Commerce","faculty":"DeGroote School of Business","degree_type":"BCom","field":"Business / Commerce","acceptance_rate":0.40,"min_admission_average":82.0,"typical_admission_average":88.0,"domestic_tuition":9500.0,"international_tuition":34000.0,"url":"https://degroote.mcmaster.ca/undergraduate"},
    {"university_short":"McMaster","name":"Bachelor of Science – Psychology, Neuroscience & Behaviour","faculty":"Faculty of Science","degree_type":"BSc","field":"Psychology","acceptance_rate":0.40,"min_admission_average":83.0,"typical_admission_average":89.0,"domestic_tuition":8500.0,"international_tuition":30000.0,"url":"https://pnb.mcmaster.ca/undergraduate"},
    {"university_short":"McMaster","name":"Bachelor of Science – Chemical Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Health Sciences","acceptance_rate":0.45,"min_admission_average":82.0,"typical_admission_average":88.0,"domestic_tuition":8500.0,"international_tuition":30000.0,"url":"https://www.science.mcmaster.ca/biochemistry/undergraduate"},
    # ── UAlberta ──────────────────────────────────────────────────────────
    {"university_short":"UAlberta","name":"Bachelor of Science – Computing Science","faculty":"Faculty of Science","degree_type":"BSc","field":"Computer Science","acceptance_rate":0.55,"min_admission_average":80.0,"typical_admission_average":86.0,"domestic_tuition":7200.0,"international_tuition":28000.0,"program_rank_national":5,"url":"https://www.ualberta.ca/computing-science/undergraduate"},
    {"university_short":"UAlberta","name":"Bachelor of Science – Engineering","faculty":"Faculty of Engineering","degree_type":"BSc","field":"Engineering","acceptance_rate":0.50,"min_admission_average":78.0,"typical_admission_average":84.0,"domestic_tuition":9000.0,"international_tuition":32000.0,"url":"https://www.ualberta.ca/engineering/undergraduate"},
    {"university_short":"UAlberta","name":"Bachelor of Science – Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Biology","acceptance_rate":0.60,"min_admission_average":76.0,"typical_admission_average":82.0,"domestic_tuition":7200.0,"international_tuition":26000.0,"url":"https://www.ualberta.ca/science/programs/biology"},
    {"university_short":"UAlberta","name":"Doctor of Veterinary Medicine (DVM)","faculty":"Faculty of Veterinary Medicine","degree_type":"DVM","field":"Veterinary Medicine","acceptance_rate":0.12,"min_admission_average":78.0,"typical_admission_average":84.0,"domestic_tuition":22000.0,"international_tuition":65000.0,"url":"https://www.ualberta.ca/veterinary-medicine/dvm"},
    {"university_short":"UAlberta","name":"Bachelor of Commerce","faculty":"Alberta School of Business","degree_type":"BCom","field":"Business / Commerce","acceptance_rate":0.45,"min_admission_average":80.0,"typical_admission_average":86.0,"domestic_tuition":8500.0,"international_tuition":32000.0,"url":"https://business.ualberta.ca/undergraduate"},
    {"university_short":"UAlberta","name":"Bachelor of Science – Psychology","faculty":"Faculty of Arts","degree_type":"BSc","field":"Psychology","acceptance_rate":0.60,"min_admission_average":75.0,"typical_admission_average":81.0,"domestic_tuition":7200.0,"international_tuition":26000.0,"url":"https://www.ualberta.ca/arts/programs/psychology"},
    {"university_short":"UAlberta","name":"Bachelor of Science – Environmental & Conservation Sciences","faculty":"Faculty of Agricultural, Life & Environmental Sciences","degree_type":"BSc","field":"Environment","acceptance_rate":0.65,"min_admission_average":74.0,"typical_admission_average":80.0,"domestic_tuition":7200.0,"international_tuition":26000.0,"url":"https://www.ualberta.ca/ales/programs/environmental-conservation-sciences"},
    # ── Queen's ───────────────────────────────────────────────────────────
    {"university_short":"Queens","name":"Bachelor of Computing","faculty":"Faculty of Arts and Science","degree_type":"BComp","field":"Computer Science","acceptance_rate":0.40,"min_admission_average":83.0,"typical_admission_average":89.0,"domestic_tuition":7500.0,"international_tuition":45000.0,"program_rank_national":4,"url":"https://www.cs.queensu.ca/undergraduate"},
    {"university_short":"Queens","name":"Bachelor of Commerce","faculty":"Smith School of Business","degree_type":"BCom","field":"Business / Commerce","acceptance_rate":0.25,"min_admission_average":85.0,"typical_admission_average":92.0,"domestic_tuition":15000.0,"international_tuition":55000.0,"program_rank_national":2,"url":"https://smith.queensu.ca/undergraduate/bcom"},
    {"university_short":"Queens","name":"Bachelor of Science – Biology","faculty":"Faculty of Arts and Science","degree_type":"BSc","field":"Biology","acceptance_rate":0.50,"min_admission_average":79.0,"typical_admission_average":85.0,"domestic_tuition":7500.0,"international_tuition":45000.0,"url":"https://www.queensu.ca/biology/undergraduate"},
    {"university_short":"Queens","name":"Bachelor of Science – Life Sciences","faculty":"Faculty of Arts and Science","degree_type":"BSc","field":"Health Sciences","acceptance_rate":0.40,"min_admission_average":83.0,"typical_admission_average":89.0,"domestic_tuition":7500.0,"international_tuition":45000.0,"url":"https://www.queensu.ca/science/programs/life-sciences"},
    {"university_short":"Queens","name":"Bachelor of Arts – Psychology","faculty":"Faculty of Arts and Science","degree_type":"BA","field":"Psychology","acceptance_rate":0.48,"min_admission_average":80.0,"typical_admission_average":86.0,"domestic_tuition":7500.0,"international_tuition":45000.0,"url":"https://www.queensu.ca/psychology/undergraduate"},
    {"university_short":"Queens","name":"Bachelor of Applied Science – Engineering","faculty":"Faculty of Engineering and Applied Science","degree_type":"BASc","field":"Engineering","acceptance_rate":0.40,"min_admission_average":84.0,"typical_admission_average":90.0,"domestic_tuition":9000.0,"international_tuition":48000.0,"url":"https://engineering.queensu.ca/undergraduate"},
    # ── SFU ───────────────────────────────────────────────────────────────
    {"university_short":"SFU","name":"Bachelor of Science – Computing Science","faculty":"Faculty of Applied Sciences","degree_type":"BSc","field":"Computer Science","acceptance_rate":0.60,"min_admission_average":75.0,"typical_admission_average":83.0,"domestic_tuition":6200.0,"international_tuition":25000.0,"url":"https://www.sfu.ca/computing/prospective-students/undergraduate"},
    {"university_short":"SFU","name":"Bachelor of Science – Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Biology","acceptance_rate":0.65,"min_admission_average":72.0,"typical_admission_average":79.0,"domestic_tuition":5800.0,"international_tuition":24000.0,"url":"https://www.sfu.ca/biology/undergraduate"},
    {"university_short":"SFU","name":"Bachelor of Science – Marine Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Marine Biology","acceptance_rate":0.63,"min_admission_average":73.0,"typical_admission_average":80.0,"domestic_tuition":5800.0,"international_tuition":24000.0,"url":"https://www.sfu.ca/biology/undergraduate/programs/marine-biology"},
    {"university_short":"SFU","name":"Bachelor of Business Administration","faculty":"Beedie School of Business","degree_type":"BBA","field":"Business / Commerce","acceptance_rate":0.55,"min_admission_average":74.0,"typical_admission_average":81.0,"domestic_tuition":6500.0,"international_tuition":27000.0,"url":"https://beedie.sfu.ca/undergraduate"},
    {"university_short":"SFU","name":"Bachelor of Arts – Psychology","faculty":"Faculty of Arts and Social Sciences","degree_type":"BA","field":"Psychology","acceptance_rate":0.65,"min_admission_average":70.0,"typical_admission_average":77.0,"domestic_tuition":5800.0,"international_tuition":24000.0,"url":"https://www.sfu.ca/psychology/undergraduate"},
    {"university_short":"SFU","name":"Bachelor of Science – Environmental Science","faculty":"Faculty of Environment","degree_type":"BSc","field":"Environment","acceptance_rate":0.65,"min_admission_average":72.0,"typical_admission_average":79.0,"domestic_tuition":5800.0,"international_tuition":24000.0,"url":"https://www.sfu.ca/ensc/undergraduate"},
    # ── UOttawa ───────────────────────────────────────────────────────────
    {"university_short":"UOttawa","name":"Bachelor of Science – Computer Science","faculty":"Faculty of Engineering","degree_type":"BSc","field":"Computer Science","acceptance_rate":0.58,"min_admission_average":77.0,"typical_admission_average":84.0,"domestic_tuition":7500.0,"international_tuition":32000.0,"url":"https://www.uottawa.ca/faculty-engineering/undergraduate-studies/programs/computer-science"},
    {"university_short":"UOttawa","name":"Bachelor of Arts – Political Science","faculty":"Faculty of Social Sciences","degree_type":"BA","field":"Arts & Social Sciences","acceptance_rate":0.65,"min_admission_average":73.0,"typical_admission_average":80.0,"domestic_tuition":6500.0,"international_tuition":28000.0,"url":"https://www.uottawa.ca/faculty-social-sciences/political-studies"},
    {"university_short":"UOttawa","name":"Bachelor of Science – Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Biology","acceptance_rate":0.62,"min_admission_average":75.0,"typical_admission_average":81.0,"domestic_tuition":7200.0,"international_tuition":30000.0,"url":"https://science.uottawa.ca/bio/undergraduate"},
    {"university_short":"UOttawa","name":"Bachelor of Commerce","faculty":"Telfer School of Management","degree_type":"BCom","field":"Business / Commerce","acceptance_rate":0.55,"min_admission_average":76.0,"typical_admission_average":82.0,"domestic_tuition":7000.0,"international_tuition":30000.0,"url":"https://telfer.uottawa.ca/en/undergraduate"},
    {"university_short":"UOttawa","name":"Bachelor of Health Sciences","faculty":"Faculty of Health Sciences","degree_type":"BHSc","field":"Health Sciences","acceptance_rate":0.45,"min_admission_average":80.0,"typical_admission_average":86.0,"domestic_tuition":7500.0,"international_tuition":32000.0,"url":"https://health.uottawa.ca/undergraduate"},
    {"university_short":"UOttawa","name":"Bachelor of Engineering – Mechanical Engineering","faculty":"Faculty of Engineering","degree_type":"BEng","field":"Engineering","acceptance_rate":0.50,"min_admission_average":78.0,"typical_admission_average":85.0,"domestic_tuition":8000.0,"international_tuition":34000.0,"url":"https://www.uottawa.ca/faculty-engineering/undergraduate-studies/programs/mechanical-engineering"},
    # ── Western ───────────────────────────────────────────────────────────
    {"university_short":"Western","name":"Bachelor of Medical Sciences","faculty":"Schulich School of Medicine & Dentistry","degree_type":"BMSc","field":"Health Sciences","acceptance_rate":0.30,"min_admission_average":85.0,"typical_admission_average":92.0,"domestic_tuition":12000.0,"international_tuition":44000.0,"program_rank_national":5,"url":"https://www.schulich.uwo.ca/bmsc"},
    {"university_short":"Western","name":"Bachelor of Science – Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Biology","acceptance_rate":0.55,"min_admission_average":78.0,"typical_admission_average":85.0,"domestic_tuition":9000.0,"international_tuition":33000.0,"url":"https://www.uwo.ca/sci/programs/biology.html"},
    {"university_short":"Western","name":"Ivey HBA – Business Administration","faculty":"Ivey Business School","degree_type":"HBA","field":"Business / Commerce","acceptance_rate":0.25,"min_admission_average":85.0,"typical_admission_average":91.0,"domestic_tuition":14000.0,"international_tuition":52000.0,"program_rank_national":1,"url":"https://www.ivey.uwo.ca/hba"},
    {"university_short":"Western","name":"Bachelor of Engineering Science","faculty":"Faculty of Engineering","degree_type":"BESc","field":"Engineering","acceptance_rate":0.45,"min_admission_average":82.0,"typical_admission_average":88.0,"domestic_tuition":11000.0,"international_tuition":44000.0,"url":"https://www.eng.uwo.ca/undergraduate"},
    {"university_short":"Western","name":"Bachelor of Arts – Psychology","faculty":"Faculty of Social Science","degree_type":"BA","field":"Psychology","acceptance_rate":0.55,"min_admission_average":76.0,"typical_admission_average":83.0,"domestic_tuition":9000.0,"international_tuition":33000.0,"url":"https://www.psychology.uwo.ca/undergraduate"},
    {"university_short":"Western","name":"Bachelor of Science – Environmental Science","faculty":"Faculty of Science","degree_type":"BSc","field":"Environment","acceptance_rate":0.57,"min_admission_average":76.0,"typical_admission_average":82.0,"domestic_tuition":9000.0,"international_tuition":33000.0,"url":"https://www.uwo.ca/sci/programs/environment.html"},
    # ── UGuelph ───────────────────────────────────────────────────────────
    {"university_short":"UGuelph","name":"Bachelor of Science – Animal Biology","faculty":"College of Biological Science","degree_type":"BSc","field":"Animal Biology","acceptance_rate":0.70,"min_admission_average":75.0,"typical_admission_average":82.0,"domestic_tuition":8500.0,"international_tuition":30000.0,"program_rank_national":1,"url":"https://bsc.uoguelph.ca/programs/animal-biology"},
    {"university_short":"UGuelph","name":"Doctor of Veterinary Medicine (DVM)","faculty":"Ontario Veterinary College","degree_type":"DVM","field":"Veterinary Medicine","acceptance_rate":0.08,"min_admission_average":80.0,"typical_admission_average":87.0,"domestic_tuition":21000.0,"international_tuition":65000.0,"program_rank_national":1,"url":"https://ovc.uoguelph.ca/dvm"},
    {"university_short":"UGuelph","name":"Bachelor of Science – Wildlife Biology & Conservation","faculty":"College of Biological Science","degree_type":"BSc","field":"Wildlife Biology","acceptance_rate":0.68,"min_admission_average":74.0,"typical_admission_average":81.0,"domestic_tuition":8500.0,"international_tuition":30000.0,"program_rank_national":2,"url":"https://bsc.uoguelph.ca/programs/wildlife-biology-conservation"},
    {"university_short":"UGuelph","name":"Bachelor of Science – Biomedical Sciences","faculty":"Ontario Veterinary College","degree_type":"BSc","field":"Health Sciences","acceptance_rate":0.45,"min_admission_average":80.0,"typical_admission_average":87.0,"domestic_tuition":9500.0,"international_tuition":32000.0,"url":"https://ovc.uoguelph.ca/bsc-biomedical-sciences"},
    {"university_short":"UGuelph","name":"Bachelor of Science – Marine & Freshwater Biology","faculty":"College of Biological Science","degree_type":"BSc","field":"Marine Biology","acceptance_rate":0.68,"min_admission_average":74.0,"typical_admission_average":81.0,"domestic_tuition":8500.0,"international_tuition":30000.0,"url":"https://bsc.uoguelph.ca/programs/marine-freshwater-biology"},
    {"university_short":"UGuelph","name":"Bachelor of Commerce","faculty":"Gordon S. Lang School of Business","degree_type":"BCom","field":"Business / Commerce","acceptance_rate":0.50,"min_admission_average":79.0,"typical_admission_average":85.0,"domestic_tuition":9000.0,"international_tuition":32000.0,"url":"https://www.uoguelph.ca/lang"},
    {"university_short":"UGuelph","name":"Bachelor of Science – Environmental Sciences","faculty":"Ontario Agricultural College","degree_type":"BSc","field":"Environment","acceptance_rate":0.65,"min_admission_average":74.0,"typical_admission_average":80.0,"domestic_tuition":8500.0,"international_tuition":30000.0,"url":"https://www.uoguelph.ca/ses/undergraduate"},
    # ── Dalhousie ─────────────────────────────────────────────────────────
    {"university_short":"Dal","name":"Bachelor of Science – Marine Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Marine Biology","acceptance_rate":0.65,"min_admission_average":74.0,"typical_admission_average":82.0,"domestic_tuition":10500.0,"international_tuition":24000.0,"program_rank_national":1,"url":"https://www.dal.ca/faculty/science/biology/programs/marine-biology.html"},
    {"university_short":"Dal","name":"Bachelor of Science – Oceanography","faculty":"Faculty of Science","degree_type":"BSc","field":"Oceanography","acceptance_rate":0.68,"min_admission_average":73.0,"typical_admission_average":80.0,"domestic_tuition":10500.0,"international_tuition":24000.0,"url":"https://www.dal.ca/faculty/science/oceanography.html"},
    {"university_short":"Dal","name":"Bachelor of Science – Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Biology","acceptance_rate":0.67,"min_admission_average":72.0,"typical_admission_average":80.0,"domestic_tuition":10500.0,"international_tuition":24000.0,"url":"https://www.dal.ca/faculty/science/biology.html"},
    {"university_short":"Dal","name":"Bachelor of Science – Environmental Science","faculty":"Faculty of Science","degree_type":"BSc","field":"Environment","acceptance_rate":0.67,"min_admission_average":72.0,"typical_admission_average":79.0,"domestic_tuition":10500.0,"international_tuition":24000.0,"url":"https://www.dal.ca/faculty/science/environmental-science.html"},
    {"university_short":"Dal","name":"Bachelor of Commerce","faculty":"Rowe School of Business","degree_type":"BCom","field":"Business / Commerce","acceptance_rate":0.60,"min_admission_average":74.0,"typical_admission_average":80.0,"domestic_tuition":10500.0,"international_tuition":24000.0,"url":"https://www.dal.ca/faculty/management/rowe/undergraduate.html"},
    {"university_short":"Dal","name":"Bachelor of Science – Psychology","faculty":"Faculty of Arts and Social Sciences","degree_type":"BSc","field":"Psychology","acceptance_rate":0.67,"min_admission_average":72.0,"typical_admission_average":79.0,"domestic_tuition":10500.0,"international_tuition":24000.0,"url":"https://www.dal.ca/faculty/arts/psychology/undergraduate.html"},
    # ── MUN ───────────────────────────────────────────────────────────────
    {"university_short":"MUN","name":"Bachelor of Science – Marine Biology","faculty":"Faculty of Science","degree_type":"BSc","field":"Marine Biology","acceptance_rate":0.75,"min_admission_average":70.0,"typical_admission_average":76.0,"domestic_tuition":3500.0,"international_tuition":13000.0,"program_rank_national":2,"url":"https://www.mun.ca/science/undergraduate/marine-biology"},
    {"university_short":"MUN","name":"Bachelor of Science – Ocean Sciences","faculty":"Faculty of Science / Ocean Sciences Centre","degree_type":"BSc","field":"Oceanography","acceptance_rate":0.76,"min_admission_average":70.0,"typical_admission_average":75.0,"domestic_tuition":3500.0,"international_tuition":13000.0,"url":"https://www.mun.ca/osc/undergraduate"},
    {"university_short":"MUN","name":"Bachelor of Science – Biology (Aquatic Biology Concentration)","faculty":"Faculty of Science","degree_type":"BSc","field":"Aquatic Biology","acceptance_rate":0.77,"min_admission_average":70.0,"typical_admission_average":75.0,"domestic_tuition":3500.0,"international_tuition":13000.0,"url":"https://www.mun.ca/science/undergraduate/biology"},
    {"university_short":"MUN","name":"Bachelor of Science – Fisheries Science","faculty":"Marine Institute","degree_type":"BSc","field":"Fisheries Science","acceptance_rate":0.78,"min_admission_average":68.0,"typical_admission_average":74.0,"domestic_tuition":4200.0,"international_tuition":15000.0,"url":"https://www.mi.mun.ca/programs/fisheries-science"},
    {"university_short":"MUN","name":"Bachelor of Science – Computer Science","faculty":"Faculty of Science","degree_type":"BSc","field":"Computer Science","acceptance_rate":0.78,"min_admission_average":70.0,"typical_admission_average":76.0,"domestic_tuition":3500.0,"international_tuition":13000.0,"url":"https://www.mun.ca/computerscience/undergraduate"},
    {"university_short":"MUN","name":"Bachelor of Commerce","faculty":"Faculty of Business Administration","degree_type":"BCom","field":"Business / Commerce","acceptance_rate":0.78,"min_admission_average":68.0,"typical_admission_average":74.0,"domestic_tuition":3500.0,"international_tuition":13000.0,"url":"https://www.mun.ca/business/undergraduate"},
    {"university_short":"MUN","name":"Bachelor of Science – Psychology","faculty":"Faculty of Science","degree_type":"BSc","field":"Psychology","acceptance_rate":0.78,"min_admission_average":68.0,"typical_admission_average":74.0,"domestic_tuition":3500.0,"international_tuition":13000.0,"url":"https://www.mun.ca/psychology/undergraduate"},
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
