"""
Scraper for University of Toronto Arts & Science course calendar.
Source: https://artsci.calendar.utoronto.ca/search-courses (paginated HTML)
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

BASE = "https://artsci.calendar.utoronto.ca"
SEARCH = BASE + "/search-courses?course_keyword=&field_section_value=All&page={page}"


class UofTScraper(BaseScraper):
    name = "uoft_courses"
    university_short = "UofT"
    delay = 1.5

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="UofT").first()
        if not uni:
            raise ValueError("UofT not found in DB — run seed first")

        count = 0
        async with httpx.AsyncClient(timeout=30) as client:
            page = 0
            while True:
                try:
                    soup = await self.fetch(SEARCH.format(page=page), client)
                except Exception:
                    break

                rows = soup.select(".views-row")
                if not rows:
                    break

                for row in rows:
                    text = row.get_text("\n", strip=True)
                    # First line: "CSC108H1 - Introduction to Computer Programming"
                    lines = [l.strip() for l in text.splitlines() if l.strip()]
                    if not lines:
                        continue
                    title_line = lines[0]
                    m = re.match(r"([A-Z]+\d+[A-Z0-9]*)\s*[-–]\s*(.+)", title_line)
                    if not m:
                        continue

                    code = m.group(1).strip()
                    name = m.group(2).strip()
                    level_m = re.search(r"(\d)", code)
                    level = int(level_m.group(1)) * 100 if level_m else None

                    # Description is remaining lines before "Prerequisites:"
                    desc_lines = []
                    prereqs = ""
                    for line in lines[1:]:
                        if re.match(r"Prerequisite[s]?:", line, re.I):
                            prereqs = re.sub(r"Prerequisite[s]?:\s*", "", line, flags=re.I)
                        elif re.match(r"Hours:", line, re.I):
                            continue
                        else:
                            desc_lines.append(line)

                    # course URL
                    link = row.select_one("a")
                    url = BASE + link["href"] if link and link.get("href") else ""

                    existing = self.db.query(Course).filter_by(
                        university_id=uni.id, code=code
                    ).first()
                    obj = existing or Course(university_id=uni.id, code=code)
                    if not existing:
                        self.db.add(obj)

                    obj.name = name
                    obj.description = " ".join(desc_lines)
                    obj.level = level
                    obj.prerequisites_text = prereqs
                    obj.url = url
                    count += 1

                # check if there's a next page
                next_link = soup.select_one('a[title="Go to next page"], a[rel="next"]')
                if not next_link:
                    # also check pager for our page+1
                    pager_links = [a.get("href", "") for a in soup.select(".pager a")]
                    if not any(f"page={page+1}" in l for l in pager_links):
                        break
                page += 1
                if page > 200:  # safety cap (~12,000 courses)
                    break

        self.db.commit()
        return count
