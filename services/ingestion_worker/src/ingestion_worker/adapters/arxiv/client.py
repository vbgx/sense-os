from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Sequence
from urllib.parse import urlencode

import httpx

from ingestion_worker.settings import settings
from .rate_limit import ARXIV_LIMITER
from .types import ArxivPaper


ARXIV_API_URL = "http://export.arxiv.org/api/query"


@dataclass
class ArxivClient:
    timeout_s: float = 20.0

    def _client(self) -> httpx.Client:
        return httpx.Client(
            timeout=self.timeout_s,
            headers={
                "User-Agent": settings.sense_ua,
                "Accept": "application/atom+xml",
            },
            follow_redirects=True,
        )

    def search(
        self,
        *,
        query: str,
        max_results: int = 20,
        sort_by: str = "submittedDate",
        sort_order: str = "descending",
    ) -> Sequence[ArxivPaper]:
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }

        url = f"{ARXIV_API_URL}?{urlencode(params)}"

        ARXIV_LIMITER.acquire()

        with self._client() as c:
            r = c.get(url)
            r.raise_for_status()
            xml_content = r.text

        return self._parse_feed(xml_content)

    def _parse_feed(self, xml_content: str) -> Sequence[ArxivPaper]:
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        root = ET.fromstring(xml_content)

        papers: list[ArxivPaper] = []

        for entry in root.findall("atom:entry", ns):
            paper_id = entry.findtext("atom:id", default="", namespaces=ns)
            title = entry.findtext("atom:title", default="", namespaces=ns).strip()
            summary = entry.findtext("atom:summary", default="", namespaces=ns).strip()
            published = entry.findtext("atom:published", default="", namespaces=ns)
            updated = entry.findtext("atom:updated", default="", namespaces=ns)

            authors = [
                author.findtext("atom:name", default="", namespaces=ns)
                for author in entry.findall("atom:author", ns)
            ]

            primary_category_elem = entry.find("arxiv:primary_category", ns)
            primary_category = (
                primary_category_elem.attrib.get("term")
                if primary_category_elem is not None
                else None
            )

            papers.append(
                ArxivPaper(
                    id=paper_id,
                    title=title,
                    summary=summary,
                    published=published,
                    updated=updated,
                    authors=authors,
                    primary_category=primary_category,
                    raw={"xml_id": paper_id},
                )
            )

        return papers
