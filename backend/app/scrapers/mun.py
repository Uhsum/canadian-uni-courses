"""
Scraper for Memorial University of Newfoundland (MUN).
Strategy: MUN's main calendar requires JavaScript, so we scrape
faculty/department course listing pages that are static HTML.

Key departments: Biology (BIOL), Marine Biology (BIOL/MARI),
Ocean Sciences (OCEA), Fisheries (FISH), Chemistry, Computer Science, etc.
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

MUN = "https://www.mun.ca"

# Faculty pages confirmed to have static course info
FACULTY_PAGES = [
    # Biology & Marine Biology (highest priority)
    MUN + "/biology/undergraduate/courses/",
    MUN + "/biology/undergraduate/marine-biology/",
    MUN + "/osc/education/undergraduate/",            # Ocean Sciences Centre
    MUN + "/marineInstitute/programs/",               # Marine Institute
    MUN + "/chemistry/undergraduate/courses/",
    MUN + "/computerscience/undergraduate/courses/",
    MUN + "/physics/undergraduate/courses/",
    MUN + "/math/undergraduate/courses/",
    MUN + "/psychology/undergraduate/",
    MUN + "/economics/undergraduate/",
    MUN + "/engineering/undergraduate/programs/",
    MUN + "/geography/undergraduate/",
    MUN + "/earth-sciences/undergraduate/",
]

# Known MUN course code prefixes for regex matching
MUN_CODES = [
    "BIOL", "MARI", "OCEA", "FISH", "BIOC", "CHEM", "COMP", "PHYS",
    "MATH", "STAT", "ENGI", "PSYC", "ECON", "GEOG", "ERTH", "ENVS",
    "OCSC", "AQUA", "NURS", "MEDS",
]
CODE_PATTERN = "|".join(MUN_CODES)


class MUNScraper(BaseScraper):
    name = "mun_courses"
    university_short = "MUN"
    delay = 1.5

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="MUN").first()
        if not uni:
            raise ValueError("MUN not found in DB — run seed first")

        count = 0
        found_codes: dict[str, dict] = {}

        async with httpx.AsyncClient(timeout=30) as client:
            for page_url in FACULTY_PAGES:
                try:
                    soup = await self.fetch(page_url, client)
                except Exception:
                    continue

                text = soup.get_text("\n")
                # Match MUN course codes e.g. "BIOL 1001" or "MARI 3200"
                for m in re.finditer(
                    rf"({CODE_PATTERN})\s+(\d{{4}}[A-Z]?)\b", text
                ):
                    code = f"{m.group(1)} {m.group(2)}"
                    if code in found_codes:
                        continue

                    # Grab nearby text for name
                    pos = m.end()
                    nearby = text[pos:pos + 150].strip()
                    name_m = re.match(r"[\s\-–]+([A-Za-z][^(\n]{3,100})", nearby)
                    name = name_m.group(1).strip() if name_m else ""

                    # Look for desc in surrounding lines
                    start = max(0, m.start() - 20)
                    window = text[start:pos + 400]
                    prereq_m = re.search(r"Prerequisite[s]?[:\s]+([^.]+\.)", window, re.I)

                    found_codes[code] = {
                        "name": name or code,
                        "url": page_url,
                        "prereqs": prereq_m.group(1).strip() if prereq_m else "",
                    }

                # Also check links that look like individual course pages
                for a in soup.select("a[href]"):
                    href = a.get("href", "")
                    link_text = a.get_text(strip=True)
                    cm = re.match(rf"({CODE_PATTERN})\s*(\d{{4}}[A-Z]?)", link_text)
                    if cm:
                        code = f"{cm.group(1)} {cm.group(2)}"
                        if code not in found_codes:
                            full_url = href if href.startswith("http") else MUN + href
                            found_codes[code] = {
                                "name": link_text[cm.end():].strip(" -–") or code,
                                "url": full_url,
                                "prereqs": "",
                            }

            # Write all collected courses to DB
            for code, info in found_codes.items():
                level_m = re.search(r"(\d)", code)
                level = int(level_m.group(1)) * 100 if level_m else None

                existing = self.db.query(Course).filter_by(
                    university_id=uni.id, code=code
                ).first()
                obj = existing or Course(university_id=uni.id, code=code)
                if not existing:
                    self.db.add(obj)
                obj.name = info["name"][:300]
                obj.level = level
                obj.prerequisites_text = info["prereqs"]
                obj.url = info["url"]
                count += 1

        self.db.commit()
        return count
