from __future__ import annotations

import hashlib
import random
from datetime import date

from powerball.analyze import analyze, last_seen_gaps, pair_counts, recency_weights
from powerball.models import POWERBALL_MAX, WHITE_MAX, Draw, TicketSet

STRATEGIES = (
    {
        "key": "hot",
        "name": "Hot Frequency",
        "summary": "Weighted toward numbers that appear most often in the current 5/69 + 1/26 format, with extra credit for recent draws and all-time history.",
        "freq": 0.62,
        "recency": 0.28,
        "overdue": 0.05,
        "all_time": 0.05,
        "pair": 0.22,
        "shape": False,
    },
    {
        "key": "due",
        "name": "Overdue",
        "summary": "Weighted toward current-format numbers that have gone longer than usual without being drawn, blended with long-run frequency so cold numbers are not pure guesses.",
        "freq": 0.18,
        "recency": 0.10,
        "overdue": 0.62,
        "all_time": 0.10,
        "pair": 0.08,
        "shape": False,
    },
    {
        "key": "balanced",
        "name": "Balanced Pattern",
        "summary": "Blends hot, overdue, and all-time counts, then keeps tickets that match how real jackpot draws usually look: mixed odd/even, mixed high/low, and a typical white-ball sum.",
        "freq": 0.34,
        "recency": 0.22,
        "overdue": 0.24,
        "all_time": 0.20,
        "pair": 0.16,
        "shape": True,
    },
)


def fingerprint_visitor(ip: str) -> str:
    """Stable visitor key from an IP address. The raw IP is not stored."""
    normalized = (ip or "").split("%", 1)[0].strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def generate_daily_picks(
    draws: list[Draw],
    pick_date: date | None = None,
    *,
    user_key: str | None = None,
    generation: int = 1,
) -> dict:
    if not draws:
        raise ValueError("no historical draws available")
    pick_date = pick_date or date.today()
    generation = max(1, int(generation))
    stats = analyze(draws)
    white_w, pb_w = recency_weights(draws)
    pairs = pair_counts(draws)
    white_gap = last_seen_gaps(draws, "white")
    pb_gap = last_seen_gaps(draws, "powerball")

    white_freq = {n: c for n, c in stats.white_freq_current}
    white_all = {n: c for n, c in stats.white_freq_all}
    pb_freq = {n: c for n, c in stats.powerball_freq_current}
    pb_all = {n: c for n, c in stats.powerball_freq_all}

    used: set[tuple[tuple[int, ...], int]] = {(draw.white, draw.powerball) for draw in draws}
    tickets: list[TicketSet] = []
    for strategy in STRATEGIES:
        rng = _rng(pick_date, strategy["key"], user_key, generation)
        ticket = _pick_ticket(
            rng,
            strategy,
            white_freq,
            white_all,
            white_w,
            white_gap,
            pb_freq,
            pb_all,
            pb_w,
            pb_gap,
            pairs,
            stats,
            used,
        )
        used.add((ticket.white, ticket.powerball))
        tickets.append(ticket)

    return {
        "pick_date": pick_date.isoformat(),
        "next_draw": _next_draw_date(pick_date).isoformat(),
        "generation": generation,
        "visitor_keyed": bool(user_key),
        "analyzed_draws": stats.total_draws,
        "current_format_draws": stats.current_format_draws,
        "first_draw": stats.first_draw.isoformat(),
        "last_draw": stats.last_draw.isoformat(),
        "disclaimer": (
            "Powerball drawings are random. Past results do not change the odds of any "
            "future combination. These sets are statistical entertainment picks, not a guarantee."
        ),
        "tickets": [
            {
                "key": t.key,
                "name": t.name,
                "summary": t.summary,
                "white": list(t.white),
                "powerball": t.powerball,
            }
            for t in tickets
        ],
        "stats": _public_stats(stats),
    }


def _pick_ticket(
    rng: random.Random,
    strategy: dict,
    white_freq: dict[int, int],
    white_all: dict[int, int],
    white_recency: list[float],
    white_gap: dict[int, int],
    pb_freq: dict[int, int],
    pb_all: dict[int, int],
    pb_recency: list[float],
    pb_gap: dict[int, int],
    pairs: dict[tuple[int, int], int],
    stats,
    used: set[tuple[tuple[int, ...], int]],
) -> TicketSet:
    white_base = _blend_weights(
        WHITE_MAX,
        white_freq,
        white_all,
        white_recency,
        white_gap,
        stats.current_format_draws or stats.total_draws,
        strategy,
    )
    pb_base = _blend_weights(
        POWERBALL_MAX,
        pb_freq,
        pb_all,
        pb_recency,
        pb_gap,
        stats.current_format_draws or stats.total_draws,
        strategy,
    )

    best: tuple[int, ...] | None = None
    best_pb = 1
    best_score = -1.0
    attempts = 80 if strategy["shape"] else 24
    for attempt in range(attempts):
        white = _sample_whites(rng, white_base, pairs, float(strategy["pair"]))
        powerball = _weighted_choice(rng, pb_base)
        key = (white, powerball)
        if key in used:
            continue
        score = 1.0
        if strategy["shape"]:
            score = _shape_score(white, stats)
            if score < 0.55 and attempt < attempts - 1:
                continue
        if score > best_score:
            best_score = score
            best = white
            best_pb = powerball
            if not strategy["shape"] or score >= 0.92:
                break

    if best is None:
        white = _sample_whites(rng, white_base, pairs, float(strategy["pair"]))
        best = white
        best_pb = _weighted_choice(rng, pb_base)

    return TicketSet(
        key=strategy["key"],
        name=strategy["name"],
        summary=strategy["summary"],
        white=best,  # type: ignore[arg-type]
        powerball=best_pb,
    )


