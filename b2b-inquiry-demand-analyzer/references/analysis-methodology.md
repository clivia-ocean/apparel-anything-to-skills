# Analysis methodology

## Unit of analysis
- Inquiry-level counts: unique `inquiry_id`.
- Customer coverage: unique `customer_id`, not number of mentions.
- Segment matrix: unique customers per segment and demand.

## Priority score
Weighted score (0–100):
`coverage × 0.40 + explicitness × 0.20 + commercial_importance × 0.25 + trend × 0.15`.

The default extractor only emits explicit phrase matches, so explicitness is 100 for a matched item. If an LLM adapter is added, use lower explicitness for inferred needs and preserve a rationale/evidence field.

## Trend
The most recent inquiry date in the dataset is the anchor. The configured recent window is compared with the preceding window. If no usable dates or no mentions in either period exist, trend is neutral (50).

## Cautions
- Dataset date span and volume affect trend reliability.
- Keyword extraction can miss paraphrases and negation. For example, “we do not need custom printing” should not count as positive demand; review and extend the extractor to handle negation.
- A request may reflect a one-off project rather than broad market demand.
- Validate with quote conversion, order value, gross margin, repeat orders and win/loss reasons.
