import json
from pathlib import Path


def test_static_app_is_self_contained():
    root = Path(__file__).resolve().parent.parent / "docs"
    assert (root / "index.html").exists()
    assert (root / "js" / "engine.js").exists()
    assert (root / "js" / "app.js").exists()
    assert (root / "css" / "style.css").exists()
    draws = json.loads((root / "draws.json").read_text(encoding="utf-8"))
    assert len(draws) >= 3800
    assert draws[0]["date"] == "1992-04-22"
    assert draws[0]["white"] == [2, 25, 35, 41, 42]
    assert draws[0]["powerball"] == 15
    assert draws[-1]["date"] >= "2026-08-15"
    assert len(draws[-1]["white"]) == 5
    html = (root / "index.html").read_text(encoding="utf-8")
    engine = (root / "js" / "engine.js").read_text(encoding="utf-8")
    app_js = (root / "js" / "app.js").read_text(encoding="utf-8")
    assert "Generate new numbers" in html
    assert 'data-ad="top-leaderboard"' in html
    assert 'data-ad="rail-top"' in html
    assert 'data-ad="in-content"' in html
    assert (root / "js" / "ads.js").exists()
    assert (root / "js" / "ads-config.js").exists()
    assert "lookupVisitorIp" in engine
    assert "loadDraws(true)" in app_js
