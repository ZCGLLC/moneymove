from __future__ import annotations

import csv
import json
from datetime import date, datetime
from pathlib import Path

import requests

from powerball.models import NY_OPEN_DATA_START, Draw, parse_white

ROOT = Path(__file__).resolve().parent.parent
HISTORICAL_CSV = ROOT / "data" / "historical_1992_2010.csv"
GAP_CSV = ROOT / "data" / "ny_open_data_gaps.csv"
CACHE_PATH = ROOT / "data" / "ny_cache.json"
NY_API = "https://data.ny.gov/resource/d6yy-54nr.json"
FETCH_LIMIT = 50000


def load_all_draws(*, refresh: bool = False, timeout: float = 20.0) -> list[Draw]:
    """Merge 1992–2010 archive with NY Open Data (2010–present)."""
    draws: dict[date, Draw] = {}
    for draw in _load_historical():
        draws[draw.draw_date] = draw
    for draw in _load_ny(refresh=refresh, timeout=timeout):
        draws[draw.draw_date] = draw
    return sorted(draws.values(), key=lambda d: d.draw_date)


def _load_historical() -> list[Draw]:
    return _read_archive(HISTORICAL_CSV) + _read_archive(GAP_CSV)


def _read_archive(path: Path) -> list[Draw]:
    if not path.exists():
        return []
    out: list[Draw] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            draw_date = date.fromisoformat(row["date"])
            white = parse_white([row["n1"], row["n2"], row["n3"], row["n4"], row["n5"]])
            multiplier = int(row["multiplier"]) if row.get("multiplier") else None
            out.append(Draw(draw_date, white, int(row["powerball"]), multiplier))
    return out


def _load_ny(*, refresh: bool, timeout: float) -> list[Draw]:
    if refresh or not CACHE_PATH.exists():
        try:
            fetched = _fetch_ny(timeout=timeout)
            _write_cache(fetched)
            return fetched
        except (requests.RequestException, ValueError, KeyError, OSError, json.JSONDecodeError):
            if CACHE_PATH.exists():
                return _read_cache()
            return []
    return _read_cache()


def _fetch_ny(*, timeout: float) -> list[Draw]:
    response = requests.get(
        NY_API,
        params={"$limit": FETCH_LIMIT, "$order": "draw_date"},
        timeout=timeout,
        headers={"Accept": "application/json", "User-Agent": "moneymove-powerball/1.0"},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or not payload:
        raise ValueError("NY Open Data returned no Powerball draws")
    out: list[Draw] = []
    for row in payload:
        draw_date = datetime.fromisoformat(row["draw_date"].replace("Z", "")).date()
        if draw_date < NY_OPEN_DATA_START:
            continue
        numbers = [int(part) for part in str(row["winning_numbers"]).split()]
        if len(numbers) != 6:
            continue
        multiplier = None
        raw_mult = row.get("multiplier")
        if raw_mult not in (None, ""):
            multiplier = int(raw_mult)
        out.append(Draw(draw_date, parse_white(numbers[:5]), numbers[5], multiplier))
    if not out:
        raise ValueError("NY Open Data contained no parseable draws")
    return out


def _write_cache(draws: list[Draw]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "date": draw.draw_date.isoformat(),
            "white": list(draw.white),
            "powerball": draw.powerball,
            "multiplier": draw.multiplier,
        }
        for draw in draws
    ]
    CACHE_PATH.write_text(json.dumps(payload), encoding="utf-8")


def _read_cache() -> list[Draw]:
    payload = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return [
        Draw(
            date.fromisoformat(row["date"]),
            parse_white(row["white"]),
            int(row["powerball"]),
            row.get("multiplier"),
        )
        for row in payload
    ]
