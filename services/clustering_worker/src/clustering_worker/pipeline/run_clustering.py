from __future__ import annotations

import json
import logging
import re
from collections import defaultdict
from typing import Any

from sqlalchemy import text

from db.models import PainCluster, PainInstance, Signal
from db.repos import cluster_signals as cluster_signals_repo
from db.repos import pain_clusters as clusters_repo
from db.session import SessionLocal

log = logging.getLogger(__name__)

# --- ML ---
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer


# -----------------------------
# SPAM FILTER
# -----------------------------

SPAM_KEYWORDS = [
    "take my exam",
    "pay someone",
    "do my homework",
    "proctored exam",
    "lockdown browser",
    "exam cheating",
    "take my online class",
    "hire test taker",
]

def _is_spam(text: str | None) -> bool:
    if not text:
        return True

    lower = text.lower()

    # very long SEO spam
    if len(text) > 5000:
        return True

    # keyword match
    if any(k in lower for k in SPAM_KEYWORDS):
        return True

    # phone numbers
    phones = re.findall(r"\+?\d[\d\s\-]{7,}", text)
    if len(phones) >= 2:
        return True

    # repetition ratio
    words = lower.split()
    if len(words) > 50:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.3:
            return True

    return False


# -----------------------------
# TEXT + TITLE + SUMMARY
# -----------------------------

def _clean_text(s: str | None) -> str:
    if not s:
        return ""
    return " ".join(s.replace("\n", " ").split())


def _top_phrases(vectorizer: TfidfVectorizer, X_tfidf, doc_idx: list[int], top_k: int = 8) -> list[str]:
    if not doc_idx:
        return []
    sub = X_tfidf[doc_idx]
    mean_scores = sub.mean(axis=0)
    arr = mean_scores.A1
    feats = vectorizer.get_feature_names_out()
    top = arr.argsort()[::-1][: max(top_k * 3, top_k)]
    phrases: list[str] = []
    for i in top:
        if arr[i] <= 0:
            break
        p = str(feats[i]).strip()
        if len(p) < 3:
            continue
        phrases.append(p)
        if len(phrases) >= top_k:
            break
    return phrases


def _pick_title(phrases: list[str], lab: int) -> str:
    if not phrases:
        return f"Cluster {lab}"
    multi = [p for p in phrases if " " in p]
    chosen = multi[0] if multi else phrases[0]
    return chosen[:1].upper() + chosen[1:]


def _build_cluster_summary(texts: list[str], doc_idx: list[int], max_sentences: int = 3) -> str:
    cluster_texts = [texts[i] for i in doc_idx if texts[i].strip()]
    if not cluster_texts:
        return ""

    sentences = []
    for t in cluster_texts:
        for s in t.split('.'):
            s_clean = s.strip()
            if s_clean:
                sentences.append(s_clean)

    sentences_sorted = sorted(sentences, key=lambda s: -len(s))
    summary = ". ".join(sentences_sorted[:max_sentences])
    if summary:
        summary += "."
    return summary


def _clean_summary(summary: str, max_total_chars: int = 400, max_sentence_len: int = 120) -> str:
    if not summary:
        return ""

    sentences = [s.strip() for s in summary.split('.') if s.strip()]
    seen = set()
    unique_sentences = []
    for s in sentences:
        if s.lower() not in seen:
            seen.add(s.lower())
            unique_sentences.append(s)

    truncated = []
    for s in unique_sentences:
        if len(s) > max_sentence_len:
            truncated.append(s[:max_sentence_len].rstrip() + "…")
        else:
            truncated.append(s)

    final_summary = ""
    for s in truncated:
        if len(final_summary) + len(s) + 2 > max_total_chars:
            break
        if final_summary:
            final_summary += ". "
        final_summary += s
    if final_summary:
        final_summary += "."
    return final_summary


# -----------------------------
# MAIN CLUSTERING JOB
# -----------------------------

