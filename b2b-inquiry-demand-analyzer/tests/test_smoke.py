import unittest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from common import normalize_records
from demand_extractor import load_taxonomy, extract

class SmokeTest(unittest.TestCase):
    def test_dedup_and_extract(self):
        records = normalize_records([
            {"inquiry_id":"1","customer_id":"c1","body":"Need breathable modal loungewear and low MOQ"},
            {"inquiry_id":"1","customer_id":"c1","body":"Need breathable modal loungewear and low MOQ"}
        ])
        taxonomy = load_taxonomy(Path(__file__).resolve().parents[1] / "config" / "demand-taxonomy.yaml")
        matches = extract(records, taxonomy)
        self.assertEqual(len(records), 1)
        self.assertTrue(any(m["demand_id"] == "fabric_material" for m in matches))
        self.assertTrue(any(m["demand_id"] == "minimum_order" for m in matches))

if __name__ == "__main__":
    unittest.main()
