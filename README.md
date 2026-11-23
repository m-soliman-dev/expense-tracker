# expense-tracker

A command-line ledger for a small business or personal budget. Record income
and expenses, then get a monthly report with totals, profit and a breakdown of
where the money went. Pure Python 3, no packages to install.

## What it does

- Records income and expense entries with a category, note and date
- Stores everything in a JSON file in your home folder, so nothing is lost
- Prints a monthly report: total income, total expenses, profit, and spending
  per category sorted from largest to smallest
- Lists every entry for a month so you can review the details

## Usage

```bash
# Record entries
python expense_tracker.py add income 5000 sales --note "market day"
python expense_tracker.py add expense 250 groceries
python expense_tracker.py add expense 1200 rent --date 2026-11-01

# See the report for November 2026
python expense_tracker.py report --month 2026-11

# List the entries behind the numbers
python expense_tracker.py list --month 2026-11
```

Example report:

```
Report for 2026-11
  income:      5000.00
  expenses:    1450.00
  profit:      3550.00
  expenses by category:
    rent                   1200.00
    groceries               250.00
```

## Running the tests

```bash
python -m unittest test_expense_tracker.py -v
```

## What I learned building this

- Modelling a small domain (a ledger) as a Python class with validation
- Persisting data safely as JSON between runs
- Aggregating data with `collections.defaultdict`
- Building subcommands with `argparse`
