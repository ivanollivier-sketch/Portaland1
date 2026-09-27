from .config import UNKNOWN


def normalize(records):
    """Keep original cells intact; reject invalid scores and costs."""
    for r in records:
        r["data"] = {k: v.strip() if isinstance(v, str) else v for k, v in r["raw"].items()}
        for field in ("valeur", "usage"):
            value = r["data"].get(field)
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not 1 <= value <= 5):
                raise ValueError(f"{r['record_id']}: {field} must be in [1,5]")
        cost = r["data"].get("cout_annuel_ke")
        if cost is not None and (isinstance(cost, bool) or not isinstance(cost, (int, float)) or cost < 0):
            raise ValueError(f"{r['record_id']}: invalid annual cost")
        r["organization"] = UNKNOWN
    return records
