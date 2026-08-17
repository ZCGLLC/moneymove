# Daily Powerball Picks

Simple software that scores **every official U.S. Powerball drawing since April 22, 1992** and prints **three ticket sets per day** for the current game:

- 5 white balls from 1–69
- 1 red Powerball from 1–26

Official rules and results live at [powerball.com](https://www.powerball.com/). This project is not affiliated with the Multi-State Lottery Association.

## What it does

1. Loads the 1992–early 2010 archive bundled in `data/historical_1992_2010.csv`, plus two later Saturday drawings that NY Open Data omits.
2. Refreshes 2010–present results from [NY Open Data](https://data.ny.gov/Government-Finance/Lottery-Powerball-Winning-Numbers-Beginning-2010/d6yy-54nr) (the same public feed used for official historical Powerball numbers).
3. Scores hot numbers, overdue numbers, all-time frequency, recent-draw recency, and typical winning-ticket shape (odd/even mix, high/low mix, white-ball sum).
4. Uses a date-based seed so the same calendar day always returns the same three sets.

The three daily sets are:

| Set | How it is built |
| --- | --- |
| **Hot Frequency** | Favors numbers drawn most often in the current 5/69 + 1/26 format, with extra weight on recent drawings. |
| **Overdue** | Favors current-format numbers that have gone longer than usual without appearing. |
| **Balanced Pattern** | Mixes those signals, then keeps tickets that look like typical jackpot draws (usually 2–3 odd and 2–3 high white balls). |

Powerball drawings are random. Past results do not change the odds of any future combination. These picks are statistical entertainment, not a prediction of the jackpot.

## Run the web app

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). Use **Refresh latest draws** after a Monday, Wednesday, or Saturday drawing.

## Command line

```bash
python -m powerball
python -m powerball --date 2026-08-17
python -m powerball --refresh --json
```

## Tests

```bash
pytest -q
```
