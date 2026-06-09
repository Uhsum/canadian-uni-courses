import asyncio
from sqlalchemy.orm import Session
from app.scrapers.uoft import UofTScraper
from app.scrapers.ubc import UBCScraper
from app.scrapers.mcgill import McGillScraper
from app.scrapers.waterloo import WaterlooScraper
from app.scrapers.mcmaster import McMasterScraper

SCRAPERS = {
    "UofT": UofTScraper,
    "UBC": UBCScraper,
    "McGill": McGillScraper,
    "Waterloo": WaterlooScraper,
    "McMaster": McMasterScraper,
}


def run_scraper(university_short: str, db: Session):
    cls = SCRAPERS.get(university_short)
    if not cls:
        raise ValueError(f"No scraper for '{university_short}'. Valid: {list(SCRAPERS)}")
    scraper = cls(db)
    asyncio.run(scraper.run())


def run_all(db: Session):
    for short, cls in SCRAPERS.items():
        print(f"Running scraper: {short}")
        try:
            scraper = cls(db)
            asyncio.run(scraper.run())
        except Exception as exc:
            print(f"  ERROR {short}: {exc}")
