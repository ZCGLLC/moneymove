"""Flask UI for daily Powerball analysis picks."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from powerball.data import load_all_draws
from powerball.generate import fingerprint_visitor, generate_daily_picks

DOCS = Path(__file__).resolve().parent / "docs"
app = Flask(__name__)
_draws_cache: list | None = None


def get_draws(*, refresh: bool = False):
    global _draws_cache
    if refresh or _draws_cache is None:
        _draws_cache = load_all_draws(refresh=refresh)
    return _draws_cache


@app.get("/api/picks")
def api_picks():
    pick_date = _parse_date(request.args.get("date"))
    generation = _parse_generation(request.args.get("generation"))
    payload = generate_daily_picks(
        get_draws(),
        pick_date,
        user_key=fingerprint_visitor(_client_ip()),
        generation=generation,
    )
    return jsonify(payload)


@app.post("/api/refresh")
def api_refresh():
    draws = get_draws(refresh=True)
    body = request.get_json(silent=True) or {}
    pick_date = _parse_date(request.args.get("date") or body.get("date"))
    generation = _parse_generation(request.args.get("generation") or body.get("generation"))
    payload = generate_daily_picks(
        draws,
        pick_date,
        user_key=fingerprint_visitor(_client_ip()),
        generation=generation,
    )
    payload["refreshed"] = True
    return jsonify(payload)


@app.get("/")
def index():
    return send_from_directory(DOCS, "index.html")


@app.get("/<path:filename>")
def docs_files(filename):
    return send_from_directory(DOCS, filename)


def _parse_date(value: str | None) -> date:
    if not value:
        return date.today()
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_generation(value) -> int:
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 1


def _client_ip() -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP", "")
    if real_ip:
        return real_ip.strip()
    return request.remote_addr or "0.0.0.0"


if __name__ == "__main__":
    get_draws(refresh=True)
    app.run(host="0.0.0.0", port=5000, debug=False)
