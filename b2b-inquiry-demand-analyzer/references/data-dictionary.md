# Canonical inquiry data dictionary

| Field | Type | Required | Description |
|---|---|---:|---|
| inquiry_id | string | recommended | Unique inquiry identifier; deterministic fallback generated |
| customer_id | string | recommended | Stable buyer/company key used for unique-customer counts |
| customer_name | string | no | Buyer/company name |
| email | string | no | Business contact email; do not expose in aggregate reports |
| website | string | no | Company website |
| country | string | no | Buyer market/country |
| customer_segment | string | no | DTC brand, retailer, wholesaler, importer, etc. |
| product_category | string | no | Product family |
| inquiry_date | ISO date | no | Date used for trend analysis |
| subject | string | no | Email subject |
| body | string | yes* | Inquiry text |
| source | string | no | Email, web form, trade show, CRM, etc. |
| language | string | no | Language tag |

*At least one of subject/body must contain text.
