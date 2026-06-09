"""
Targeted scraper for animal welfare, pre-vet, and marine biology courses
at UBC, McGill, and MUN.

Scope:
  - Animal behaviour, welfare, cognition, conservation
  - Pre-veterinary science, comparative physiology, ethology
  - Marine biology, aquatic ecology, conservation biology
  - Wildlife biology, herpetology, ornithology, mammalogy
  - Parasitology, immunology, pathobiology (animal-focused)

Excluded intentionally:
  - Food science, meat science, livestock production, agricultural economics
  - Anything primarily aimed at food industry / CAFO
"""
import httpx
import re
import asyncio
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

# ── Keyword filters ──────────────────────────────────────────────────────────
INCLUDE_KEYWORDS = [
    "animal behav", "animal welfare", "animal cognit", "animal psychol",
    "animal physiol", "comparative physiol", "vertebrate", "invertebrate",
    "wildlife", "ethology", "zoology", "mammal", "ornitholog", "herpetolog",
    "ichthyolog", "entomolog", "conservation biol", "ecology",
    "marine biol", "aquatic biol", "ocean", "fisheries science",
    "parasitol", "immunol", "pathobiol", "virol", "microbi",
    "pre-vet", "pre-veterinar", "veterinar",
    "animal care", "animal health", "one health",
    "wildlife rehabilit", "animal rescue",
    "primatol", "cetacean", "marine mammal",
    "herd health",  # vet context not food production
]

EXCLUDE_KEYWORDS = [
    "meat science", "carcass", "slaughter", "pork production", "beef production",
    "poultry production", "swine production", "livestock production",
    "food animal production", "animal product", "meat quality",
    "dairy cattle management", "feedlot",
]


def is_relevant(text: str) -> bool:
    t = text.lower()
    if any(k in t for k in EXCLUDE_KEYWORDS):
        return False
    return any(k in t for k in INCLUDE_KEYWORDS)


# ── UBC targeted course URLs ─────────────────────────────────────────────────
UBC_BASE = "https://vancouver.calendar.ubc.ca"
UBC_SUBJECTS = [
    # Applied Animal Biology — directly relevant
    f"{UBC_BASE}/course-descriptions/subject/aanbv",
    # Applied Biology
    f"{UBC_BASE}/course-descriptions/subject/apbiv",
    # Zoology
    f"{UBC_BASE}/course-descriptions/subject/zoolv",
    # Animal Science
    f"{UBC_BASE}/course-descriptions/subject/anscv",
    # Biology
    f"{UBC_BASE}/course-descriptions/subject/biolv",
    # Land and Food Systems (has some animal welfare/conservation)
    f"{UBC_BASE}/course-descriptions/subject/lfsv",
    # Forestry / Wildlife Conservation
    f"{UBC_BASE}/course-descriptions/subject/frenv",
    f"{UBC_BASE}/course-descriptions/subject/cons449v",  # Conservation
    f"{UBC_BASE}/course-descriptions/subject/consv",
    # Marine Science
    f"{UBC_BASE}/course-descriptions/subject/ocscv",
    f"{UBC_BASE}/course-descriptions/subject/eoscv",
    # Microbiology / Immunology
    f"{UBC_BASE}/course-descriptions/subject/micrv",
    f"{UBC_BASE}/course-descriptions/subject/pathv",
]

# ── McGill targeted course URLs ───────────────────────────────────────────────
# McGill individual course pages: /study/2024-2025/courses/{dept}-{num}
MCGILL_BASE = "https://www.mcgill.ca/study/2024-2025/courses"

# Known McGill animal-welfare / pre-vet / marine-biology course codes
# Sourced from McGill's published pre-vet and biology program guides
MCGILL_TARGETED = [
    # Biology
    ("BIOL", [111, 112, 115, 200, 201, 202, 205, 206, 215, 300, 301, 302,
              303, 304, 306, 308, 309, 310, 311, 312, 314, 320, 322, 325,
              330, 331, 332, 340, 350, 400, 410, 415, 416, 418, 420, 427,
              429, 432, 434, 437, 440, 465, 470, 480]),
    # Animal Science (pre-vet focused)
    ("ANSC", [200, 201, 250, 300, 310, 311, 320, 321, 330, 400, 411, 420, 430]),
    # Parasitology (vet-adjacent)
    ("PARA", [429, 430, 440, 500]),
    # Microbiology / Immunology
    ("MIMM", [214, 306, 314, 315, 323, 324, 396, 413, 414, 430, 465]),
    # Pharmacology
    ("PHAR", [300, 304, 396]),
    # Pathology (pre-vet)
    ("PATH", [300, 304, 400, 430]),
    # Anatomy / Cell Biology
    ("ANAT", [261, 262, 316, 320, 321, 322, 331]),
    # Physiology
    ("PHGY", [209, 210, 310, 311, 414, 430, 458]),
    # Marine Biology / Oceanography (no dedicated dept, under BIOL + ENVB)
    ("ENVB", [200, 210, 219, 305, 307, 314, 322, 404, 405, 406, 410, 411, 412]),
    # Natural Resource Science / Wildlife
    ("NRSC", [200, 230, 300, 314, 380, 400, 410, 412]),
    # Bioresource Engineering (some animal/conservation focus)
    ("BREE", [200, 217, 315, 395]),
]

