"""
Scraper for McGill University courses.

McGill's search portal and department pages require login (as of 2024-25).
Individual course pages are still publicly accessible at:
  https://www.mcgill.ca/study/2024-2025/courses/{dept_lower}-{num}

Strategy:
  1. Use known McGill department codes and typical course number ranges.
  2. Fetch each course URL; 200 + valid h1 = real course; 404/redirect = skip.
  3. Parse course name, description, and prerequisites from the page div.

We limit to undergrad range (100–499) for each department.
"""
import httpx
import re
import asyncio
from app.scrapers.base import BaseScraper
from app.models.models import University, Course

BASE = "https://www.mcgill.ca/study/2024-2025/courses"

# McGill undergrad department codes → typical course number suffixes used
# Format: (dept_code, url_prefix, number_range_step)
DEPARTMENTS = [
    # Science
    ("COMP", "comp",  list(range(202, 600, 1))),
    ("MATH", "math",  list(range(111, 600, 1))),
    ("BIOL", "biol",  list(range(111, 600, 1))),
    ("CHEM", "chem",  list(range(110, 500, 1))),
    ("PHYS", "phys",  list(range(101, 500, 1))),
    ("PSYC", "psyc",  list(range(100, 500, 1))),
    ("STAT", "stat",  list(range(204, 460, 1))),
    ("MICR", "micr",  list(range(230, 500, 1))),
    ("ANAT", "anat",  list(range(212, 460, 1))),
    ("NSCI", "nsci",  list(range(200, 420, 1))),
    # Engineering
    ("ECSE", "ecse",  list(range(200, 500, 1))),
    ("MECH", "mech",  list(range(210, 500, 1))),
    ("CIVE", "cive",  list(range(200, 490, 1))),
    ("CHEE", "chee",  list(range(200, 490, 1))),
    # Arts & Social Sciences
    ("ECON", "econ",  list(range(208, 460, 1))),
    ("POLI", "poli",  list(range(200, 490, 1))),
    ("SOCI", "soci",  list(range(202, 490, 1))),
    ("HIST", "hist",  list(range(200, 490, 1))),
    ("ENGL", "engl",  list(range(200, 490, 1))),
    ("PHIL", "phil",  list(range(210, 490, 1))),
    # Management
    ("MGCR", "mgcr",  list(range(211, 430, 1))),
    ("FINE", "fine",  list(range(340, 490, 1))),
    # Health Sciences
    ("EPIB", "epib",  list(range(301, 490, 1))),
    ("NUTR", "nutr",  list(range(201, 460, 1))),
    ("EXER", "exer",  list(range(201, 460, 1))),
    ("KINE", "kine",  list(range(200, 490, 1))),
]


class McGillScraper(BaseScraper):
    name = "mcgill_courses"
    university_short = "McGill"
    # Lower delay since most URLs will 404 quickly
    delay = 0.3

    async def scrape(self) -> int:
        uni = self.db.query(University).filter_by(short_name="McGill").first()
        if not uni:
            raise ValueError("McGill not found in DB — run seed first")

        count = 0
        async with httpx.AsyncClient(timeout=15) as client:
            for dept_code, url_prefix, numbers in DEPARTMENTS:
                for num in numbers:
                    url = f"{BASE}/{url_prefix}-{num}"
                    try:
                        await asyncio.sleep(self.delay)
                        resp = await client.get(url, headers=self.HEADERS, follow_redirects=False)
                    except Exception:
                        continue

                    # Skip 404s and redirects quickly
                    if resp.status_code != 200:
                        continue

                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(resp.text, "lxml")
                    h1 = soup.find("h1")
                    if not h1:
                        continue

                    title = h1.get_text(strip=True)
                    # Verify it matches our expected code
                    expected = f"{dept_code} {num}"
                    if not title.startswith(expected):
                        continue

                    # Extract name — title format: "COMP 202 Course Name (N credits)"
                    name_m = re.match(
                        rf"{re.escape(expected)}\s+(.*?)(?:\s+\(\d+\s+credits?\))?$",
                        title,
                    )
                    name = name_m.group(1).strip() if name_m else title

                    # Content is in a large unstyled div — find the paragraph after the title
                    full_text = soup.get_text("\n")
                    # Find section after the course code heading
                    code_pos = full_text.find(expected)
                    window = full_text[code_pos:code_pos + 800] if code_pos >= 0 else ""

                    # Extract description (skip "Offered by:" line)
                    desc_m = re.search(r"Overview\s*(.*?)(?:Prerequisite|Restriction|Note|$)", window, re.S)
                    desc = re.sub(r"\s+", " ", desc_m.group(1)).strip()[:1000] if desc_m else ""

                    prereq_m = re.search(r"Prerequisite[s]?[:\s]+([^.]+\.)", window, re.I)
                    prereqs = prereq_m.group(1).strip() if prereq_m else ""

                    level_m = re.search(r"(\d)", str(num))
                    level = int(level_m.group(1)) * 100 if level_m else None

                    existing = self.db.query(Course).filter_by(
                        university_id=uni.id, code=expected
                    ).first()
                    obj = existing or Course(university_id=uni.id, code=expected)
                    if not existing:
                        self.db.add(obj)

                    obj.name = name
                    obj.description = desc
                    obj.level = level
                    obj.prerequisites_text = prereqs
                    obj.url = url
                    count += 1

                    if count % 50 == 0:
                        self.db.flush()

        self.db.commit()
        return count
