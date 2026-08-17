from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from powerball.data import load_all_draws

OUT = ROOT / "docs" / "draws.json"


def main() -> None:
    refresh = os.environ.get("EXPORT_REFRESH", "1") != "0"
    draws = load_all_draws(refresh=refresh)
    payload = [
        {
            "date": draw.draw_date.isoformat(),
            "white": list(draw.white),
            "powerball": draw.powerball,
            "multiplier": draw.multiplier,
        }
        for draw in draws
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {len(payload)} draws to {OUT}")


if __name__ == "__main__":
    main()
