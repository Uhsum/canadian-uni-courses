"""
Scraper for University of Guelph course catalogue.
Source: https://calendar.uoguelph.ca/undergraduate-calendar/course-descriptions/
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

BASE = "https://calendar.uoguelph.ca"
INDEX_URL = BASE + "/undergraduate-calendar/course-descriptions/"


class UGuelphScraper(BaseScraper):
    name = "uguelph_courses"
    university_short = "UGuelph"
    delay = 1.5

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="UGuelph").first()
        if not uni:
            raise ValueError("UGuelph not found in DB — run seed first")

        count = 0
        async with httpx.AsyncClient(timeout=30) as client:
            # Get full dept list
            idx_soup = await self.fetch(INDEX_URL, client)
            dept_hrefs = list(dict.fromkeys(
                a["href"]
                for a in idx_soup.select("a[href*='/course-descriptions/']")
                if a["href"].rstrip("/") != "/undergraduate-calendar/course-descriptions"
                and len(a["href"].rstrip("/").split("/")[-1]) > 0
            ))

            for href in dept_hrefs:
                url = href if href.startswith("http") else BASE + href
                try:
                    soup = await self.fetch(url, client)
                except Exception:
                    continue

                for block in soup.select(".courseblock"):
                    code_el = block.select_one(".detail-code strong, .detail-code")
                    title_el = block.select_one(".detail-title strong, .detail-title")
                    if not code_el or not title_el:
                        continue

                    code = code_el.get_text(strip=True)   # e.g. "ANSC*2210"
                    name = title_el.get_text(strip=True)

                    level_m = re.search(r"(\d)", code)
                    level = int(level_m.group(1)) * 100 if level_m else None

                    # Credits from hours or weight element
                    credits_el = block.select_one(".detail-credits, .detail-hours_html")
                    credits = None
                    if credits_el:
                        cm = re.search(r"[\d.]+", credits_el.get_text())
                        credits = float(cm.group()) if cm else None

                    # Description
                    desc_el = block.select_one(".courseblockdesc, .detail-description")
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
                    obj.credits = credits
                    obj.prerequisites_text = prereq_m.group(1).strip() if prereq_m else ""
                    obj.url = url
                    count += 1

        self.db.commit()
        return count
