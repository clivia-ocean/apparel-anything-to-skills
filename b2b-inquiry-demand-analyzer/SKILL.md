---
name: b2b-inquiry-demand-analyzer
description: Analyze batches and ongoing streams of B2B customer inquiries, extract recurring buyer needs, rank demand, compare customer segments, identify product opportunities, and recommend supplier capability improvements. Supports general industries with an apparel/loungewear taxonomy.
中文描述: 分析B2B客户的批量及持续性询盘，提炼买家共性需求，对需求进行优先级排序，对比不同客户群体，挖掘产品机会，并就提升供应商能力提出建议。该方案适用于通用行业，并内置了服装/家居服类目体系。
version: 1.0.0
---

# B2B Inquiry Demand Analyzer

## Purpose
Turn raw B2B inquiries into evidence-based demand intelligence. The skill must analyze both:
1. **Batch mode** — a historical set of inquiry records.
2. **Incremental mode** — append new inquiries, deduplicate records, and refresh the aggregate analysis without losing prior records.

The engine is industry-neutral. Apparel, sleepwear, pajamas, robes, and loungewear are supported through a configurable domain taxonomy.

## Inputs
Accept one or more of:
- CSV or XLSX exports (CSV is supported by the included CLI; XLSX can be converted to CSV or handled by a future adapter).
- JSON or JSONL records.
- Plain-text/email inquiry content, manually converted to the canonical record format.
- CRM exports after mapping their columns to the canonical schema.

Canonical fields:
- `inquiry_id`: stable unique ID; if missing, generate one.
- `customer_id`: stable buyer/company ID where available.
- `customer_name`
- `email`
- `website`
- `country`
- `customer_segment`: e.g. DTC brand, retailer, wholesaler, importer, distributor, marketplace seller, unknown.
- `product_category`
- `inquiry_date`: ISO date `YYYY-MM-DD`.
- `subject`
- `body`
- `source`
- `language`

At minimum, `body` or `subject` must contain inquiry text.

## Workflow
1. **Normalize** — standardize dates, whitespace, IDs, and missing values.
2. **Deduplicate** — deduplicate by `inquiry_id`; optionally detect likely duplicates by normalized text + customer.
3. **Extract needs** — match configurable taxonomy terms and phrases. Preserve evidence snippets and distinguish explicit evidence from inferred matches.
4. **Aggregate** — count unique inquiries and unique customers for each demand item. Repeated mentions in one inquiry count once for coverage.
5. **Score** — calculate a transparent 0–100 priority score using the configured weights:
   - unique-customer coverage: 40%
   - explicitness: 20%
   - commercial importance: 25%
   - recent trend: 15%
6. **Segment** — compare country, customer segment, and product category where sample size permits.
7. **Co-occurrence** — identify needs commonly requested together.
8. **Opportunity analysis** — identify high-frequency, high-priority, and potentially underserved needs. Do not claim an unmet market need unless evidence supports it; label it as a hypothesis.
9. **Supplier analysis** — translate demand into supplier capabilities, quality controls, production capabilities, customization and documentation requirements.
10. **Report** — produce ranking, matrix, opportunity, and supplier reports.

## Batch mode
Run:
```bash
python scripts/analyze.py --input examples/sample-inquiries.csv --out output --format both
```

## Incremental mode
Append new records to the same canonical dataset:
```bash
python scripts/analyze.py --input examples/new-inquiries.csv --store data/inquiries.csv --append --out output
```
The store is the source of truth. Existing `inquiry_id` values are not duplicated. If no `inquiry_id` is supplied, a deterministic ID is generated from customer, date, subject, and body.

## Output files
The analyzer generates:
- `demand_ranking.csv` — ranked needs with inquiry/customer coverage and score.
- `demand_matrix.csv` — segment-by-demand counts and rates.
- `product_opportunities.md` — evidence-based product opportunity hypotheses.
- `supplier_capabilities.md` — supplier capability and operational recommendations.
- `analysis_summary.json` — machine-readable metrics, configuration and run metadata.

## Interpretation rules
- Frequency is not the same as willingness to pay, urgency, or profitability.
- A buyer mentioning a feature is not proof that the buyer will purchase it.
- Do not merge distinct concepts just because they share a keyword.
- A single buyer sending multiple emails must not inflate unique-customer coverage.
- Separate explicit matches from inferred matches. The included baseline extractor is rule-based and transparent; use an LLM adapter only as an optional enhancement.
- For small samples, show counts and mark rates as directional. Do not overstate statistical significance.
- Never infer sensitive personal attributes. Analyze business requirements only.
- Do not fabricate customer identities, purchase volumes, supplier relationships, prices, or certifications.
- Preserve source IDs and evidence snippets so findings can be audited.

## Customization
Edit:
- `config/demand-taxonomy.yaml` to add industries, categories, synonyms, and supplier capability mappings.
- `config/scoring.yaml` to change weights and trend windows.
- `config/customer-segments.yaml` to add segment labels and normalization aliases.

The taxonomy is intentionally data-driven. Do not hard-code industry assumptions into the scripts.

## Recommended extension points
- Add an XLSX adapter using `openpyxl`.
- Add multilingual synonym dictionaries.
- Add an LLM extraction adapter that returns the same schema as `demand_extractor.py`, with source evidence and confidence.
- Add CRM/email connectors as separate adapters. Keep authentication and data retrieval outside the core analyzer.
- Add database storage (SQLite/PostgreSQL) behind a repository interface when the inquiry volume requires it.

## Quality assurance
Before using results commercially:
1. Review the top 20 extracted needs and their evidence.
2. Confirm customer-level deduplication.
3. Inspect unknown/unmatched inquiries.
4. Compare results across relevant customer segments.
5. Treat opportunity and supplier recommendations as hypotheses until validated with buyers or sales data.
