"""
Scraper for McGill University course catalogue.
Source: https://www.mcgill.ca/study/2024-2025/courses/<dept-code>
        e.g. /courses/comp, /courses/math, /courses/phys

McGill moved their full search to coursecatalogue.mcgill.ca (requires JS),
but individual department pages on the eCalendar still serve static HTML.
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

BASE = "https://www.mcgill.ca"

# Common McGill department codes (lowercase URL slugs)
DEPARTMENTS = [
    "acct", "anat", "anth", "arab", "arth", "biol", "chem", "chin",
    "comm", "comp", "econ", "edpe", "educ", "engl", "engr", "envr",
    "epib", "exer", "fina", "fren", "geog", "geol", "germ", "hist",
    "ital", "japn", "kine", "lang", "lasc", "law", "ling", "lsci",
    "math", "mech", "mgmt", "mimm", "mjhc", "mrkt", "mumt", "musi",
    "neur", "nsci", "nutr", "occh", "phar", "phil", "phgy", "phys",
    "poli", "psyc", "ptot", "relg", "rusa", "soci", "span", "stat",
    "surg", "swrk", "theo", "urbp",
]


class McGillScraper(BaseScraper):
    name = "mcgill_courses"
    university_short = "McGill"
    delay = 1.5

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="McGill").first()
        if not uni:
            raise ValueError("McGill not found in DB — run seed first")

        count = 0
        async with httpx.AsyncClient(timeout=30) as client:
            for dept in DEPARTMENTS:
                url = f"{BASE}/study/2024-2025/courses/{dept}"
                try:
                    soup = await self.fetch(url, client)
                except Exception:
                    continue

                # Courses appear as <div class="view-content"> containing
                # <li> or heading elements with title + body
                # Try to find course entries by looking for h3/h4 with codes
                course_blocks = soup.select(
                    "div.views-row, li.views-row, .course-block, article"
                )
                if not course_blocks:
                    # Fall back: parse text for patterns like "COMP 202 - Name"
                    text = soup.get_text("\n")
                    for m in re.finditer(
                        r"([A-Z]{2,5})\s+(\d{3}[A-Z]?)\s*[-–]\s*([^\n]{3,80})", text
                    ):
                        dept_code = m.group(1)
                        num = m.group(2)
                        name = m.group(3).strip()
                        code = f"{dept_code} {num}"
                        level_m = re.search(r"(\d)", num)
                        level = int(level_m.group(1)) * 100 if level_m else None

                        existing = self.db.query(Course).filter_by(
                            university_id=uni.id, code=code
                        ).first()
                        obj = existing or Course(university_id=uni.id, code=code)
                        if not existing:
                            self.db.add(obj)
                        obj.name = name
                        obj.level = level
                        obj.url = f"{BASE}/study/2024-2025/courses/{dept_code.lower()}-{num.lower()}"
                        count += 1
                    continue

                for block in course_blocks:
                    text = block.get_text("\n", strip=True)
                    lines = [l.strip() for l in text.splitlines() if l.strip()]
                    if not lines:
                        continue
                    m = re.match(
                        r"([A-Z]{2,5})\s+(\d{3}[A-Z]?)\s*[-–]\s*(.+?)(?:\s+\(\d+\s+credits?\))?$",
                        lines[0],
                    )
                    if not m:
                        continue
                    dept_code, num, name = m.group(1), m.group(2), m.group(3).strip()
                    code = f"{dept_code} {num}"
                    level_m = re.search(r"(\d)", num)
                    level = int(level_m.group(1)) * 100 if level_m else None

                    desc = " ".join(lines[1:3]) if len(lines) > 1 else ""
                    prereqs = ""
                    for line in lines:
                        if re.match(r"Prerequisite[s]?:", line, re.I):
                            prereqs = re.sub(r"Prerequisite[s]?:\s*", "", line, flags=re.I)

                    link = block.select_one("a")
                    course_url = BASE + link["href"] if link and link.get("href") else \
                        f"{BASE}/study/2024-2025/courses/{dept_code.lower()}-{num.lower()}"

                    existing = self.db.query(Course).filter_by(
                        university_id=uni.id, code=code
                    ).first()
                    obj = existing or Course(university_id=uni.id, code=code)
                    if not existing:
                        self.db.add(obj)
                    obj.name = name
                    obj.description = desc
                    obj.level = level
                    obj.prerequisites_text = prereqs
                    obj.url = course_url
                    count += 1

        self.db.commit()
        return count
