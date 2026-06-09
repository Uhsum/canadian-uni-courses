import asyncio
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from tenacity import retry, stop_after_attempt, wait_exponential
from app.models.models import ScraperRun
from sqlalchemy.orm import Session


class BaseScraper:
    name: str = "base"
    university_short: str = ""
    base_url: str = ""
    # Polite crawl delay in seconds
    delay: float = 1.5

    HEADERS = {
        "User-Agent": (
            "CanadianUniCourses/1.0 (educational research tool; "
            "contact: your@email.com)"
        ),
        "Accept-Language": "en-CA,en;q=0.9",
    }

    def __init__(self, db: Session):
        self.db = db
        self._run: ScraperRun | None = None

    async def run(self):
        self._run = ScraperRun(
            scraper_name=self.name,
            university_short=self.university_short,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(self._run)
        self.db.commit()

        try:
            count = await self.scrape()
            self._run.status = "success"
            self._run.records_upserted = count
        except Exception as exc:
            self._run.status = "error"
            self._run.error_message = str(exc)
            raise
        finally:
            self._run.finished_at = datetime.now(timezone.utc)
            self.db.commit()

    async def scrape(self) -> int:
        raise NotImplementedError

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def fetch(self, url: str, client: httpx.AsyncClient) -> BeautifulSoup:
        await asyncio.sleep(self.delay)
        resp = await client.get(url, headers=self.HEADERS, follow_redirects=True, timeout=20)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")
