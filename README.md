# TriplePick.pro

**Use it now:** [https://raw.githack.com/ZCGLLC/moneymove/cursor/powerball-daily-picks-9c63/docs/index.html](https://raw.githack.com/ZCGLLC/moneymove/cursor/powerball-daily-picks-9c63/docs/index.html)

TriplePick.pro is a one-page Powerball analysis desk. It scores every official U.S. drawing since April 22, 1992, updates after each drawing, and gives each visitor three unique ticket sets keyed to their IP address.

Production domain: [https://triplepick.pro/](https://triplepick.pro/)

## Connect triplepick.pro

The app is ready in this repo (`docs/CNAME` is already `triplepick.pro`). The domain currently still points at Squarespace, so you have to do these two owner steps.

### 1. Turn on GitHub Pages first

In [ZCGLLC/moneymove](https://github.com/ZCGLLC/moneymove):

1. Merge this branch into `main`, or keep Pages pointed at `cursor/powerball-daily-picks-9c63`.
2. Open **Settings → Pages**.
3. Under **Build and deployment → Source**, choose **GitHub Actions**, or **Deploy from a branch** with branch `main` (or this feature branch) and folder `/docs`.
4. Under **Custom domain**, enter `triplepick.pro` and click **Save**.
5. Wait for the DNS check. After it succeeds, check **Enforce HTTPS**.

The preview URL will be `https://zcgllc.github.io/moneymove/` until DNS switches.

### 2. Point Squarespace DNS at GitHub

`triplepick.pro` is on Squarespace DNS and now serves a Coming Soon page. In [account.squarespace.com](https://account.squarespace.com) → **Domains** → **triplepick.pro** → **DNS** → **DNS Settings**:

1. Delete the Squarespace default **A** records for `@` (`198.49…` / `198.185…`).
2. Delete the **www** CNAME that points to `ext-sq.squarespace.com`.
3. Delete any leftover **HTTPS** / Squarespace website records that conflict. Keep MX/TXT records if you use email.
4. Under **Custom records**, add:

| Type | Name / Host | Data |
| --- | --- | --- |
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `zcgllc.github.io` |

Save. DNS can take a few minutes to a few hours. When it is right, `triplepick.pro` should resolve to those `185.199…` addresses, not Squarespace.

Until that switch is done, the live app is still here: [current TriplePick.pro build](https://raw.githack.com/ZCGLLC/moneymove/cursor/powerball-daily-picks-9c63/docs/index.html).

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
