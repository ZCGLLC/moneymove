# Daily Powerball Picks

**Use the software now:** [Open Daily Powerball Picks](https://raw.githack.com/ZCGLLC/moneymove/cursor/powerball-daily-picks-9c63/docs/index.html)

Anyone can open that link and click **Generate new numbers**. The site scores every official U.S. Powerball drawing since April 22, 1992, pulls new results automatically after each drawing, and gives each visitor their own tickets keyed to their IP address. The raw IP is hashed in the browser and is not stored.

Stable GitHub Pages URL after Pages is enabled in repo Settings → Pages → GitHub Actions: [https://zcgllc.github.io/moneymove/](https://zcgllc.github.io/moneymove/)

Official rules and results live at [powerball.com](https://www.powerball.com/). This project is not affiliated with the Multi-State Lottery Association.

## What it does

1. Loads the 1992–early 2010 archive bundled in `data/historical_1992_2010.csv`, plus two later Saturday drawings that NY Open Data omits.
2. Pulls 2010–present results from [NY Open Data](https://data.ny.gov/Government-Finance/Lottery-Powerball-Winning-Numbers-Beginning-2010/d6yy-54nr) on every visit, then checks again automatically after Monday, Wednesday, and Saturday drawings.
3. Scores hot numbers, overdue numbers, all-time frequency, recent-draw recency, and typical winning-ticket shape (odd/even mix, high/low mix, white-ball sum).
4. Seeds each visitor’s tickets from a hash of their IP so two people do not receive the same sets. Clicking **Generate new numbers** creates another unique trio for that visitor.

The layout reserves standard IAB ad units (728×90 leaderboard, 300×250, 300×600, in-content 336×280, and a mobile 320×50 anchor) so ads can run without covering the tickets. To switch on Google AdSense, edit `docs/js/ads-config.js`: set `provider` to `"adsense"`, add your `adsenseClient` (`ca-pub-…`), and fill each `adsenseSlot` id.

The three daily sets are:

| Set | How it is built |
| --- | --- |
| **Hot Frequency** | Favors numbers drawn most often in the current 5/69 + 1/26 format, with extra weight on recent drawings. |
| **Overdue** | Favors numbers that have gone longer than usual without appearing. |
| **Balanced Pattern** | Mixes those signals, then keeps tickets that look like typical jackpot draws (usually 2–3 odd and 2–3 high white balls). |

Powerball drawings are random. Past results do not change the odds of any future combination. These picks are statistical entertainment, not a prediction of the jackpot.

## Run locally

The live site needs no install. To run the same app on your computer:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Command line

```bash
python -m powerball
python -m powerball --date 2026-08-17 --ip 203.0.113.10
python -m powerball --refresh --json
```

## Tests

```bash
pytest -q
```
