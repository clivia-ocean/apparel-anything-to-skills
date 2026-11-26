import csv, json, hashlib, re
from pathlib import Path
from datetime import datetime, date

def load_records(path):
    p = Path(path)
    if p.suffix.lower() in (".json", ".jsonl"):
        text = p.read_text(encoding="utf-8-sig")
        if p.suffix.lower() == ".jsonl":
            return [json.loads(line) for line in text.splitlines() if line.strip()]
        data = json.loads(text)
        return data if isinstance(data, list) else data.get("records", [])
    with p.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def save_csv(path, rows, fieldnames=None):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = fieldnames or list(dict.fromkeys(k for row in rows for k in row.keys()))
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()

def parse_date(value):
    if not value: return None
    s = str(value).strip()[:10]
    try: return date.fromisoformat(s)
    except ValueError: return None

def stable_id(record):
    raw = "|".join(clean_text(record.get(k, "")).lower() for k in
                   ("customer_id", "customer_name", "email", "inquiry_date", "subject", "body"))
    return "inq_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

def normalize_records(records):
    out, seen = [], set()
    for r0 in records:
        r = {k: clean_text(v) for k, v in dict(r0).items()}
        r["body"] = clean_text(r.get("body"))
        r["subject"] = clean_text(r.get("subject"))
        if not r["body"] and not r["subject"]: continue
        r["inquiry_id"] = r.get("inquiry_id") or stable_id(r)
        key = r["inquiry_id"]
        if key in seen: continue
        seen.add(key)
        r.setdefault("customer_id", "")
        if not r["customer_id"]:
            r["customer_id"] = (r.get("email") or r.get("customer_name") or "unknown").lower()
        r.setdefault("customer_segment", "unknown")
        r.setdefault("country", "unknown")
        r.setdefault("product_category", "unknown")
        r.setdefault("inquiry_date", "")
        r.setdefault("source", "")
        r["text"] = (r["subject"] + " " + r["body"]).strip()
        out.append(r)
    return out

def read_yaml_simple(path):
    # Minimal YAML subset reader for the package's simple config files.
    # For complex YAML, install PyYAML and replace this adapter.
    try:
        import yaml
        return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except ImportError:
        raise RuntimeError("PyYAML is required to parse YAML configs. Install with: pip install pyyaml")
