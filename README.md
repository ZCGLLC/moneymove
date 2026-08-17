# TriplePick.pro

**Use it now:** [https://raw.githack.com/ZCGLLC/moneymove/cursor/powerball-daily-picks-9c63/docs/index.html](https://raw.githack.com/ZCGLLC/moneymove/cursor/powerball-daily-picks-9c63/docs/index.html)

TriplePick.pro is a one-page Powerball analysis desk. It scores every official U.S. drawing since April 22, 1992, updates after each drawing, and gives each visitor three unique ticket sets keyed to their IP address.

Production domain: [https://triplepick.pro/](https://triplepick.pro/)

Browsers hide the `http://` / `https://` prefix. A secured TriplePick site shows a **lock** and opens as **https://triplepick.pro/**.

## Connect triplepick.pro (HTTPS)

GitHub Pages is already publishing TriplePick from this branch (`/docs`) with custom domain `triplepick.pro`. The lock / HTTPS certificate cannot finish while the **apex** (`triplepick.pro` with no `www`) still points at Squarespace.

Squarespace often puts its own A records back after you save. If [https://triplepick.pro/](https://triplepick.pro/) shows **Coming Soon**, the domain is still on Squarespace, not this site.

### 1. Disconnect Squarespace from the website

In [account.squarespace.com](https://account.squarespace.com) → **Domains** → **triplepick.pro**:

1. If the domain is connected to a Squarespace site or “Coming Soon” page, **disconnect** it. Leave the domain in Squarespace only as DNS.
2. Open **DNS** → **DNS Settings**.
3. Delete every **A** record for `@` / `triplepick.pro` that uses `198.49…` or `198.185…`.
4. Delete any **www** CNAME to `ext-sq.squarespace.com`.
5. Keep MX/TXT records if you use email.

### 2. Point the apex at GitHub Pages

Add these **custom** records only:

| Type | Name / Host | Data |
| --- | --- | --- |
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `zcgllc.github.io` |

Save. Do **not** click Squarespace’s “link domain” / default website records again. Those overwrite GitHub and break HTTPS.

When this is right, `triplepick.pro` resolves to `185.199.108–111.153`, not `198.49…` / `198.185…`.

### 3. Turn on Enforce HTTPS

In [ZCGLLC/moneymove → Settings → Pages](https://github.com/ZCGLLC/moneymove/settings/pages):

1. Keep **Custom domain** as `triplepick.pro`.
2. Keep source on this branch and folder **`/docs`** (or `main` + `/docs` after merge).
3. Wait until GitHub shows the domain check as successful and the certificate is issued.
4. Check **Enforce HTTPS**. That makes `http://triplepick.pro` redirect to **`https://triplepick.pro`** with a lock.

GitHub cannot issue that certificate while Squarespace still answers `triplepick.pro`.

Until the A records stay on GitHub, use the live TriplePick build: [current TriplePick.pro page](https://raw.githack.com/ZCGLLC/moneymove/cursor/powerball-daily-picks-9c63/docs/index.html).

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
