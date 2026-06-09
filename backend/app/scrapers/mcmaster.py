"""
Scraper for McMaster University course calendar.
Source: Acalog CMS at https://academiccalendars.romcmaster.ca
        Uses the paginated course listings (catoid=53, navoid=10775).
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

BASE = "https://academiccalendars.romcmaster.ca"
LIST_URL = (
    BASE
    + "/content.php?catoid=53&catoid=53&navoid=10775"
    "&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1"
    "&filter%5B3%5D=1&filter%5Bcpage%5D={page}"
)
DETAIL_URL = BASE + "/{path}"


class McMasterScraper(BaseScraper):
    name = "mcmaster_courses"
    university_short = "McMaster"
    delay = 1.5

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="McMaster").first()
        if not uni:
            raise ValueError("McMaster not found in DB — run seed first")

        count = 0
        async with httpx.AsyncClient(timeout=30) as client:
            page = 1
            while True:
                try:
                    soup = await self.fetch(LIST_URL.format(page=page), client)
                except Exception:
                    break

                links = soup.select("a[href*=preview_course_nopop], a[href*=coid]")
                if not links:
                    break

                for link in links:
                    text = link.get_text(strip=True)
                    # Format: "DEPT 1AA3 - Course Name"
                    m = re.match(r"([A-Z\s]+?\d+[A-Z0-9]+)\s*[-–]\s*(.+)", text)
                    if not m:
                        continue

                    code = m.group(1).strip()
                    name = m.group(2).strip()
                    level_m = re.search(r"(\d)", code)
                    level = int(level_m.group(1)) * 100 if level_m else None
                    href = link.get("href", "")
                    detail_url = BASE + "/" + href if not href.startswith("http") else href

                    existing = self.db.query(Course).filter_by(
                        university_id=uni.id, code=code
                    ).first()
                    obj = existing or Course(university_id=uni.id, code=code)
                    if not existing:
                        self.db.add(obj)

                    obj.name = name
                    obj.level = level
                    obj.url = detail_url
                    count += 1

                # Check if next page exists
                pager = soup.select(".pager a, .pager-item a")
                has_next = any(f"cpage%5D={page+1}" in a.get("href", "") for a in pager)
                if not has_next and page > 1:
                    break
                page += 1
                if page > 100:  # ~10,000 courses max
                    break

        self.db.commit()
        return count
