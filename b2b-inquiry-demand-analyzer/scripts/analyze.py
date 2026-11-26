#!/usr/bin/env python3
import argparse, sys
from pathlib import Path
from common import load_records, normalize_records, save_csv, read_yaml_simple
from demand_extractor import load_taxonomy, extract
from demand_scoring import score
from reporting import write_reports

def main():
    ap = argparse.ArgumentParser(description="Analyze B2B inquiry demand.")
    ap.add_argument("--input", required=True, help="CSV, JSON or JSONL input file")
    ap.add_argument("--out", default="output", help="Output directory")
    ap.add_argument("--store", help="Canonical CSV store used for incremental mode")
    ap.add_argument("--append", action="store_true", help="Append input to --store, deduplicating inquiry_id")
    ap.add_argument("--taxonomy", default="config/demand-taxonomy.yaml")
    ap.add_argument("--scoring", default="config/scoring.yaml")
    args = ap.parse_args()

    incoming = normalize_records(load_records(args.input))
    if args.append:
        if not args.store:
            ap.error("--append requires --store")
        store_path = Path(args.store)
        existing = normalize_records(load_records(store_path)) if store_path.exists() else []
        merged = {r["inquiry_id"]: r for r in existing}
        for r in incoming: merged.setdefault(r["inquiry_id"], r)
        records = list(merged.values())
        store_path.parent.mkdir(parents=True, exist_ok=True)
        save_csv(store_path, records)
    elif args.store and Path(args.store).exists():
        records = normalize_records(load_records(args.store))
    else:
        records = incoming

    taxonomy = load_taxonomy(args.taxonomy)
    matches = extract(records, taxonomy)
    scoring_cfg = read_yaml_simple(args.scoring)
    ranking = score(matches, records, scoring_cfg)
    write_reports(args.out, records, matches, ranking, taxonomy)
    print(f"Analyzed {len(records)} inquiries from {len(set(r['customer_id'] for r in records))} customers.")
    print(f"Matched {len(matches)} demand mentions. Reports: {Path(args.out).resolve()}")

if __name__ == "__main__":
    main()
