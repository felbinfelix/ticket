
# Daily Ticket Monitor for Freshdesk

## Overview

This tool tracks unresolved Freshdesk tickets daily, detects changes, and updates your master ticket list.

## Structure

- `full_export.py`: Fetches all unresolved tickets using the Search API with daily chunking and stores them in `all_unresolved_tickets_full.csv`.
- `daily_sync.py`: Compares the latest unresolved tickets with the master list and detects:
  - New tickets
  - Closed tickets

## Files Generated

- `all_unresolved_tickets_full.csv` — full master dataset
- `today_unresolved_tickets.csv` — today's snapshot
- `new_tickets_today.csv` — new unresolved tickets today
- `closed_tickets_today.csv` — tickets that got resolved or removed today

## Usage

1. Run `full_export.py` periodically (e.g. weekly):
```bash
python full_export.py
```

2. Run `daily_sync.py` every day (via cron or manually):
```bash
python daily_sync.py
```
