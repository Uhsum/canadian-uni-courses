"""
Scraper for McGill course calendar.
Source: https://www.mcgill.ca/study/courses (public HTML)
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

MCGILL_SEARCH = "https://www.mcgill.ca/study/2024-2025/courses/search"


class McGillScraper(BaseScraper):
    name = "mcgill_courses"
    university_short = "McGill"
    delay = 2.0

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="McGill").first()
        if not uni:
            raise ValueError("McGill not found in DB — run seed first")

        count = 0
        async with httpx.AsyncClient(timeout=30) as client:
            page = 0
            while True:
                url = f"{MCGILL_SEARCH}?page={page}"
                try:
                    soup = await self.fetch(url, client)
                except Exception:
                    break

                items = soup.select("div.views-row")
                if not items:
                    break

                for item in items:
                    title_el = item.select_one("h4 a, .field-content a")
                    if not title_el:
                        continue

                    full_title = title_el.get_text(strip=True)
                    # Format: "COMP 202 Foundations of Programming (3 credits)"
                    match = re.match(r"([A-Z]+\s+\d+[A-Z]?)\s+(.+?)(?:\s+\(\d+\s+credits?\))?$", full_title)
                    if not match:
                        continue

                    code = match.group(1).strip()
                    name = match.group(2).strip()
                    level_match = re.search(r"(\d)", code.split()[-1])
                    level = int(level_match.group(1)) * 100 if level_match else None

                    desc_el = item.select_one(".field-name-body, .views-field-body")
                    description = desc_el.get_text(strip=True) if desc_el else ""

                    existing = self.db.query(Course).filter_by(
                        university_id=uni.id, code=code
                    ).first()
                    obj = existing or Course(university_id=uni.id, code=code)
                    if not existing:
                        self.db.add(obj)

                    obj.name = name
                    obj.description = description
                    obj.level = level
                    obj.url = "https://www.mcgill.ca" + (title_el.get("href", "") or "")
                    count += 1

                page += 1
                if page > 50:  # safety cap
                    break

        self.db.commit()
        return count