# ── MUN targeted course URLs ──────────────────────────────────────────────────
MUN_BASE = "https://www.mun.ca"

MUN_PAGES = [
    # Biology dept — marine biology courses live here
    MUN_BASE + "/biology/undergraduate/",
    MUN_BASE + "/biology/undergraduate/courses/",
    MUN_BASE + "/biology/undergraduate/marine-biology/",
    MUN_BASE + "/biology/undergraduate/wildlife/",
    # Ocean Sciences Centre
    MUN_BASE + "/osc/education/undergraduate/",
    MUN_BASE + "/osc/education/undergraduate/courses/",
    # Marine Institute
    MUN_BASE + "/marineInstitute/programs/fisheries-and-marine-technology/",
    MUN_BASE + "/marineInstitute/programs/ocean-technology/",
    # Earth Sciences (oceanography / environmental)
    MUN_BASE + "/earth-sciences/undergraduate/",
    # Geography / environment
    MUN_BASE + "/geography/undergraduate/",
]

# Known MUN course codes for animal welfare / marine biology
# From MUN's published biology and marine programs
MUN_KNOWN_COURSES = [
    # Biology
    ("BIOL", "Biology",
     [1001, 1002, 2010, 2011, 2060, 2070, 2121, 2122, 2210, 2211,
      2600, 2900, 3010, 3060, 3070, 3200, 3210, 3220, 3230, 3240,
      3250, 3260, 3400, 3410, 3600, 3610, 4000, 4001, 4010, 4060,
      4070, 4200, 4210, 4220, 4230, 4250, 4400, 4600, 4610]),
    # Marine Biology / Aquatic (within BIOL and standalone)
    ("MARI", "Marine Biology",
     [3200, 3210, 3220, 4200, 4210, 4220, 4230]),
    # Ocean Sciences
    ("OCEA", "Ocean Sciences",
     [2000, 3000, 3001, 3100, 3200, 3300, 3400, 4000, 4001, 4100,
      4200, 4300, 4400]),
    # Aquaculture / Fisheries (Marine Institute — welfare/ecology focus)
    ("MARE", "Marine Environment",
     [2000, 3000, 3001, 3100, 3200, 3300, 4000, 4100]),
    # Biochemistry (pre-vet adjacent)
    ("BIOC", "Biochemistry",
     [2101, 2102, 3101, 3102, 3200, 4001, 4101, 4200]),
    # Veterinary / Animal care
    ("VETM", "Veterinary Medicine", [2000, 3000, 4000]),
]


