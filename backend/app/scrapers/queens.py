"""
Scraper for Queen's University course calendar.
Source: https://www.queensu.ca/academic-calendar/arts-science/course-descriptions/
        Static HTML, organized by department.
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

BASE = "https://www.queensu.ca/academic-calendar"
INDEX = BASE + "/arts-science/course-descriptions/"


class QueensScraper(BaseScraper):
    name = "queens_courses"
    university_short = "Queens"
    delay = 1.5

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="Queens").first()
        if not uni:
            raise ValueError("Queen's not found in DB — run seed first")

        count = 0
        async with httpx.AsyncClient(timeout=30) as client:
            # Get list of department pages
            try:
                soup = await self.fetch(INDEX, client)
            except Exception:
                return 0

            dept_links = [
                a["href"] for a in soup.select("a[href]")
                if "/course-descriptions/" in a.get("href", "")
                and a["href"] != INDEX
                and not a["href"].endswith("/course-descriptions/")
            ]

            for href in dept_links:
                url = href if href.startswith("http") else BASE + href
                try:
                    dept_soup = await self.fetch(url, client)
                except Exception:
                    continue

                # Queen's course format: "CISC 101 – Computing" as headings
                # or within definition lists
                for el in dept_soup.select("h3, h4, dt, .course-code"):
                    text = el.get_text(strip=True)
                    m = re.match(r"([A-Z]+)\s+(\d{3}[A-Z]?(?:\.\d+)?)\s*[-–]\s*(.+)", text)
                    if not m:
                        continue
                    dept_code, num, name = m.group(1), m.group(2), m.group(3).strip()
                    code = f"{dept_code} {num}"
                    level_m = re.search(r"(\d)", num)
                    level = int(level_m.group(1)) * 100 if level_m else None

                    # Description from sibling or next paragraph
                    desc_el = el.find_next_sibling(["p", "dd", "div"])
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
                    obj.url = url
                    count += 1

        self.db.commit()
        return count
