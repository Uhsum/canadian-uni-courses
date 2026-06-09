"""
Scraper for University of Western Ontario course calendar.
Source: https://www.westerncalendar.uwo.ca/Courses.cfm?Subject=X
        Courses are in .panel-heading > h4.courseTitleNoBlueLink
"""
import httpx
import re
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

BASE = "https://www.westerncalendar.uwo.ca"
INDEX = BASE + "/Courses.cfm?SelectedCalendar=Live&ArchiveID="
SUBJ_URL = BASE + "/Courses.cfm?Subject={subj}&SelectedCalendar=Live&ArchiveID="


class WesternScraper(BaseScraper):
    name = "western_courses"
    university_short = "Western"
    delay = 1.5

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="Western").first()
        if not uni:
            raise ValueError("Western not found in DB — run seed first")

        count = 0
        async with httpx.AsyncClient(timeout=30) as client:
            # Get subject list from index
            soup = await self.fetch(INDEX, client)
            subj_links = [
                a["href"].split("Subject=")[1].split("&")[0]
                for a in soup.select("a[href*='Subject=']")
                if "Subject=" in a.get("href", "")
            ]
            subjects = list(dict.fromkeys(subj_links))

            for subj in subjects:
                try:
                    subj_soup = await self.fetch(SUBJ_URL.format(subj=subj), client)
                except Exception:
                    continue

                # Courses: h4.courseTitleNoBlueLink
                # Format: "Biology 1001A BIOLOGY FOR SCIENCE I"
                for h4 in subj_soup.select("h4.courseTitleNoBlueLink"):
                    raw = h4.get_text(" ", strip=True)
                    # Remove hidden text / link text
                    raw = re.sub(r'\s+', ' ', raw).strip()
                    m = re.match(
                        r"([A-Za-z &]+?)\s+(\d{4}[A-Z/]*)\s+(.*)", raw
                    )
                    if not m:
                        continue
                    subject_name = m.group(1).strip()
                    num_raw = m.group(2)
                    # Normalise "1001A/B" → "1001"
                    num = re.match(r"\d{4}", num_raw).group() if re.match(r"\d{4}", num_raw) else num_raw
                    name = m.group(3).strip()
                    if not name:
                        continue

                    # Build a compact code: first word of subject + number
                    words = subject_name.upper().split()
                    short = "".join(w[:3] for w in words[:2])
                    code = f"{short} {num}"

                    level_m = re.search(r"(\d)", num)
                    level = int(level_m.group(1)) * 100 if level_m else None

                    # Description from the adjacent collapse panel
                    panel_body = h4.find_parent(".panel-heading")
                    desc = ""
                    prereqs = ""
                    if panel_body:
                        panel_id = panel_body.select_one("a[href*=collapse]")
                        if panel_id:
                            collapse_id = panel_id["href"].lstrip("#")
                            collapse = subj_soup.find(id=collapse_id)
                            if collapse:
                                full_text = collapse.get_text("\n", strip=True)
                                prereq_m = re.search(r"Prerequisite[s]?\(s\)[:\s]+([^.]+\.)", full_text, re.I)
                                prereqs = prereq_m.group(1).strip() if prereq_m else ""
                                desc_lines = [l for l in full_text.splitlines() if l.strip() and "Prerequisite" not in l and "Antirequisite" not in l]
                                desc = " ".join(desc_lines[:3])

                    existing = self.db.query(Course).filter_by(
                        university_id=uni.id, code=code
                    ).first()
                    obj = existing or Course(university_id=uni.id, code=code)
                    if not existing:
                        self.db.add(obj)

                    obj.name = name
                    obj.description = desc[:1000]
                    obj.level = level
                    obj.prerequisites_text = prereqs
                    obj.url = SUBJ_URL.format(subj=subj)
                    count += 1

        self.db.commit()
        return count
