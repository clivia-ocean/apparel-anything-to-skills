from datetime import date, timedelta
from collections import defaultdict

def score(matches, records, config):
    weights = config["weights"]
    dates = [date.fromisoformat(r["inquiry_date"][:10]) for r in records
             if r.get("inquiry_date") and _valid_date(r["inquiry_date"][:10])]
    anchor = max(dates) if dates else None
    recent_days = int(config["trend"]["recent_days"])
    compare_days = int(config["trend"]["comparison_days"])
    neutral = float(config["trend"].get("neutral_score", 50))
    grouped = defaultdict(list)
    for m in matches: grouped[m["demand_id"]].append(m)
    total_customers = max(1, len(set(r["customer_id"] for r in records)))
    rows = []
    for did, group in grouped.items():
        customers = set(x["customer_id"] for x in group)
        inquiries = set(x["inquiry_id"] for x in group)
        coverage = len(customers) / total_customers * 100
        explicit = sum(x["explicitness"] for x in group) / len(group) * 100
        importance = sum(x["commercial_importance"] for x in group) / len(group) * 100
        recent_score = neutral
        recent_n = prior_n = 0
        if anchor:
            recent_start = anchor - timedelta(days=recent_days - 1)
            prior_start = recent_start - timedelta(days=compare_days)
            prior_end = recent_start - timedelta(days=1)
            recent_n = sum(1 for x in group if _in_range(x.get("inquiry_date"), recent_start, anchor))
            prior_n = sum(1 for x in group if _in_range(x.get("inquiry_date"), prior_start, prior_end))
            if recent_n + prior_n:
                # Relative change is bounded to avoid extreme scores on tiny counts.
                ratio = (recent_n + 1) / (prior_n + 1)
                recent_score = max(0, min(100, 50 + 25 * (ratio - 1)))
        total = (coverage * weights["customer_coverage"] +
                 explicit * weights["explicitness"] +
                 importance * weights["commercial_importance"] +
                 recent_score * weights["recent_trend"])
        rows.append({
            "demand_id": did, "demand_label": group[0]["demand_label"],
            "industry": group[0]["industry"], "unique_customers": len(customers),
            "unique_inquiries": len(inquiries), "customer_coverage_pct": round(coverage, 2),
            "explicitness_pct": round(explicit, 2), "commercial_importance_pct": round(importance, 2),
            "recent_mentions": recent_n, "previous_period_mentions": prior_n,
            "trend_score": round(recent_score, 2), "priority_score": round(total, 2)
        })
    return sorted(rows, key=lambda x: (-x["priority_score"], -x["unique_customers"]))

def _valid_date(s):
    try: date.fromisoformat(s); return True
    except Exception: return False

def _in_range(s, start, end):
    if not s or not _valid_date(s[:10]): return False
    d = date.fromisoformat(s[:10])
    return start <= d <= end
