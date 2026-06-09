"""
Scraper for UBC course calendar.
Source: https://www.calendar.ubc.ca/vancouver/courses.cfm
        Static HTML A-Z department listing, no JS required.
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

BASE = "https://www.calendar.ubc.ca/vancouver"
# Each letter page lists all departments starting with that letter
ALPHA_URL = BASE + "/courses.cfm?page={letter}"
# Department course page
DEPT_URL = BASE + "/courses.cfm?page=all&dept={code}"


class UBCScraper(BaseScraper):
    name = "ubc_courses"
    university_short = "UBC"
    delay = 1.5

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="UBC").first()
        if not uni:
            raise ValueError("UBC not found in DB — run seed first")

        count = 0
        async with httpx.AsyncClient(timeout=30) as client:
            # 1. Collect all department codes from the A-Z index
            dept_codes = set()
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                try:
                    soup = await self.fetch(ALPHA_URL.format(letter=letter), client)
                except Exception:
                    continue
                for a in soup.select("a[href*='dept=']"):
                    href = a.get("href", "")
                    m = re.search(r"dept=([A-Z]+)", href)
                    if m:
                        dept_codes.add(m.group(1))

            # 2. For each department, scrape the course list
            for dept in sorted(dept_codes):
                try:
                    soup = await self.fetch(DEPT_URL.format(code=dept), client)
                except Exception:
                    continue

                # UBC calendar uses <dt> for course title, <dd> for description
                for dt in soup.select("dt"):
                    title = dt.get_text(strip=True)
                    # Format: "CPSC 110 (4) Computation, Programs, and Programming"
                    m = re.match(
                        r"([A-Z]+)\s+(\d{3}[A-Z]?)\s*(?:\([^)]+\))?\s*[-–]?\s*(.+)",
                        title,
                    )
                    if not m:
                        continue
                    dept_code = m.group(1)
                    num = m.group(2)
                    name = m.group(3).strip()
                    code = f"{dept_code} {num}"
                    level_m = re.search(r"(\d)", num)
                    level = int(level_m.group(1)) * 100 if level_m else None

                    # Description from following <dd>
                    dd = dt.find_next_sibling("dd")
                    description = dd.get_text(strip=True) if dd else ""

                    # Prereqs from description
                    prereq_m = re.search(r"Prerequisite[s]?[:\s]+([^.]+\.)", description, re.I)
                    prereqs = prereq_m.group(1).strip() if prereq_m else ""

                    existing = self.db.query(Course).filter_by(
                        university_id=uni.id, code=code
                    ).first()
                    obj = existing or Course(university_id=uni.id, code=code)
                    if not existing:
                        self.db.add(obj)

                    obj.name = name
                    obj.description = description[:1000]
                    obj.level = level
                    obj.prerequisites_text = prereqs
                    obj.url = DEPT_URL.format(code=dept)
                    count += 1

        self.db.commit()
        return count
