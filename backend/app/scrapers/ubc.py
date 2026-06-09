"""
Scraper for UBC course calendar.
Source: UBC Course Schedule API (public JSON, used by SSC)
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

UBC_SUBJECTS_URL = "https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subjareas"
UBC_SUBJECT_URL = "https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-all-departments&department={dept}"
UBC_COURSE_URL = "https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-course&dept={dept}&course={num}"


class UBCScraper(BaseScraper):
    name = "ubc_courses"
    university_short = "UBC"
    delay = 2.0

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="UBC").first()
        if not uni:
            raise ValueError("UBC not found in DB — run seed first")

        count = 0
        async with httpx.AsyncClient(timeout=30) as client:
            # Get list of departments
            soup = await self.fetch(UBC_SUBJECTS_URL, client)
            dept_links = soup.select("table.table tbody tr td a")
            depts = [a.get_text(strip=True) for a in dept_links if a.get_text(strip=True)]

            for dept in depts[:30]:  # cap at 30 depts for initial run
                dept_url = UBC_SUBJECT_URL.format(dept=dept)
                try:
                    dept_soup = await self.fetch(dept_url, client)
                except Exception:
                    continue

                rows = dept_soup.select("table.table tbody tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) < 2:
                        continue
                    course_num = cols[0].get_text(strip=True)
                    course_name = cols[1].get_text(strip=True)
                    if not course_num or not course_name:
                        continue

                    code = f"{dept} {course_num}"
                    level_match = re.match(r"(\d)", course_num)
                    level = int(level_match.group(1)) * 100 if level_match else None

                    existing = self.db.query(Course).filter_by(
                        university_id=uni.id, code=code
                    ).first()
                    obj = existing or Course(university_id=uni.id, code=code)
                    if not existing:
                        self.db.add(obj)

                    obj.name = course_name
                    obj.level = level
                    obj.url = UBC_COURSE_URL.format(dept=dept, num=course_num)
                    count += 1

        self.db.commit()
        return count
