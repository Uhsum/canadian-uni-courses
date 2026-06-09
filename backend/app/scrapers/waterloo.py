"""
Scraper for University of Waterloo course calendar.
Source: https://uwflow.com/api (public GraphQL — crowd-sourced course data)
"""
import httpx
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

UWFLOW_GQL = "https://uwflow.com/graphql"

QUERY = """
query GetAllCourses {
  course(limit: 5000, order_by: {code: asc}) {
    code
    name
    description
    prereqs
    coreqs
    antireqs
  }
}
"""


class WaterlooScraper(BaseScraper):
    name = "waterloo_courses"
    university_short = "Waterloo"
    delay = 1.0

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="Waterloo").first()
        if not uni:
            raise ValueError("Waterloo not found in DB — run seed first")

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                UWFLOW_GQL,
                json={"query": QUERY},
                headers={**self.HEADERS, "Content-Type": "application/json"},
            )
            resp.raise_for_status()
            courses = resp.json().get("data", {}).get("course", [])

        count = 0
        for c in courses:
            code = (c.get("code") or "").upper()
            name = (c.get("name") or "").strip()
            if not code or not name:
                continue

            import re
            level_match = re.search(r"(\d)", code)
            level = int(level_match.group(1)) * 100 if level_match else None

            existing = self.db.query(Course).filter_by(
                university_id=uni.id, code=code
            ).first()
            obj = existing or Course(university_id=uni.id, code=code)
            if not existing:
                self.db.add(obj)

            obj.name = name
            obj.description = c.get("description", "")
            obj.level = level
            obj.prerequisites_text = c.get("prereqs", "")
            obj.corequisites_text = c.get("coreqs", "")
            obj.exclusions_text = c.get("antireqs", "")
            obj.url = f"https://uwflow.com/course/{code.lower()}"
            count += 1

        self.db.commit()
        return count
