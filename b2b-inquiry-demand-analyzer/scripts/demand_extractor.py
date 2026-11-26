from pathlib import Path
from common import read_yaml_simple

def load_taxonomy(path):
    cfg = read_yaml_simple(path)
    items = []
    for industry, block in cfg.get("industries", {}).items():
        for item in block.get("categories", []):
            entry = dict(item); entry["industry"] = industry
            items.append(entry)
    return items

def extract(records, taxonomy):
    matches = []
    for rec in records:
        text = (rec.get("text") or "").lower()
        for item in taxonomy:
            hits = [term for term in item.get("terms", []) if term.lower() in text]
            if not hits: continue
            # Evidence is a short window around the first matched term.
            term = max(hits, key=len)
            pos = text.find(term.lower())
            start, end = max(0, pos - 65), min(len(text), pos + len(term) + 90)
            matches.append({
                "inquiry_id": rec["inquiry_id"],
                "customer_id": rec["customer_id"],
                "customer_name": rec.get("customer_name", ""),
                "country": rec.get("country", "unknown"),
                "customer_segment": rec.get("customer_segment", "unknown"),
                "product_category": rec.get("product_category", "unknown"),
                "inquiry_date": rec.get("inquiry_date", ""),
                "demand_id": item["id"],
                "demand_label": item["label"],
                "industry": item["industry"],
                "matched_terms": "; ".join(hits),
                "evidence": rec.get("text", "")[start:end],
                "explicitness": 1.0,
                "commercial_importance": float(item.get("importance", 0.5))
            })
    return matches