def run_clustering_job(job: dict[str, Any]) -> dict[str, int]:
    vertical_id = str(job.get("vertical_id") or "")
    vertical_db_id = int(job.get("vertical_db_id") or 0)
    if vertical_db_id <= 0:
        raise ValueError(f"invalid vertical_db_id: {job.get('vertical_db_id')!r}")

    cluster_version = str(job.get("cluster_version") or "tfidf_v2")
    run_id = job.get("run_id")
    day = job.get("day")

    db = SessionLocal()
    try:
        rows = (
            db.query(PainInstance.id, PainInstance.signal_id, Signal.content)
            .join(Signal, Signal.id == PainInstance.signal_id)
            .filter(PainInstance.vertical_id == vertical_db_id)
            .order_by(PainInstance.id.asc())
            .all()
        )

        # --- SPAM FILTER APPLIED HERE ---
        filtered_rows = [r for r in rows if not _is_spam(r[2])]
        if not filtered_rows:
            return {"clusters": 0, "pain_instances": 0, "links_inserted": 0}

        pain_ids = [int(r[0]) for r in filtered_rows]
        texts = [_clean_text(r[2]) for r in filtered_rows]

        # purge previous version
        existing_cluster_ids = [
            int(x[0])
            for x in db.query(PainCluster.id)
            .filter(PainCluster.vertical_id == vertical_db_id)
            .filter(PainCluster.cluster_version == cluster_version)
            .all()
        ]
        if existing_cluster_ids:
            db.execute(
                text("DELETE FROM cluster_signals WHERE cluster_id = ANY(:ids)"),
                {"ids": existing_cluster_ids},
            )
            db.query(PainCluster).filter(
                PainCluster.id.in_(existing_cluster_ids)
            ).delete(synchronize_session=False)
            db.flush()

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.9,
            strip_accents="unicode",
        )
        X = vectorizer.fit_transform(texts)

        n_docs = X.shape[0]
        n_components = min(50, max(2, n_docs - 1), X.shape[1] - 1 if X.shape[1] > 1 else 1)

        if n_components < 2:
            labels = [0] * n_docs
            X_low = None
        else:
            svd = TruncatedSVD(n_components=n_components, random_state=0)
            X_low = svd.fit_transform(X)
            try:
                agg = AgglomerativeClustering(
                    n_clusters=None,
                    distance_threshold=1.2,
                    linkage="ward",
                )
                labels = agg.fit_predict(X_low).tolist()
            except Exception:
                labels = [0] * n_docs

        if len(set(labels)) <= 1 and n_docs >= 8 and X_low is not None:
            k = min(12, max(2, n_docs // 10))
            km = KMeans(n_clusters=k, random_state=0, n_init="auto")
            labels = km.fit_predict(X_low).tolist()

        by_label: dict[int, list[int]] = defaultdict(list)
        for i, lab in enumerate(labels):
            by_label[int(lab)].append(i)

        created_clusters = 0
        total_links = 0

        for lab, doc_idx in sorted(by_label.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            size = len(doc_idx)
            if size <= 0:
                continue

            cluster_key = f"lab_{lab}"
            phrases = _top_phrases(vectorizer, X, doc_idx)
            title = _pick_title(phrases, lab)
            top_signal_ids_json = json.dumps([filtered_rows[i][1] for i in doc_idx])
            summary = _clean_summary(_build_cluster_summary(texts, doc_idx))

            cluster_obj, _ = clusters_repo.upsert_cluster(
                db,
                vertical_id=vertical_db_id,
                cluster_version=cluster_version,
                cluster_key=cluster_key,
                title=title,
                size=size,
                key_phrases_json=json.dumps(phrases, ensure_ascii=False),
                top_signal_ids_json=top_signal_ids_json,
                cluster_summary=summary,
            )

            ids_for_cluster = [pain_ids[i] for i in doc_idx]
            inserted = cluster_signals_repo.link_many(
                db,
                cluster_id=int(cluster_obj.id),
                pain_instance_ids=ids_for_cluster,
            )

            created_clusters += 1
            total_links += inserted

        db.commit()

        log.info(
            "clustered vertical_id=%s vertical_db_id=%s clusters=%s pain_instances=%s links_inserted=%s run_id=%s",
            vertical_id,
            vertical_db_id,
            created_clusters,
            len(pain_ids),
            total_links,
            run_id,
        )

        return {
            "clusters": created_clusters,
            "pain_instances": len(pain_ids),
            "links_inserted": total_links,
        }

    finally:
        db.close()
