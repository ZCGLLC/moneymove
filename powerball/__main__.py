from __future__ import annotations

import argparse
import json
from datetime import date, datetime

from powerball.data import load_all_draws
from powerball.generate import fingerprint_visitor, generate_daily_picks


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 3 daily Powerball sets from historical draws.")
    parser.add_argument("--date", help="Pick date YYYY-MM-DD (default: today)")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a ticket view")
    parser.add_argument("--refresh", action="store_true", help="Refresh NY Open Data cache")
    parser.add_argument("--ip", help="Visitor IP used to make this user's tickets unique")
    parser.add_argument("--generation", type=int, default=1, help="Generation round for additional unique sets")
    args = parser.parse_args()
    pick_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    draws = load_all_draws(refresh=args.refresh)
    user_key = fingerprint_visitor(args.ip) if args.ip else None
    payload = generate_daily_picks(draws, pick_date, user_key=user_key, generation=args.generation)
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
