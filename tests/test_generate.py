from datetime import date

from powerball.generate import fingerprint_visitor, generate_daily_picks
from tests.conftest import make_draw


def _history():
    draws = [make_draw(1992, 4, 22, [2, 25, 35, 41, 42], 15)]
    whites = [
        [5, 12, 23, 44, 61],
        [8, 21, 28, 36, 64],
        [3, 19, 27, 48, 63],
        [11, 21, 32, 55, 69],
        [7, 16, 28, 41, 61],
        [4, 23, 36, 47, 64],
        [9, 18, 27, 50, 63],
        [6, 21, 33, 44, 68],
        [10, 24, 32, 51, 61],
        [13, 22, 39, 56, 64],
        [1, 15, 28, 42, 67],
        [14, 21, 36, 53, 69],
        [2, 17, 29, 45, 61],
        [8, 20, 34, 48, 62],
        [12, 23, 37, 49, 65],
    ]
    start = date(2015, 10, 7)
    for index, white in enumerate(whites * 8):
        day = date.fromordinal(start.toordinal() + index * 2)
        draws.append(make_draw(day.year, day.month, day.day, white, (index % 26) + 1))
    return draws


def test_daily_picks_are_valid_and_deterministic():
    draws = _history()
    first = generate_daily_picks(draws, date(2026, 8, 17))
    second = generate_daily_picks(draws, date(2026, 8, 17))
    assert first["tickets"] == second["tickets"]
    assert first["next_draw"] == "2026-08-17"
    assert first["analyzed_draws"] == len(draws)
    assert len(first["tickets"]) == 3
    keys = {ticket["key"] for ticket in first["tickets"]}
    assert keys == {"hot", "due", "balanced"}
    combos = set()
    for ticket in first["tickets"]:
        white = ticket["white"]
        assert white == sorted(white)
        assert len(set(white)) == 5
        assert all(1 <= n <= 69 for n in white)
        assert 1 <= ticket["powerball"] <= 26
        combos.add((tuple(white), ticket["powerball"]))
    assert len(combos) == 3


def test_different_days_can_change_picks():
    draws = _history()
    monday = generate_daily_picks(draws, date(2026, 8, 17))
    tuesday = generate_daily_picks(draws, date(2026, 8, 18))
    assert monday["next_draw"] == "2026-08-17"
    assert tuesday["next_draw"] == "2026-08-19"
    assert monday["tickets"] != tuesday["tickets"]


def test_different_ips_get_different_tickets():
    draws = _history()
    first = generate_daily_picks(
        draws,
        date(2026, 8, 17),
        user_key=fingerprint_visitor("1.1.1.1"),
    )
    second = generate_daily_picks(
        draws,
        date(2026, 8, 17),
        user_key=fingerprint_visitor("8.8.8.8"),
    )
    assert first["tickets"] != second["tickets"]
    assert first["visitor_keyed"] is True


def test_same_ip_is_stable_until_user_generates_again():
    draws = _history()
    key = fingerprint_visitor("203.0.113.10")
    first = generate_daily_picks(draws, date(2026, 8, 17), user_key=key, generation=1)
    second = generate_daily_picks(draws, date(2026, 8, 17), user_key=key, generation=1)
    third = generate_daily_picks(draws, date(2026, 8, 17), user_key=key, generation=2)
    assert first["tickets"] == second["tickets"]
    assert first["tickets"] != third["tickets"]
