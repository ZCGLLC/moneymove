from datetime import date

from powerball.data import _load_historical, load_all_draws
from powerball.models import NY_OPEN_DATA_START


def test_historical_archive_covers_1992_to_early_2010():
    draws = sorted(_load_historical(), key=lambda item: item.draw_date)
    assert len(draws) == 1858
    assert draws[0].draw_date == date(1992, 4, 22)
    assert draws[0].white == (2, 25, 35, 41, 42)
    assert draws[0].powerball == 15
    assert date(2014, 6, 28) in {draw.draw_date for draw in draws}
    assert date(2017, 6, 10) in {draw.draw_date for draw in draws}
    assert all(len(draw.white) == 5 for draw in draws)
    assert NY_OPEN_DATA_START == date(2010, 2, 3)


def test_load_all_draws_uses_archive_when_ny_unavailable(monkeypatch):
    monkeypatch.setattr("powerball.data._load_ny", lambda **_kwargs: [])
    draws = load_all_draws(refresh=False)
    assert draws[0].draw_date == date(1992, 4, 22)
    assert len(draws) == 1858
