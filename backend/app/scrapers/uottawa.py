"""
Scraper for University of Ottawa course catalogue.
Source: https://catalogue.uottawa.ca/en/courses/ (public HTML, Acalog CMS)
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

BASE = "https://catalogue.uottawa.ca"
LIST_URL = (
    BASE
    + "/content.php?catoid=11&navoid=1388"
    "&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1"
    "&filter%5B3%5D=1&filter%5Bcpage%5D={page}"
)


class UOttawaScraper(BaseScraper):
    name = "uottawa_courses"
    university_short = "UOttawa"
    delay = 1.5

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="UOttawa").first()
        if not uni:
            raise ValueError("UOttawa not found in DB — run seed first")

        # Find the right catoid/navoid dynamically from the catalogue index
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                soup = await self.fetch(f"{BASE}/en/courses/", client)
            except Exception:
                try:
                    soup = await self.fetch(f"{BASE}/index.php", client)
                except Exception:
                    return 0

            # Find course listing link
            course_link = soup.select_one("a[href*=navoid]")
            if course_link:
                href = course_link.get("href", "")
                catoid_m = re.search(r"catoid=(\d+)", href)
                navoid_m = re.search(r"navoid=(\d+)", href)
                if catoid_m and navoid_m:
                    catoid = catoid_m.group(1)
                    navoid = navoid_m.group(1)
                    list_tpl = (
                        f"{BASE}/content.php?catoid={catoid}&navoid={navoid}"
                        "&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1"
                        "&filter%5B3%5D=1&filter%5Bcpage%5D={{page}}"
                    )
                else:
                    list_tpl = LIST_URL
            else:
                list_tpl = LIST_URL

            count = 0
            page = 1
            while True:
                try:
                    pg_soup = await self.fetch(list_tpl.format(page=page), client)
                except Exception:
                    break

                links = pg_soup.select("a[href*=preview_course_nopop], a[href*=coid]")
                if not links:
                    break

                for link in links:
                    text = link.get_text(strip=True)
                    m = re.match(r"([A-Z]{2,6}\s*\d{4}[A-Z]?)\s*[-–]\s*(.+)", text)
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

                pager = pg_soup.select(".pager a, .pager-item a")
                has_next = any(f"cpage%5D={page+1}" in a.get("href", "") for a in pager)
                if not has_next and page > 1:
                    break
                page += 1
                if page > 150:
                    break

        self.db.commit()
        return count