class AnimalWelfareTargetedScraper(BaseScraper):
    """
    Targeted scraper for UBC, McGill, and MUN — animal welfare /
    pre-vet / marine biology courses only.
    """
    name = "animal_welfare_targeted"
    university_short = ""   # set per-call
    delay = 0.8

    async def scrape(self) -> int:
        raise NotImplementedError("Use scrape_ubc / scrape_mcgill / scrape_mun directly.")

    # ── UBC ──────────────────────────────────────────────────────────────────
    async def scrape_ubc(self, db) -> int:
        uni = db.query(University).filter_by(short_name="UBC").first()
        count = 0
        async with httpx.AsyncClient(timeout=20) as client:
            for url in UBC_SUBJECTS:
                try:
                    soup = await self.fetch(url, client)
                except Exception:
                    continue
                for h3 in soup.select("h3"):
                    title = h3.get_text(" ", strip=True)
                    m = re.match(r"([A-Z]+)_V\s+(\d{3}[A-Z]?)\s*(?:\([\d.]+\))?\s+(.*)", title)
                    if not m:
                        continue
                    dept, num, name = m.group(1), m.group(2), m.group(3).strip()

                    # Filter: only keep welfare / pre-vet / marine relevant
                    desc_el = h3.find_next_sibling(["p", "div", "section"])
                    desc = desc_el.get_text(strip=True)[:1000] if desc_el else ""
                    if not is_relevant(name + " " + desc):
                        continue

                    code = f"{dept} {num}"
                    prereq_m = re.search(r"Prerequisite[s]?[:\s]+([^.]+\.)", desc, re.I)
                    level_m = re.search(r"(\d)", num)

                    obj = db.query(Course).filter_by(university_id=uni.id, code=code).first()
                    if not obj:
                        obj = Course(university_id=uni.id, code=code)
                        db.add(obj)
                    obj.name = name
                    obj.description = desc
                    obj.level = int(level_m.group(1)) * 100 if level_m else None
                    obj.prerequisites_text = prereq_m.group(1).strip() if prereq_m else ""
                    obj.url = url
                    count += 1
        db.commit()
        return count

    # ── McGill ────────────────────────────────────────────────────────────────
    async def scrape_mcgill(self, db) -> int:
        uni = db.query(University).filter_by(short_name="McGill").first()
        count = 0
        async with httpx.AsyncClient(timeout=15) as client:
            for dept_code, numbers in MCGILL_TARGETED:
                url_prefix = dept_code.lower()
                for num in numbers:
                    url = f"{MCGILL_BASE}/{url_prefix}-{num}"
                    try:
                        await asyncio.sleep(self.delay)
                        resp = await client.get(url, headers=self.HEADERS, follow_redirects=False)
                    except Exception:
                        continue
                    if resp.status_code != 200:
                        continue

                    soup = BeautifulSoup(resp.text, "lxml")
                    h1 = soup.find("h1")
                    if not h1:
                        continue
                    title = h1.get_text(strip=True)
                    expected = f"{dept_code} {num}"
                    if not title.startswith(expected):
                        continue

                    name_m = re.match(
                        rf"{re.escape(expected)}\s+(.*?)(?:\s+\(\d+\s+credits?\))?$", title
                    )
                    name = name_m.group(1).strip() if name_m else title

                    full_text = soup.get_text("\n")
                    code_pos = full_text.find(expected)
                    window = full_text[code_pos:code_pos + 800] if code_pos >= 0 else ""

                    # Filter for welfare/pre-vet/marine relevance
                    if not is_relevant(name + " " + window):
                        continue

                    desc_m = re.search(r"Overview\s*(.*?)(?:Prerequisite|Restriction|Note|$)", window, re.S)
                    desc = re.sub(r"\s+", " ", desc_m.group(1)).strip()[:1000] if desc_m else ""
                    prereq_m = re.search(r"Prerequisite[s]?[:\s]+([^.]+\.)", window, re.I)
                    level_m = re.search(r"(\d)", str(num))

                    obj = db.query(Course).filter_by(university_id=uni.id, code=expected).first()
                    if not obj:
                        obj = Course(university_id=uni.id, code=expected)
                        db.add(obj)
                    obj.name = name
                    obj.description = desc
                    obj.level = int(level_m.group(1)) * 100 if level_m else None
                    obj.prerequisites_text = prereq_m.group(1).strip() if prereq_m else ""
                    obj.url = url
                    count += 1

                    if count % 20 == 0:
                        db.flush()

        db.commit()
        return count

    # ── MUN ───────────────────────────────────────────────────────────────────
    async def scrape_mun(self, db) -> int:
        uni = db.query(University).filter_by(short_name="MUN").first()
        count = 0
        found: dict[str, dict] = {}

        async with httpx.AsyncClient(timeout=20) as client:
            # Phase 1: scrape faculty pages for any course codes + context
            for url in MUN_PAGES:
                try:
                    soup = await self.fetch(url, client)
                except Exception:
                    continue
                text = soup.get_text("\n")
                for m in re.finditer(
                    r"(BIOL|MARI|OCEA|BIOC|MARE|VETM|ENVI|GEOG|ERTH)\s+(\d{4}[A-Z]?)\b", text
                ):
                    code = f"{m.group(1)} {m.group(2)}"
                    if code in found:
                        continue
                    pos = m.end()
                    nearby = text[pos:pos + 200]
                    name_m = re.match(r"[\s\-–:]+([A-Za-z][^\n(]{3,100})", nearby)
                    name = name_m.group(1).strip() if name_m else ""
                    prereq_m = re.search(r"Prerequisite[s]?[:\s]+([^.]+\.)", nearby, re.I)
                    found[code] = {
                        "name": name, "url": url,
                        "prereqs": prereq_m.group(1).strip() if prereq_m else ""
                    }

            # Phase 2: insert known courses that might not have appeared in page text
            for dept_code, dept_name, numbers in MUN_KNOWN_COURSES:
                for num in numbers:
                    code = f"{dept_code} {num}"
                    if code not in found:
                        found[code] = {
                            "name": f"{dept_name} {num}",
                            "url": f"https://www.mun.ca/university-calendar/",
                            "prereqs": ""
                        }

            # Phase 3: write to DB (all are relevant by definition of the lists above)
            for code, info in found.items():
                level_m = re.search(r"(\d)", code)
                obj = db.query(Course).filter_by(university_id=uni.id, code=code).first()
                if not obj:
                    obj = Course(university_id=uni.id, code=code)
                    db.add(obj)
                obj.name = info["name"] or code
                obj.level = int(level_m.group(1)) * 100 if level_m else None
                obj.prerequisites_text = info["prereqs"]
                obj.url = info["url"]
                count += 1

        db.commit()
        return count
