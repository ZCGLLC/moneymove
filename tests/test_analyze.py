from datetime import date

from powerball.analyze import analyze
from powerball.models import CURRENT_FORMAT_START
from tests.conftest import make_draw


def test_analyze_counts_current_and_all_time():
    draws = [
        make_draw(2014, 1, 1, [1, 2, 3, 4, 5], 9),
        make_draw(2016, 1, 2, [10, 20, 30, 40, 50], 4),
        make_draw(2016, 1, 6, [10, 21, 32, 40, 61], 4),
        make_draw(2016, 1, 9, [11, 22, 33, 44, 55], 18),
    ]
    stats = analyze(draws)
    assert stats.total_draws == 4
    assert stats.current_format_draws == 3
    assert stats.first_draw == date(2014, 1, 1)
    assert stats.last_draw == date(2016, 1, 9)
    assert stats.white_freq_current[0][0] in {10, 40}
    pb_hot = dict(stats.powerball_freq_current)
    assert pb_hot[4] == 2
    overdue = dict(stats.overdue_white)
    assert overdue[10] == 1
    assert all(draw.draw_date >= CURRENT_FORMAT_START for draw in stats.recent_draws if draw.is_current_format)
