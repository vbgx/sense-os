def deduplicate_by_key(items, key_fn):
    seen = set()
    result = []

    for item in items:
        key = key_fn(item)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)

    return result
