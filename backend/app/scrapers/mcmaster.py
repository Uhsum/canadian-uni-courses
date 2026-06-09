"""
Scraper for McMaster University course calendar.
Source: https://academiccalendars.romcmaster.ca (public HTML)
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

MCMASTER_CAL = "https://academiccalendars.romcmaster.ca/content.php?catoid=53&navoid=9953"


class McMasterScraper(BaseScraper):
    name = "mcmaster_courses"
    university_short = "McMaster"
    delay = 2.0

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="McMaster").first()
        if not uni:
            raise ValueError("McMaster not found in DB — run seed first")

        count = 0
        async with httpx.AsyncClient(timeout=30) as client:
            soup = await self.fetch(MCMASTER_CAL, client)

            # Courses appear as <td> with pattern "DEPT 1AA3 - Course Name"
            for td in soup.select("td.width"):
                text = td.get_text(strip=True)
                match = re.match(r"([A-Z]+\s+\d+[A-Z]+\d*)\s*[-–]\s*(.+)", text)
                if not match:
                    continue

                code = match.group(1).strip()
                name = match.group(2).strip()
                level_match = re.search(r"(\d)", code)
                level = int(level_match.group(1)) * 100 if level_match else None

                # Try to get detail URL
                link = td.select_one("a")
                detail_url = ""
                if link and link.get("href"):
                    href = link["href"]
                    if href.startswith("http"):
                        detail_url = href
                    else:
                        detail_url = "https://academiccalendars.romcmaster.ca/" + href

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

        self.db.commit()
        return count
