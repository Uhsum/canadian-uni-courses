import asyncio
from sqlalchemy.orm import Session
from app.scrapers.uoft import UofTScraper
from app.scrapers.ubc import UBCScraper
from app.scrapers.mcgill import McGillScraper
from app.scrapers.waterloo import WaterlooScraper
from app.scrapers.mcmaster import McMasterScraper
from app.scrapers.ualberta import UAlbertaScraper
from app.scrapers.queens import QueensScraper
from app.scrapers.sfu import SFUScraper
from app.scrapers.uottawa import UOttawaScraper
from app.scrapers.western import WesternScraper
from app.scrapers.uguelph import UGuelphScraper
from app.scrapers.dalhousie import DalhouisieScraper
from app.scrapers.mun import MUNScraper

SCRAPERS = {
    "UofT":     UofTScraper,
    "UBC":      UBCScraper,
    "McGill":   McGillScraper,
    "Waterloo": WaterlooScraper,
    "McMaster": McMasterScraper,
    "UAlberta": UAlbertaScraper,
    "Queens":   QueensScraper,
    "SFU":      SFUScraper,
    "UOttawa":  UOttawaScraper,
    "Western":  WesternScraper,
    "UGuelph":  UGuelphScraper,
    "Dal":      DalhouisieScraper,
    "MUN":      MUNScraper,
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
            print(f"  {short}: {scraper._run.status} — {scraper._run.records_upserted} courses")
        except Exception as exc:
            print(f"  ERROR {short}: {exc}")
