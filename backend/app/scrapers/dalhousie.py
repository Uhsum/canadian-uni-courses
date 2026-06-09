"""
Scraper for Dalhousie University courses.
Strategy: scrape faculty/department pages that list course codes with names,
then pull descriptions from the Acalog entity pages.

Key departments covered: Biology, Marine Biology, Oceanography, Chemistry,
Computer Science, Psychology, Economics, Engineering, Environmental Science.
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

DAL = "https://www.dal.ca"
ACALOG = "http://academiccalendar.dal.ca"

# Pages that contain course code listings (confirmed static HTML)
FACULTY_PAGES = [
    # Biology & Marine Biology
    (DAL + "/faculty/science/biology/BiologyProgram/course-sillabi.html", "BIOL"),
    (DAL + "/faculty/science/biology/BiologyProgram/course-sillabi/Biology/marine-biology.html", "BIOL"),
    # Oceanography
    (DAL + "/faculty/science/oceanography.html", "OCEA"),
    # Chemistry
    (DAL + "/faculty/science/chemistry/undergraduate/courses.html", "CHEM"),
    # Computer Science
    (DAL + "/faculty/computerscience/undergraduate/courses.html", "CSCI"),
    # Psychology
    (DAL + "/faculty/science/psychology/undergrad/courses.html", "PSYO"),
    # Mathematics
    (DAL + "/faculty/science/math-stats/undergraduate/courses.html", "MATH"),
    # Environmental Science
    (DAL + "/faculty/science/earthsciences/programs/undergraduate/courses.html", "ENVS"),
    # Economics
    (DAL + "/faculty/management/economics/undergrad/courses.html", "ECON"),
    # Engineering
    (DAL + "/faculty/engineering/undergraduate/courses.html", "ENGN"),
    # Physics
    (DAL + "/faculty/science/physics/undergraduate/courses.html", "PHYS"),
]

# Also: scrape the Acalog entity pages directly for course descriptions
# Format: http://academiccalendar.dal.ca/Catalog/ViewCatalog.aspx?pageid=viewcatalog&entitytype=CID&entitycode=BIOL+1010


class DalhouisieScraper(BaseScraper):
    name = "dal_courses"
    university_short = "Dal"
    delay = 1.5

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="Dal").first()
        if not uni:
            raise ValueError("Dalhousie not found in DB — run seed first")

        count = 0
        found_codes: dict[str, dict] = {}  # code → {name, url}

        async with httpx.AsyncClient(timeout=30) as client:
            # Phase 1: collect course codes + names from faculty pages
            for page_url, dept_hint in FACULTY_PAGES:
                try:
                    soup = await self.fetch(page_url, client)
                except Exception:
                    continue

                text = soup.get_text("\n")
                # Match patterns: "BIOL 1010" or "BIOL1010" followed by course name
                for m in re.finditer(
                    r"([A-Z]{3,5})\s*(\d{4}[A-Z]?)\b", text
                ):
                    code = f"{m.group(1)} {m.group(2)}"
                    if code not in found_codes:
                        # Try to get name from nearby text
                        pos = m.end()
                        nearby = text[pos:pos+120].strip()
                        # Strip credit info "(3 credit hours)" from name
                        name_m = re.match(r"[\s\-–]+([A-Za-z][^(\n]{3,80})", nearby)
                        name = name_m.group(1).strip() if name_m else ""
                        found_codes[code] = {"name": name, "url": page_url}

            # Phase 2: try to get descriptions from Acalog entity pages for found codes
            for code, info in list(found_codes.items()):
                entity_url = (
                    ACALOG
                    + "/Catalog/ViewCatalog.aspx?pageid=viewcatalog"
                    f"&entitytype=CID&entitycode={code.replace(' ', '+')}"
                    "&catalogid=119"
                )
                desc = ""
                prereqs = ""
                try:
                    det_soup = await self.fetch(entity_url, client)
                    body = det_soup.get_text("\n")
                    # Extract description (everything after the code line)
                    code_pos = body.find(code)
                    if code_pos >= 0:
                        after = body[code_pos + len(code):code_pos + len(code) + 600]
                        desc_lines = [l.strip() for l in after.splitlines() if l.strip() and len(l.strip()) > 10]
                        desc = " ".join(desc_lines[:3])
                        prereq_m = re.search(r"Prerequisite[s]?[:\s]+([^.]+\.)", after, re.I)
                        prereqs = prereq_m.group(1).strip() if prereq_m else ""
                    # Also pull name if we didn't get one
                    if not info["name"]:
                        h2 = det_soup.find(["h1", "h2", "h3"])
                        if h2:
                            nt = re.sub(code, "", h2.get_text()).strip(" -–")
                            if nt:
                                info["name"] = nt[:200]
                except Exception:
                    pass

                if not info["name"]:
                    info["name"] = code  # fallback

                level_m = re.search(r"(\d)", code)
                level = int(level_m.group(1)) * 100 if level_m else None

                existing = self.db.query(Course).filter_by(
                    university_id=uni.id, code=code
                ).first()
                obj = existing or Course(university_id=uni.id, code=code)
                if not existing:
                    self.db.add(obj)
                obj.name = info["name"]
                obj.description = desc[:1000]
                obj.level = level
                obj.prerequisites_text = prereqs
                obj.url = entity_url
                count += 1

        self.db.commit()
        return count
