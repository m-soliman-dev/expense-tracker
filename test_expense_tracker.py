import tempfile
import unittest
from pathlib import Path

from expense_tracker import Ledger


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.ledger = Ledger(Path(self.folder.name) / "store.json")

    def tearDown(self):
        self.folder.cleanup()

    def test_add_and_persist(self):
        self.ledger.add("income", 1000, "sales", entry_date="2026-11-01")
        self.ledger.save()
        reloaded = Ledger(self.ledger.path)
        self.assertEqual(len(reloaded.entries), 1)
        self.assertEqual(reloaded.entries[0]["amount"], 1000.0)

    def test_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            self.ledger.add("expense", -5, "food")
        with self.assertRaises(ValueError):
            self.ledger.add("gift", 5, "food")

    def test_report_profit_and_categories(self):
        self.ledger.add("income", 5000, "sales", entry_date="2026-11-01")
        self.ledger.add("income", 500, "sales", entry_date="2026-11-03")
        self.ledger.add("expense", 200, "rent", entry_date="2026-11-02")
        self.ledger.add("expense", 50, "food", entry_date="2026-11-02")
        self.ledger.add("expense", 30, "food", entry_date="2026-11-04")
        self.ledger.add("expense", 999, "rent", entry_date="2026-10-01")
        report = self.ledger.report(month="2026-11")
        self.assertEqual(report["income"], 5500.0)
        self.assertEqual(report["expenses"], 280.0)
        self.assertEqual(report["profit"], 5220.0)
        self.assertEqual(report["by_category"]["food"], 80.0)
        self.assertEqual(report["by_category"]["rent"], 200.0)

    def test_month_filtering(self):
        self.ledger.add("expense", 10, "food", entry_date="2026-10-31")
        self.ledger.add("expense", 20, "food", entry_date="2026-11-01")
        self.assertEqual(len(self.ledger.for_month("2026-11")), 1)
        self.assertEqual(len(self.ledger.for_month(None)), 2)


if __name__ == "__main__":
    unittest.main()
