"""
Scraper for UBC Vancouver course calendar.
Source: https://vancouver.calendar.ubc.ca/course-descriptions/courses-subject
        Course pages at /course-descriptions/subject/{code}
        Courses appear as <h3> "CPSC_V 110 (4)  Course Name"
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

BASE = "https://vancouver.calendar.ubc.ca"
SUBJECTS_URL = BASE + "/course-descriptions/courses-subject"
SUBJECT_URL  = BASE + "/course-descriptions/subject/{slug}"


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
            # Get all subject slugs
            soup = await self.fetch(SUBJECTS_URL, client)
            subject_links = [
                a["href"]
                for a in soup.select("a[href*='/course-descriptions/subject/']")
                if "/course-descriptions/subject/" in a.get("href", "")
            ]
            subjects = list(dict.fromkeys(subject_links))

            for subj_url in subjects:
                full_url = subj_url if subj_url.startswith("http") else BASE + subj_url
                try:
                    subj_soup = await self.fetch(full_url, client)
                except Exception:
                    continue

                # Courses appear as <h3> with format:
                # "CPSC_V 110 (4)  Computation, Programs, and Programming"
                for h3 in subj_soup.select("h3"):
                    text = h3.get_text(" ", strip=True)
                    m = re.match(
                        r"([A-Z]+)_V\s+(\d{3}[A-Z]?)\s*(?:\([\d.]+\))?\s+(.*)",
                        text,
                    )
                    if not m:
                        continue
                    dept = m.group(1)
                    num = m.group(2)
                    name = m.group(3).strip()
                    code = f"{dept} {num}"
                    level_m = re.search(r"(\d)", num)
                    level = int(level_m.group(1)) * 100 if level_m else None

                    # Description from following <p> or <div>
                    desc_el = h3.find_next_sibling(["p", "div", "section"])
                    description = desc_el.get_text(strip=True)[:1000] if desc_el else ""
                    prereq_m = re.search(r"Prerequisite[s]?[:\s]+([^.]+\.)", description, re.I)

                    existing = self.db.query(Course).filter_by(
                        university_id=uni.id, code=code
                    ).first()
                    obj = existing or Course(university_id=uni.id, code=code)
                    if not existing:
                        self.db.add(obj)

                    obj.name = name
                    obj.description = description
                    obj.level = level
                    obj.prerequisites_text = prereq_m.group(1).strip() if prereq_m else ""
                    obj.url = full_url
                    count += 1

        self.db.commit()
        return count
