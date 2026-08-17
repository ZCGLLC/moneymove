from datetime import date

from app import app
from powerball.generate import fingerprint_visitor, generate_daily_picks
from tests.test_generate import _history


def test_picks_endpoint(monkeypatch):
    draws = _history()
    monkeypatch.setattr("app.get_draws", lambda **_kwargs: draws)
    client = app.test_client()
    response = client.get("/api/picks?date=2026-08-17", environ_base={"REMOTE_ADDR": "203.0.113.25"})
    assert response.status_code == 200
    payload = response.get_json()
    expected = generate_daily_picks(
        draws,
        date(2026, 8, 17),
        user_key=fingerprint_visitor("203.0.113.25"),
        generation=1,
    )
    assert payload["tickets"] == expected["tickets"]
    other = client.get("/api/picks?date=2026-08-17", environ_base={"REMOTE_ADDR": "198.51.100.7"})
    assert other.get_json()["tickets"] != payload["tickets"]
    home = client.get("/")
    assert home.status_code == 200
    assert b"TriplePick.pro" in home.data
    assert b"Generate new numbers" in home.data
    assert b"data-ad=" in home.data
