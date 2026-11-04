from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from rank_skills import norm_log, parse_date


class RankingTests(unittest.TestCase):
    def test_norm_log_is_bounded(self):
        values = norm_log([0, 1, 10, 100])
        self.assertEqual(len(values), 4)
        self.assertAlmostEqual(values[0], 0.0)
        self.assertAlmostEqual(values[-1], 1.0)
        self.assertTrue(all(0.0 <= value <= 1.0 for value in values))

    def test_norm_log_handles_empty_and_constant_values(self):
        self.assertEqual(norm_log([]), [])
        self.assertEqual(norm_log([5, 5, 5]), [0.0, 0.0, 0.0])

    def test_norm_log_handles_negative_values_as_zero(self):
        self.assertEqual(norm_log([-5, 0]), [0.0, 0.0])

    def test_parse_date_accepts_github_timestamp(self):
        parsed = parse_date("2026-11-04T00:00:00Z")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.utcoffset().total_seconds(), 0)

    def test_parse_date_rejects_invalid_input(self):
        self.assertIsNone(parse_date(None))
        self.assertIsNone(parse_date("not-a-date"))


if __name__ == "__main__":
    unittest.main()
