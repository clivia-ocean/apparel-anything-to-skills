from collections import defaultdict
from pathlib import Path
import json
from common import save_csv

def build_matrix(matches):
    groups = defaultdict(set)
    for m in matches:
        for dimension, value in (("country", m["country"]), ("customer_segment", m["customer_segment"]),
                                 ("product_category", m["product_category"])):
            groups[(dimension, value, m["demand_id"], m["demand_label"])].add(m["customer_id"])
    return [{"dimension": k[0], "segment": k[1], "demand_id": k[2], "demand_label": k[3],
             "unique_customers": len(v)} for k, v in groups.items()]

def write_reports(outdir, records, matches, ranking, taxonomy):
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    save_csv(out / "demand_ranking.csv", ranking)
    save_csv(out / "demand_matrix.csv", build_matrix(matches))
    evidence_by = defaultdict(list)
    for m in matches: evidence_by[m["demand_id"]].append(m["evidence"])
    labels = {x["id"]: x["label"] for x in taxonomy}
    opp = ["# Product Opportunity Report", "",
           "> Opportunities are hypotheses based on inquiry frequency and evidence, not proof of market size or profitability.", "",
           "## Highest-priority demand signals", ""]
    for row in ranking[:15]:
        opp += [f"### {row['demand_label']} — score {row['priority_score']}/100",
                f"- Unique customers: {row['unique_customers']} ({row['customer_coverage_pct']}% coverage)",
                f"- Unique inquiries: {row['unique_inquiries']}",
                f"- Trend mentions: recent {row['recent_mentions']} vs previous {row['previous_period_mentions']}",
                f"- Evidence example: “{(evidence_by[row['demand_id']][0] if evidence_by[row['demand_id']] else '')}”", ""]
    opp += ["## Validation checklist", "- Confirm target price and willingness to pay.",
            "- Compare inquiry frequency with quotation conversion and closed-won orders.",
            "- Validate demand by country and customer segment.",
            "- Check margin, material availability, MOQ and production feasibility."]
    (out / "product_opportunities.md").write_text("\n".join(opp), encoding="utf-8")
    supplier = ["# Supplier Capability Recommendations", "",
                "> Recommendations translate observed inquiry signals into capabilities to validate with factories.", ""]
    cap_map = {x["id"]: x.get("supplier_capabilities", []) for x in taxonomy}
    for row in ranking[:15]:
        caps = cap_map.get(row["demand_id"], [])
        if not caps: continue
        supplier += [f"## {row['demand_label']}", f"- Demand priority score: {row['priority_score']}/100",
                     "- Suggested capabilities: " + "; ".join(caps),
                     "- Evidence coverage: " + str(row["unique_customers"]) + " unique customers", ""]
    supplier += ["## Supplier evaluation questions",
                 "- Can the supplier provide recent production examples and verifiable quality records?",
                 "- What are standard and negotiable MOQs by fabric, color and size?",
                 "- What is realistic sample and bulk lead time, including peak-season capacity?",
                 "- Which test reports/certifications are current, applicable and verifiable?",
                 "- Can the supplier demonstrate lot-to-lot consistency and corrective-action procedures?"]
    (out / "supplier_capabilities.md").write_text("\n".join(supplier), encoding="utf-8")
    summary = {"record_count": len(records), "matched_demand_mentions": len(matches),
               "unique_customers": len(set(r["customer_id"] for r in records)),
               "ranked_demands": len(ranking), "top_demands": ranking[:10]}
    (out / "analysis_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
