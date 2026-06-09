"""
Scraper for University of Toronto course calendar.
Source: https://artsci.utoronto.ca/course-search (public HTML)
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course, Program


class UofTScraper(BaseScraper):
    name = "uoft_courses"
    university_short = "UofT"
    # UofT exposes a JSON search API used by their course search UI
    SEARCH_URL = "https://api.artsci.utoronto.ca/search-v2/search"
    COURSE_URL = "https://api.artsci.utoronto.ca/search-v2/course/{code}"

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="UofT").first()
        if not uni:
            raise ValueError("UofT not found in DB — run seed first")

        count = 0
        async with httpx.AsyncClient(timeout=30) as client:
            # Paginate through all undergrad courses
            page = 0
            page_size = 100
            while True:
                resp = await client.get(
                    self.SEARCH_URL,
                    params={
                        "q": "*",
                        "fq": "section_code:LEC",
                        "start": page * page_size,
                        "rows": page_size,
                        "wt": "json",
                    },
                    headers=self.HEADERS,
                )
                if resp.status_code != 200:
                    break
                data = resp.json()
                docs = data.get("response", {}).get("docs", [])
                if not docs:
                    break

                for doc in docs:
                    count += self._upsert_course(uni, doc)

                page += 1
                if page * page_size >= data.get("response", {}).get("numFound", 0):
                    break

        self.db.commit()
        return count

    def _upsert_course(self, uni: University, doc: dict) -> int:
        code = doc.get("code", "").strip()
        name = doc.get("name", "").strip()
        if not code or not name:
            return 0

        # Extract year level from code (e.g. CSC1** → 100)
        level_match = re.search(r"[A-Z]+(\d)", code)
        level = int(level_match.group(1)) * 100 if level_match else None

        existing = self.db.query(Course).filter_by(
            university_id=uni.id, code=code
        ).first()

        if existing:
            obj = existing
        else:
            obj = Course(university_id=uni.id, code=code)
            self.db.add(obj)

        obj.name = name
        obj.description = doc.get("description", "")
        obj.level = level
        obj.credits = float(doc.get("credit_value", 0.5) or 0.5)
        obj.prerequisites_text = doc.get("prerequisites", "")
        obj.corequisites_text = doc.get("corequisites", "")
        obj.exclusions_text = doc.get("exclusions", "")
        obj.url = f"https://artsci.utoronto.ca/course/{code.lower()}"
        return 1
