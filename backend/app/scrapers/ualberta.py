"""
Scraper for University of Alberta course catalogue.
Source: https://apps.ualberta.ca/catalogue/course (public JSON API)
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

# UAlberta exposes a public course catalogue API
SUBJECTS_URL = "https://apps.ualberta.ca/catalogue/course"
SUBJECT_URL  = "https://apps.ualberta.ca/catalogue/course/{subject}"


class UAlbertaScraper(BaseScraper):
    name = "ualberta_courses"
    university_short = "UAlberta"
    delay = 1.0

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="UAlberta").first()
        if not uni:
            raise ValueError("UAlberta not found in DB — run seed first")

        count = 0
        async with httpx.AsyncClient(timeout=30) as client:
            # Get all subject codes from the catalogue index page
            soup = await self.fetch(SUBJECTS_URL, client)
            subject_links = soup.select("a[href*='/catalogue/course/']")
            subjects = list({
                a["href"].split("/catalogue/course/")[-1].strip("/").upper()
                for a in subject_links
                if "/catalogue/course/" in a.get("href", "")
                and len(a["href"].split("/catalogue/course/")[-1].strip("/")) <= 6
            })

            for subj in sorted(subjects):
                try:
                    subj_soup = await self.fetch(SUBJECT_URL.format(subject=subj), client)
                except Exception:
                    continue

                # Each course is in a card/section with heading like "CMPUT 101"
                for heading in subj_soup.select("h3, h4, .course-title"):
                    text = heading.get_text(strip=True)
                    m = re.match(r"([A-Z]+)\s+(\d{3}[A-Z]?)\s*[-–]?\s*(.*)", text)
                    if not m:
                        continue
                    dept, num, name = m.group(1), m.group(2), m.group(3).strip()
                    if not name:
                        # name might be in next sibling
                        sib = heading.find_next_sibling()
                        name = sib.get_text(strip=True)[:200] if sib else ""
                    code = f"{dept} {num}"
                    level_m = re.search(r"(\d)", num)
                    level = int(level_m.group(1)) * 100 if level_m else None

                    # Description from following paragraph
                    desc_el = heading.find_next_sibling("p")
                    description = desc_el.get_text(strip=True)[:1000] if desc_el else ""
                    prereq_m = re.search(r"Prerequisite[s]?[:\s]+([^.]+\.)", description, re.I)
                    prereqs = prereq_m.group(1).strip() if prereq_m else ""

                    existing = self.db.query(Course).filter_by(
                        university_id=uni.id, code=code
                    ).first()
                    obj = existing or Course(university_id=uni.id, code=code)
                    if not existing:
                        self.db.add(obj)

                    obj.name = name
                    obj.description = description
                    obj.level = level
                    obj.prerequisites_text = prereqs
                    obj.url = SUBJECT_URL.format(subject=subj)
                    count += 1

        self.db.commit()
        return count
