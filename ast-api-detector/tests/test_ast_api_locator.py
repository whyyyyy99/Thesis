import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ast_api_locator import build_maps_from_json, extract_pandas_api_details


class DetectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maps = build_maps_from_json(
            str(ROOT / "data/registry/pandas_source_api_registry.json")
        )

    def detect(self, code):
        return extract_pandas_api_details(code, maps=self.maps)

    def test_alias_and_dataframe_chain(self):
        result = self.detect("import pandas as pd\ndf = pd.read_csv('x.csv')\ndf.dropna()")
        self.assertIn("pandas.read_csv", result["normalized_apis"])
        self.assertIn("pandas.DataFrame.dropna", result["normalized_apis"])

    def test_series_selection(self):
        result = self.detect("df['value'].fillna(0)")
        self.assertIn("pandas.Series.fillna", result["normalized_apis"])

    def test_non_pandas_module_is_excluded(self):
        result = self.detect("import itertools\nitertools.groupby(values)")
        self.assertEqual(result["normalized_apis"], [])

    def test_parse_failure(self):
        result = self.detect("df.dropna(")
        self.assertFalse(result["parse_success"])


if __name__ == "__main__":
    unittest.main()
