#!/usr/bin/env python3
"""expense-tracker - record income and expenses, see where the money goes.

A command-line ledger for a small business or personal budget. Entries are
stored in a JSON file, and the report command shows totals, profit and a
per-category breakdown for any month.

Usage:
    python expense_tracker.py add expense 250 groceries --note "weekly shop"
    python expense_tracker.py add income 5000 sales --date 2026-11-01
    python expense_tracker.py report --month 2026-11
    python expense_tracker.py list --month 2026-11
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

STORE = Path.home() / ".expense_tracker.json"
KINDS = ("income", "expense")


class Ledger:
    """A list of income/expense entries backed by a JSON file."""

    def __init__(self, path=STORE):
        self.path = Path(path)
        self.entries = self._load()

    def _load(self):
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                raise SystemExit(f"error: {self.path} is corrupted")
        return []

    def save(self):
        self.path.write_text(json.dumps(self.entries, indent=2),
                             encoding="utf-8")

    def add(self, kind, amount, category, note="", entry_date=None):
        if kind not in KINDS:
            raise ValueError(f"kind must be one of {KINDS}")
        if amount <= 0:
            raise ValueError("amount must be positive")
        entry = {
            "kind": kind,
            "amount": round(float(amount), 2),
            "category": category.strip().lower(),
            "note": note,
            "date": entry_date or date.today().isoformat(),
        }
        self.entries.append(entry)
        return entry

    def for_month(self, month):
        """Entries whose date starts with YYYY-MM (all entries if month is None)."""
        if month is None:
            return list(self.entries)
        return [e for e in self.entries if e["date"].startswith(month)]

    def report(self, month=None):
        """Totals, profit and per-category sums for the given month."""
        entries = self.for_month(month)
        income = sum(e["amount"] for e in entries if e["kind"] == "income")
        expenses = sum(e["amount"] for e in entries if e["kind"] == "expense")
        by_category = defaultdict(float)
        for entry in entries:
            if entry["kind"] == "expense":
                by_category[entry["category"]] += entry["amount"]
        return {
            "income": round(income, 2),
            "expenses": round(expenses, 2),
            "profit": round(income - expenses, 2),
            "by_category": {k: round(v, 2) for k, v in
                            sorted(by_category.items(),
                                   key=lambda item: item[1], reverse=True)},
        }


def cmd_add(args):
    ledger = Ledger()
    try:
        entry = ledger.add(args.kind, args.amount, args.category,
                           note=args.note, entry_date=args.date)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    ledger.save()
    print(f"added {entry['kind']}: {entry['amount']:.2f} "
          f"[{entry['category']}] on {entry['date']}")
    return 0


def cmd_report(args):
    report = Ledger().report(month=args.month)
    period = args.month or "all time"
    print(f"Report for {period}")
    print(f"  income:   {report['income']:>10.2f}")
    print(f"  expenses: {report['expenses']:>10.2f}")
    print(f"  profit:   {report['profit']:>10.2f}")
    if report["by_category"]:
        print("  expenses by category:")
        for category, total in report["by_category"].items():
            print(f"    {category:<20} {total:>10.2f}")
    return 0


def cmd_list(args):
    entries = Ledger().for_month(args.month)
    if not entries:
        print("no entries")
        return 0
    for entry in entries:
        note = f" - {entry['note']}" if entry["note"] else ""
        print(f"{entry['date']}  {entry['kind']:<8} {entry['amount']:>10.2f}  "
              f"{entry['category']}{note}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="record an income or expense")
    add.add_argument("kind", choices=KINDS)
    add.add_argument("amount", type=float)
    add.add_argument("category")
    add.add_argument("--note", default="")
    add.add_argument("--date", help="YYYY-MM-DD (default: today)")
    add.set_defaults(func=cmd_add)

    for name, func, help_text in [
            ("report", cmd_report, "totals, profit and category breakdown"),
            ("list", cmd_list, "list entries")]:
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--month", help="YYYY-MM (default: all time)")
        command.set_defaults(func=func)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
