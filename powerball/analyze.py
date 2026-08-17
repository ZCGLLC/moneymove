from __future__ import annotations

from collections import Counter

from powerball.models import POWERBALL_MAX, WHITE_MAX, Analysis, Draw


def analyze(draws: list[Draw]) -> Analysis:
    if not draws:
        raise ValueError("no draws to analyze")

    current = [draw for draw in draws if draw.is_current_format]
    era = current or draws

    white_all = Counter()
    pb_all = Counter()
    for draw in draws:
        white_all.update(n for n in draw.white if 1 <= n <= WHITE_MAX)
        if 1 <= draw.powerball <= POWERBALL_MAX:
            pb_all[draw.powerball] += 1

    white_cur = Counter()
    pb_cur = Counter()
    for draw in era:
        white_cur.update(n for n in draw.white if 1 <= n <= WHITE_MAX)
        if 1 <= draw.powerball <= POWERBALL_MAX:
            pb_cur[draw.powerball] += 1

    white_overdue = _overdue_counts(era, "white")
    pb_overdue = _overdue_counts(era, "powerball")

    odd_counts = Counter(draw.odd_count for draw in era)
    high_counts = Counter(draw.high_count for draw in era)
    typical_odd = tuple(sorted(k for k, _ in odd_counts.most_common(2)))  # type: ignore[assignment]
    typical_high = tuple(sorted(k for k, _ in high_counts.most_common(2)))  # type: ignore[assignment]
    if len(typical_odd) != 2:
        typical_odd = (2, 3)
    if len(typical_high) != 2:
        typical_high = (2, 3)

    sums = sorted(draw.white_sum for draw in era)
    p10 = sums[max(0, len(sums) // 10)]
    p90 = sums[min(len(sums) - 1, (9 * len(sums)) // 10)]
    mean_sum = sum(sums) / len(sums)
    consec = sum(1 for draw in era if draw.has_consecutive) / len(era)

    return Analysis(
        total_draws=len(draws),
        current_format_draws=len(current),
        first_draw=draws[0].draw_date,
        last_draw=draws[-1].draw_date,
        white_freq_current=_ranked(white_cur, range(1, WHITE_MAX + 1)),
        white_freq_all=_ranked(white_all, range(1, WHITE_MAX + 1)),
        powerball_freq_current=_ranked(pb_cur, range(1, POWERBALL_MAX + 1)),
        powerball_freq_all=_ranked(pb_all, range(1, POWERBALL_MAX + 1)),
        overdue_white=sorted(white_overdue.items(), key=lambda item: (-item[1], item[0])),
        overdue_powerball=sorted(pb_overdue.items(), key=lambda item: (-item[1], item[0])),
        recent_draws=list(reversed(draws[-12:])),
        typical_odd=(int(typical_odd[0]), int(typical_odd[1])),
        typical_high=(int(typical_high[0]), int(typical_high[1])),
        typical_sum=(p10, p90, round(mean_sum, 1)),
        consecutive_rate=round(consec, 3),
    )


def recency_weights(draws: list[Draw], *, half_life: int = 180) -> tuple[list[float], list[float]]:
    """Exponential recency weights for current-format white balls and Powerballs."""
    white = [0.0] * (WHITE_MAX + 1)
    power = [0.0] * (POWERBALL_MAX + 1)
    era = [draw for draw in draws if draw.is_current_format] or draws
    decay = 0.5 ** (1 / half_life)
    weight = 1.0
    for draw in reversed(era):
        for number in draw.white:
            if 1 <= number <= WHITE_MAX:
                white[number] += weight
        if 1 <= draw.powerball <= POWERBALL_MAX:
            power[draw.powerball] += weight
        weight *= decay
    return white, power


def pair_counts(draws: list[Draw]) -> dict[tuple[int, int], int]:
    counts: dict[tuple[int, int], int] = {}
    era = [draw for draw in draws if draw.is_current_format] or draws
    for draw in era:
        balls = [n for n in draw.white if 1 <= n <= WHITE_MAX]
        for i, left in enumerate(balls):
            for right in balls[i + 1 :]:
                key = (left, right) if left < right else (right, left)
                counts[key] = counts.get(key, 0) + 1
    return counts


def last_seen_gaps(draws: list[Draw], kind: str) -> dict[int, int]:
    era = [draw for draw in draws if draw.is_current_format] or draws
    limit = WHITE_MAX if kind == "white" else POWERBALL_MAX
    gaps = {n: len(era) for n in range(1, limit + 1)}
    for offset, draw in enumerate(reversed(era)):
        values = draw.white if kind == "white" else (draw.powerball,)
        for number in values:
            if 1 <= number <= limit and gaps[number] == len(era):
                gaps[number] = offset
    return gaps


def _overdue_counts(era: list[Draw], kind: str) -> dict[int, int]:
    return last_seen_gaps(era, kind)


def _ranked(counter: Counter, domain) -> list[tuple[int, int]]:
    return sorted(((n, int(counter.get(n, 0))) for n in domain), key=lambda item: (-item[1], item[0]))
