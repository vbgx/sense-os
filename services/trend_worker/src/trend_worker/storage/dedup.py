def idempotency_key(cluster_id: int, date: str, formula_version: str) -> str:
    return f"{cluster_id}:{date}:{formula_version}"
