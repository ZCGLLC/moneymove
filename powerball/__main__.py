from __future__ import annotations

import argparse
import json
from datetime import date, datetime

from powerball.data import load_all_draws
from powerball.generate import generate_daily_picks


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 3 daily Powerball sets from historical draws.")
    parser.add_argument("--date", help="Pick date YYYY-MM-DD (default: today)")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a ticket view")
    parser.add_argument("--refresh", action="store_true", help="Refresh NY Open Data cache")
    args = parser.parse_args()
    pick_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    draws = load_all_draws(refresh=args.refresh)
    payload = generate_daily_picks(draws, pick_date)
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(f"Powerball daily picks for {payload['pick_date']}")
    print(f"Analyzed {payload['analyzed_draws']} draws ({payload['first_draw']} – {payload['last_draw']})")
    print(f"Next drawing: {payload['next_draw']}")
    print()
    for ticket in payload["tickets"]:
        whites = " ".join(f"{n:02d}" for n in ticket["white"])
        print(f"{ticket['name']}: {whites}  PB {ticket['powerball']:02d}")
        print(f"  {ticket['summary']}")
        print()
    print(payload["disclaimer"])


if __name__ == "__main__":
    main()
