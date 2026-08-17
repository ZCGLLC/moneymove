from datetime import date

from app import app
from powerball.generate import generate_daily_picks
from tests.test_generate import _history


def test_picks_endpoint(monkeypatch):
    draws = _history()
    monkeypatch.setattr("app.get_draws", lambda **_kwargs: draws)
    client = app.test_client()
    response = client.get("/api/picks?date=2026-08-17")
    assert response.status_code == 200
    payload = response.get_json()
    expected = generate_daily_picks(draws, date(2026, 8, 17))
    assert payload["tickets"] == expected["tickets"]
    home = client.get("/")
    assert home.status_code == 200
    assert b"Daily Powerball Picks" in home.data
