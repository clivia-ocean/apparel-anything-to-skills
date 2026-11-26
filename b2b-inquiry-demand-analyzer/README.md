# B2B Inquiry Demand Analyzer

A standalone, extensible Skill package for batch and incremental analysis of B2B inquiries.

## Requirements
- Python 3.9+
- Python package `PyYAML` for reading the YAML configuration files.

Install dependency:
```bash
pip install pyyaml
```

## Quick start
```bash
python scripts/analyze.py --input examples/sample-inquiries.csv --out output
```

For JSON input:
```bash
python scripts/analyze.py --input examples/sample-inquiries.jsonl --out output
```

Incremental append:
```bash
python scripts/analyze.py --input examples/new-inquiries.csv --store data/inquiries.csv --append --out output
```

## CSV format
Required:
- `body` or `subject`

Recommended:
- `inquiry_id`, `customer_id`, `customer_name`, `country`, `customer_segment`,
  `product_category`, `inquiry_date`, `subject`, `body`, `source`, `language`

See `examples/sample-inquiries.csv`.

## Reports
| File | Purpose |
|---|---|
| `demand_ranking.csv` | Most requested needs, unique inquiry/customer counts, priority score |
| `demand_matrix.csv` | Demand distribution by country, segment, and product category |
| `product_opportunities.md` | Product and assortment opportunities, explicitly labeled as hypotheses |
| `supplier_capabilities.md` | Factory/supplier capability priorities |
| `analysis_summary.json` | Machine-readable run details and metrics |

## Scoring
Default weights are configured in `config/scoring.yaml`:
- unique-customer coverage: 40%
- explicitness: 20%
- commercial importance: 25%
- recent trend: 15%

Scores are normalized to 0–100. The baseline trend component compares the recent window with the previous window. If date coverage is insufficient, the trend component is neutral rather than fabricated.

## Important limitations
The included extractor is a transparent keyword/phrase baseline, not a semantic language model. It supports English and selected Chinese terms in the default apparel taxonomy. Add synonyms to YAML for your actual markets and terminology. For production use, review extracted evidence and consider an optional LLM extraction adapter.

## Suggested workflow
1. Export historical inquiries from email/CRM.
2. Map columns to the canonical schema.
3. Run batch analysis.
4. Review top-ranked needs and evidence.
5. Add new inquiries to the store and run incremental mode.
6. Validate product opportunities with sales, quote conversion, win/loss and margin data.

## License
MIT. See `LICENSE`.