def _blend_weights(
    limit: int,
    freq: dict[int, int],
    all_time: dict[int, int],
    recency: list[float],
    gaps: dict[int, int],
    era_draws: int,
    strategy: dict,
) -> list[float]:
    freq_n = _normalize([float(freq.get(n, 0)) for n in range(limit + 1)])
    all_n = _normalize([float(all_time.get(n, 0)) for n in range(limit + 1)])
    rec_n = _normalize(list(recency[: limit + 1]) if len(recency) > limit else recency + [0.0] * (limit + 1 - len(recency)))
    overdue = [0.0] * (limit + 1)
    for n in range(1, limit + 1):
        expected = era_draws / max(freq.get(n, 0), 1)
        overdue[n] = min(4.0, gaps.get(n, era_draws) / max(expected, 1.0))
    over_n = _normalize(overdue)
    weights = [0.0] * (limit + 1)
    for n in range(1, limit + 1):
        weights[n] = (
            strategy["freq"] * freq_n[n]
            + strategy["recency"] * rec_n[n]
            + strategy["overdue"] * over_n[n]
            + strategy["all_time"] * all_n[n]
            + 0.02
        )
    return weights


def _sample_whites(
    rng: random.Random,
    base: list[float],
    pairs: dict[tuple[int, int], int],
    pair_boost: float,
) -> tuple[int, ...]:
    weights = base[:]
    chosen: list[int] = []
    for _ in range(5):
        number = _weighted_choice(rng, weights)
        chosen.append(number)
        weights[number] = 0.0
        if pair_boost and chosen:
            for other in range(1, WHITE_MAX + 1):
                if weights[other] <= 0:
                    continue
                key = (number, other) if number < other else (other, number)
                weights[other] *= 1.0 + pair_boost * (pairs.get(key, 0) / 40.0)
    return tuple(sorted(chosen))


def _shape_score(white: tuple[int, ...], stats) -> float:
    odd = sum(n % 2 for n in white)
    high = sum(n >= 36 for n in white)
    total = sum(white)
    score = 0.0
    score += 0.34 if odd in stats.typical_odd else (0.12 if odd in (1, 4) else 0.0)
    score += 0.34 if high in stats.typical_high else (0.12 if high in (1, 4) else 0.0)
    low, high_sum, mean = stats.typical_sum
    if low <= total <= high_sum:
        score += 0.32
    else:
        score += max(0.0, 0.32 - abs(total - mean) / 250.0)
    return score


def _weighted_choice(rng: random.Random, weights: list[float]) -> int:
    total = sum(weights[1:])
    if total <= 0:
        return rng.randint(1, len(weights) - 1)
    pick = rng.random() * total
    running = 0.0
    last = 1
    for number, weight in enumerate(weights[1:], start=1):
        if weight <= 0:
            continue
        running += weight
        last = number
        if running >= pick:
            return number
    return last


def _normalize(values: list[float]) -> list[float]:
    out = list(values)
    if not out:
        return out
    out[0] = 0.0
    peak = max(out) if out else 0.0
    if peak <= 0:
        return [0.0 if i == 0 else 1.0 for i in range(len(out))]
    return [v / peak for v in out]


def _rng(pick_date: date, key: str, user_key: str | None, generation: int) -> random.Random:
    visitor = user_key or "anon"
    material = f"moneymove-powerball|{pick_date.isoformat()}|{visitor}|{generation}|{key}|v2".encode()
    seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    return random.Random(seed)


def _next_draw_date(day: date) -> date:
    weekday = day.weekday()  # Mon=0
    for offset in range(0, 8):
        candidate = date.fromordinal(day.toordinal() + offset)
        if candidate.weekday() in (0, 2, 5):
            return candidate
    return day


def _public_stats(stats) -> dict:
    return {
        "total_draws": stats.total_draws,
        "current_format_draws": stats.current_format_draws,
        "first_draw": stats.first_draw.isoformat(),
        "last_draw": stats.last_draw.isoformat(),
        "hottest_white": stats.white_freq_current[:10],
        "coldest_white": list(reversed(stats.white_freq_current[-10:])),
        "hottest_powerball": stats.powerball_freq_current[:8],
        "coldest_powerball": list(reversed(stats.powerball_freq_current[-6:])),
        "overdue_white": stats.overdue_white[:10],
        "overdue_powerball": stats.overdue_powerball[:6],
        "hottest_white_all_time": stats.white_freq_all[:10],
        "hottest_powerball_all_time": stats.powerball_freq_all[:8],
        "typical_odd": list(stats.typical_odd),
        "typical_high": list(stats.typical_high),
        "typical_sum": {
            "p10": stats.typical_sum[0],
            "p90": stats.typical_sum[1],
            "mean": stats.typical_sum[2],
        },
        "consecutive_rate": stats.consecutive_rate,
        "recent_draws": [
            {
                "date": draw.draw_date.isoformat(),
                "white": list(draw.white),
                "powerball": draw.powerball,
                "multiplier": draw.multiplier,
            }
            for draw in stats.recent_draws
        ],
    }
