from sqlalchemy.dialects.mysql import Insert


def preserve_fields(insert: Insert, *keys: str):
    d = {}
    for key in keys:
        d[key] = getattr(insert.inserted, key)
    return d
