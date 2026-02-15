from ingestion_worker.adapters.reddit.fetch import fetch_reddit_signals
from ingestion_worker.storage.signals_writer import SignalsWriter
from ingestion_worker.adapters.reddit.types import RssItem

def ingest_vertical(job) -> None:
    vertical_id = job["vertical_id"]
    source = job["source"]
    query = job.get("query", "saas")
    limit = job.get("limit", 25)

    print(f"Fetching signals for vertical_id={vertical_id} with query={query} (limit={limit})")

    signals = fetch_reddit_signals(vertical_id=vertical_id, limit=limit)

    writer = SignalsWriter()
    inserted, deduped = writer.insert_many(signals)

    print(f"[ingestion] vertical_id={vertical_id} source={source} inserted={inserted} deduped={deduped}")
