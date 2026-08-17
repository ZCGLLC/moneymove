# TriplePick.pro

**Use it now:** [https://raw.githack.com/ZCGLLC/moneymove/cursor/powerball-daily-picks-9c63/docs/index.html](https://raw.githack.com/ZCGLLC/moneymove/cursor/powerball-daily-picks-9c63/docs/index.html)

TriplePick.pro is a one-page Powerball analysis desk. It scores every official U.S. drawing since April 22, 1992, updates after each drawing, and gives each visitor three unique ticket sets keyed to their IP address.

Production domain: [https://triplepick.pro/](https://triplepick.pro/)

Official rules and results live at [powerball.com](https://www.powerball.com/). TriplePick.pro is not affiliated with the Multi-State Lottery Association.

## What it does

1. Loads the 1992–early 2010 archive bundled in `data/historical_1992_2010.csv`, plus two later Saturday drawings that NY Open Data omits.
2. Pulls 2010–present results from [NY Open Data](https://data.ny.gov/Government-Finance/Lottery-Powerball-Winning-Numbers-Beginning-2010/d6yy-54nr) on every visit, then checks again automatically after Monday, Wednesday, and Saturday drawings.
3. Scores hot numbers, overdue numbers, all-time frequency, recent-draw recency, and typical winning-ticket shape.
4. Seeds each visitor’s tickets from a hash of their IP. Clicking **Generate new numbers** creates another unique trio.

The layout is a full one-page site with navigation, hero, generator, analysis, and footer, plus reserved IAB ad units. To switch on Google AdSense, edit `docs/js/ads-config.js`.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Tests

```bash
pytest -q
```
