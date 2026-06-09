"""
Scraper for Simon Fraser University course catalogue.
Source: http://www.sfu.ca/students/calendar/2024/fall/courses.html
        SFU exposes a public JSON course API used by their calendar site.
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

# SFU course outlines API (public, no auth required)
SFU_DEPTS_URL = "https://www.sfu.ca/bin/wcm/course-outlines?{term}/courses"
SFU_COURSES_URL = "https://www.sfu.ca/bin/wcm/course-outlines?{term}/{dept}/courses"
TERM = "2024/fall"

SFU_CALENDAR_URL = "https://www.sfu.ca/students/calendar/2024/fall/courses/{dept}.html"


class SFUScraper(BaseScraper):
    name = "sfu_courses"
    university_short = "SFU"
    delay = 1.0

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="SFU").first()
        if not uni:
            raise ValueError("SFU not found in DB — run seed first")

        count = 0
        async with httpx.AsyncClient(timeout=30) as client:
            # Get list of departments from the SFU outlines API
            depts_url = f"https://www.sfu.ca/bin/wcm/course-outlines?{TERM}/courses"
            try:
                resp = await client.get(depts_url, headers=self.HEADERS, timeout=20)
                depts = resp.json() if resp.status_code == 200 else []
            except Exception:
                depts = []

            if not depts:
                # Fall back to calendar HTML index
                try:
                    soup = await self.fetch(
                        "https://www.sfu.ca/students/calendar/2024/fall/courses.html", client
                    )
                    dept_links = soup.select("a[href*='/courses/']")
                    depts = [
                        {"value": a["href"].split("/courses/")[-1].strip("/").upper()}
                        for a in dept_links
                        if "/courses/" in a.get("href", "")
                    ]
                except Exception:
                    return 0

            for dept_item in depts:
                dept = (dept_item.get("value") or dept_item.get("text", "")).upper()
                if not dept or len(dept) > 6:
                    continue
                # Try JSON API first
                courses_url = f"https://www.sfu.ca/bin/wcm/course-outlines?{TERM}/{dept.lower()}/courses"
                try:
                    resp = await client.get(courses_url, headers=self.HEADERS, timeout=15)
                    if resp.status_code == 200:
                        course_list = resp.json()
                        for c in course_list:
                            num = str(c.get("value", "")).strip()
                            name = (c.get("text") or c.get("title", "")).strip()
                            if not num or not name:
                                continue
                            code = f"{dept} {num}"
                            level_m = re.search(r"(\d)", num)
                            level = int(level_m.group(1)) * 100 if level_m else None

                            existing = self.db.query(Course).filter_by(
                                university_id=uni.id, code=code
                            ).first()
                            obj = existing or Course(university_id=uni.id, code=code)
                            if not existing:
                                self.db.add(obj)
                            obj.name = name
                            obj.level = level
                            obj.url = f"https://www.sfu.ca/students/calendar/2024/fall/courses/{dept.lower()}.html"
                            count += 1
                        continue
                except Exception:
                    pass

                # Fall back to HTML calendar page
                try:
                    cal_soup = await self.fetch(
                        SFU_CALENDAR_URL.format(dept=dept.lower()), client
                    )
                except Exception:
                    continue

                for el in cal_soup.select("h3, h4, dt"):
                    text = el.get_text(strip=True)
                    m = re.match(r"([A-Z]+)\s+(\d{3}[A-Z]?(?:\.\d+)?)\s*[-–]\s*(.+)", text)
                    if not m:
                        continue
                    d, num, name = m.group(1), m.group(2), m.group(3).strip()
                    code = f"{d} {num}"
                    level_m = re.search(r"(\d)", num)
                    level = int(level_m.group(1)) * 100 if level_m else None

                    desc_el = el.find_next_sibling(["p", "dd"])
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
                    obj.url = SFU_CALENDAR_URL.format(dept=dept.lower())
                    count += 1

        self.db.commit()
        return count
