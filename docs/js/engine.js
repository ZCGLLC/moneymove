const WHITE_MAX = 69;
const POWERBALL_MAX = 26;
const CURRENT_FORMAT_START = "2015-10-07";
const NY_API = "https://data.ny.gov/resource/d6yy-54nr.json?$limit=50000&$order=draw_date";
const DISCLAIMER =
  "Powerball drawings are random. Past results do not change the odds of any future combination. These sets are statistical entertainment picks, not a guarantee.";

const STRATEGIES = [
  {
    key: "hot",
    name: "Hot Frequency",
    summary:
      "Weighted toward numbers that appear most often in the current 5/69 + 1/26 format, with extra credit for recent draws and all-time history.",
    freq: 0.62,
    recency: 0.28,
    overdue: 0.05,
    allTime: 0.05,
    pair: 0.22,
    shape: false,
  },
  {
    key: "due",
    name: "Overdue",
    summary:
      "Weighted toward current-format numbers that have gone longer than usual without being drawn, blended with long-run frequency so cold numbers are not pure guesses.",
    freq: 0.18,
    recency: 0.1,
    overdue: 0.62,
    allTime: 0.1,
    pair: 0.08,
    shape: false,
  },
  {
    key: "balanced",
    name: "Balanced Pattern",
    summary:
      "Blends hot, overdue, and all-time counts, then keeps tickets that match how real jackpot draws usually look: mixed odd/even, mixed high/low, and a typical white-ball sum.",
    freq: 0.34,
    recency: 0.22,
    overdue: 0.24,
    allTime: 0.2,
    pair: 0.16,
    shape: true,
  },
];

function isCurrentFormat(draw) {
  return draw.date >= CURRENT_FORMAT_START;
}

function whiteSum(draw) {
  return draw.white.reduce((sum, n) => sum + n, 0);
}

function oddCount(white) {
  return white.filter((n) => n % 2 === 1).length;
}

function highCount(white) {
  return white.filter((n) => n >= 36).length;
}

function hasConsecutive(white) {
  const sorted = [...white].sort((a, b) => a - b);
  return sorted.some((n, i) => i < 4 && n + 1 === sorted[i + 1]);
}

function ranked(counter, limit) {
  return Array.from({ length: limit }, (_, i) => [i + 1, counter[i + 1] || 0]).sort(
    (a, b) => b[1] - a[1] || a[0] - b[0]
  );
}

function lastSeenGaps(draws, kind) {
  const era = draws.filter(isCurrentFormat);
  const pool = era.length ? era : draws;
  const limit = kind === "white" ? WHITE_MAX : POWERBALL_MAX;
  const gaps = {};
  for (let n = 1; n <= limit; n += 1) gaps[n] = pool.length;
  for (let offset = 0; offset < pool.length; offset += 1) {
    const draw = pool[pool.length - 1 - offset];
    const values = kind === "white" ? draw.white : [draw.powerball];
    values.forEach((number) => {
      if (number >= 1 && number <= limit && gaps[number] === pool.length) {
        gaps[number] = offset;
      }
    });
  }
  return gaps;
}

function recencyWeights(draws) {
  const white = Array(WHITE_MAX + 1).fill(0);
  const power = Array(POWERBALL_MAX + 1).fill(0);
  const era = draws.filter(isCurrentFormat);
  const pool = era.length ? era : draws;
  const decay = 0.5 ** (1 / 180);
  let weight = 1;
  for (let i = pool.length - 1; i >= 0; i -= 1) {
    pool[i].white.forEach((number) => {
      if (number >= 1 && number <= WHITE_MAX) white[number] += weight;
    });
    if (pool[i].powerball >= 1 && pool[i].powerball <= POWERBALL_MAX) {
      power[pool[i].powerball] += weight;
    }
    weight *= decay;
  }
  return [white, power];
}

function pairCounts(draws) {
  const counts = {};
  const era = draws.filter(isCurrentFormat);
  const pool = era.length ? era : draws;
  pool.forEach((draw) => {
    const balls = draw.white.filter((n) => n >= 1 && n <= WHITE_MAX);
    for (let i = 0; i < balls.length; i += 1) {
      for (let j = i + 1; j < balls.length; j += 1) {
        const left = Math.min(balls[i], balls[j]);
        const right = Math.max(balls[i], balls[j]);
        const key = `${left}-${right}`;
        counts[key] = (counts[key] || 0) + 1;
      }
    }
  });
  return counts;
}

function analyze(draws) {
  const current = draws.filter(isCurrentFormat);
  const era = current.length ? current : draws;
  const whiteAll = {};
  const pbAll = {};
  const whiteCur = {};
  const pbCur = {};
  const bump = (map, n) => {
    map[n] = (map[n] || 0) + 1;
  };
  draws.forEach((draw) => {
    draw.white.forEach((n) => {
      if (n >= 1 && n <= WHITE_MAX) bump(whiteAll, n);
    });
    if (draw.powerball >= 1 && draw.powerball <= POWERBALL_MAX) bump(pbAll, draw.powerball);
  });
  era.forEach((draw) => {
    draw.white.forEach((n) => {
      if (n >= 1 && n <= WHITE_MAX) bump(whiteCur, n);
    });
    if (draw.powerball >= 1 && draw.powerball <= POWERBALL_MAX) bump(pbCur, draw.powerball);
  });

  const oddMap = {};
  const highMap = {};
  era.forEach((draw) => {
    bump(oddMap, oddCount(draw.white));
    bump(highMap, highCount(draw.white));
  });
  const typicalOdd = Object.entries(oddMap)
    .sort((a, b) => b[1] - a[1] || Number(a[0]) - Number(b[0]))
    .slice(0, 2)
    .map(([k]) => Number(k))
    .sort((a, b) => a - b);
  const typicalHigh = Object.entries(highMap)
    .sort((a, b) => b[1] - a[1] || Number(a[0]) - Number(b[0]))
    .slice(0, 2)
    .map(([k]) => Number(k))
    .sort((a, b) => a - b);

  const sums = era.map(whiteSum).sort((a, b) => a - b);
  const p10 = sums[Math.max(0, Math.floor(sums.length / 10))];
  const p90 = sums[Math.min(sums.length - 1, Math.floor((9 * sums.length) / 10))];
  const mean = Math.round((sums.reduce((s, n) => s + n, 0) / sums.length) * 10) / 10;
  const consecutiveRate =
    Math.round((era.filter((draw) => hasConsecutive(draw.white)).length / era.length) * 1000) / 1000;

  const overdueWhite = lastSeenGaps(draws, "white");
  const overduePb = lastSeenGaps(draws, "powerball");
  const asPairs = (obj) =>
    Object.entries(obj)
      .map(([n, c]) => [Number(n), c])
      .sort((a, b) => b[1] - a[1] || a[0] - b[0]);

  return {
    totalDraws: draws.length,
    currentFormatDraws: current.length,
    firstDraw: draws[0].date,
    lastDraw: draws[draws.length - 1].date,
    whiteFreqCurrent: ranked(whiteCur, WHITE_MAX),
    whiteFreqAll: ranked(whiteAll, WHITE_MAX),
    powerballFreqCurrent: ranked(pbCur, POWERBALL_MAX),
    powerballFreqAll: ranked(pbAll, POWERBALL_MAX),
    overdueWhite: asPairs(overdueWhite),
    overduePowerball: asPairs(overduePb),
    recentDraws: [...draws].slice(-12).reverse(),
    typicalOdd: typicalOdd.length === 2 ? typicalOdd : [2, 3],
    typicalHigh: typicalHigh.length === 2 ? typicalHigh : [2, 3],
    typicalSum: [p10, p90, mean],
    consecutiveRate,
    whiteCur,
    pbCur,
  };
}

function normalize(values) {
  const out = values.slice();
  if (!out.length) return out;
  out[0] = 0;
  const peak = Math.max(...out);
  if (peak <= 0) return out.map((_, i) => (i === 0 ? 0 : 1));
  return out.map((v) => v / peak);
}

function blendWeights(limit, freq, allTime, recency, gaps, eraDraws, strategy) {
  const freqN = normalize(Array.from({ length: limit + 1 }, (_, n) => freq[n] || 0));
  const allN = normalize(Array.from({ length: limit + 1 }, (_, n) => allTime[n] || 0));
  const rec = recency.length > limit ? recency.slice(0, limit + 1) : recency.concat(Array(limit + 1 - recency.length).fill(0));
  const recN = normalize(rec);
  const overdue = Array(limit + 1).fill(0);
  for (let n = 1; n <= limit; n += 1) {
    const expected = eraDraws / Math.max(freq[n] || 0, 1);
    overdue[n] = Math.min(4, (gaps[n] ?? eraDraws) / Math.max(expected, 1));
  }
  const overN = normalize(overdue);
  const weights = Array(limit + 1).fill(0);
  for (let n = 1; n <= limit; n += 1) {
    weights[n] =
      strategy.freq * freqN[n] +
      strategy.recency * recN[n] +
      strategy.overdue * overN[n] +
      strategy.allTime * allN[n] +
      0.02;
  }
  return weights;
}

function xmur3(str) {
  let h = 1779033703 ^ str.length;
  for (let i = 0; i < str.length; i += 1) {
    h = Math.imul(h ^ str.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  return () => {
    h = Math.imul(h ^ (h >>> 16), 2246822507);
    h = Math.imul(h ^ (h >>> 13), 3266489909);
    h ^= h >>> 16;
    return h >>> 0;
  };
}

function mulberry32(a) {
  return () => {
    a += 0x6d2b79f5;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function makeRng(pickDate, key, userKey, generation) {
  const seed = xmur3(`moneymove-powerball|${pickDate}|${userKey || "anon"}|${generation}|${key}|v2`)();
  const random = mulberry32(seed);
  return {
    random,
    randint(min, max) {
      return min + Math.floor(random() * (max - min + 1));
    },
  };
}

function weightedChoice(rng, weights) {
  const total = weights.slice(1).reduce((sum, n) => sum + n, 0);
  if (total <= 0) return rng.randint(1, weights.length - 1);
  const pick = rng.random() * total;
  let running = 0;
  let last = 1;
  for (let number = 1; number < weights.length; number += 1) {
    if (weights[number] <= 0) continue;
    running += weights[number];
    last = number;
    if (running >= pick) return number;
  }
  return last;
}

function sampleWhites(rng, base, pairs, pairBoost) {
  const weights = base.slice();
  const chosen = [];
  for (let i = 0; i < 5; i += 1) {
    const number = weightedChoice(rng, weights);
    chosen.push(number);
    weights[number] = 0;
    if (pairBoost) {
      for (let other = 1; other <= WHITE_MAX; other += 1) {
        if (weights[other] <= 0) continue;
        const left = Math.min(number, other);
        const right = Math.max(number, other);
        weights[other] *= 1 + pairBoost * ((pairs[`${left}-${right}`] || 0) / 40);
      }
    }
  }
  return chosen.sort((a, b) => a - b);
}

function shapeScore(white, stats) {
  const odd = oddCount(white);
  const high = highCount(white);
  const total = white.reduce((sum, n) => sum + n, 0);
  let score = 0;
  score += stats.typicalOdd.includes(odd) ? 0.34 : odd === 1 || odd === 4 ? 0.12 : 0;
  score += stats.typicalHigh.includes(high) ? 0.34 : high === 1 || high === 4 ? 0.12 : 0;
  const [low, highSum, mean] = stats.typicalSum;
  if (total >= low && total <= highSum) score += 0.32;
  else score += Math.max(0, 0.32 - Math.abs(total - mean) / 250);
  return score;
}

function pickTicket(rng, strategy, stats, whiteRecency, pbRecency, whiteGap, pbGap, pairs, used) {
  const whiteFreq = Object.fromEntries(stats.whiteFreqCurrent);
  const whiteAll = Object.fromEntries(stats.whiteFreqAll);
  const pbFreq = Object.fromEntries(stats.powerballFreqCurrent);
  const pbAll = Object.fromEntries(stats.powerballFreqAll);
  const eraDraws = stats.currentFormatDraws || stats.totalDraws;
  const whiteBase = blendWeights(WHITE_MAX, whiteFreq, whiteAll, whiteRecency, whiteGap, eraDraws, strategy);
  const pbBase = blendWeights(POWERBALL_MAX, pbFreq, pbAll, pbRecency, pbGap, eraDraws, strategy);
  let best = null;
  let bestPb = 1;
  let bestScore = -1;
  const attempts = strategy.shape ? 80 : 24;
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    const white = sampleWhites(rng, whiteBase, pairs, strategy.pair);
    const powerball = weightedChoice(rng, pbBase);
    const key = `${white.join(",")}|${powerball}`;
    if (used.has(key)) continue;
    let score = 1;
    if (strategy.shape) {
      score = shapeScore(white, stats);
      if (score < 0.55 && attempt < attempts - 1) continue;
    }
    if (score > bestScore) {
      bestScore = score;
      best = white;
      bestPb = powerball;
      if (!strategy.shape || score >= 0.92) break;
    }
  }
  if (!best) {
    best = sampleWhites(rng, whiteBase, pairs, strategy.pair);
    bestPb = weightedChoice(rng, pbBase);
  }
  return { key: strategy.key, name: strategy.name, summary: strategy.summary, white: best, powerball: bestPb };
}

function nextDrawDate(iso) {
  const [year, month, day] = iso.split("-").map(Number);
  const start = new Date(year, month - 1, day);
  for (let offset = 0; offset < 8; offset += 1) {
    const candidate = new Date(start);
    candidate.setDate(start.getDate() + offset);
    const weekday = candidate.getDay();
    if (weekday === 1 || weekday === 3 || weekday === 6) {
      const y = candidate.getFullYear();
      const m = String(candidate.getMonth() + 1).padStart(2, "0");
      const d = String(candidate.getDate()).padStart(2, "0");
      return `${y}-${m}-${d}`;
    }
  }
  return iso;
}

function generateDailyPicks(draws, pickDate, userKey, generation, priorUsed) {
  if (!draws.length) throw new Error("no historical draws available");
  generation = Math.max(1, Number(generation) || 1);
  const stats = analyze(draws);
  const [whiteRecency, pbRecency] = recencyWeights(draws);
  const pairs = pairCounts(draws);
  const whiteGap = lastSeenGaps(draws, "white");
  const pbGap = lastSeenGaps(draws, "powerball");
  const used = new Set(draws.map((draw) => `${[...draw.white].sort((a, b) => a - b).join(",")}|${draw.powerball}`));
  (priorUsed || []).forEach((key) => used.add(key));
  const tickets = STRATEGIES.map((strategy) => {
    const ticket = pickTicket(
      makeRng(pickDate, strategy.key, userKey, generation),
      strategy,
      stats,
      whiteRecency,
      pbRecency,
      whiteGap,
      pbGap,
      pairs,
      used
    );
    used.add(`${ticket.white.join(",")}|${ticket.powerball}`);
    return ticket;
  });
  return {
    pick_date: pickDate,
    next_draw: nextDrawDate(pickDate),
    generation,
    visitor_keyed: Boolean(userKey),
    analyzed_draws: stats.totalDraws,
    current_format_draws: stats.currentFormatDraws,
    first_draw: stats.firstDraw,
    last_draw: stats.lastDraw,
    disclaimer: DISCLAIMER,
    tickets,
    stats: {
      total_draws: stats.totalDraws,
      current_format_draws: stats.currentFormatDraws,
      first_draw: stats.firstDraw,
      last_draw: stats.lastDraw,
      hottest_white: stats.whiteFreqCurrent.slice(0, 10),
      overdue_white: stats.overdueWhite.slice(0, 10),
      hottest_powerball: stats.powerballFreqCurrent.slice(0, 8),
      hottest_white_all_time: stats.whiteFreqAll.slice(0, 10),
      typical_odd: stats.typicalOdd,
      typical_high: stats.typicalHigh,
      typical_sum: { p10: stats.typicalSum[0], p90: stats.typicalSum[1], mean: stats.typicalSum[2] },
      consecutive_rate: stats.consecutiveRate,
      recent_draws: stats.recentDraws.map((draw) => ({
        date: draw.date,
        white: draw.white,
        powerball: draw.powerball,
        multiplier: draw.multiplier,
      })),
    },
  };
}

function parseNyRow(row) {
  const date = String(row.draw_date).slice(0, 10);
  const numbers = String(row.winning_numbers)
    .trim()
    .split(/\s+/)
    .map((part) => Number(part));
  if (numbers.length !== 6 || numbers.some((n) => !Number.isFinite(n))) return null;
  return {
    date,
    white: numbers.slice(0, 5).sort((a, b) => a - b),
    powerball: numbers[5],
    multiplier: row.multiplier ? Number(row.multiplier) : null,
  };
}

function mergeDraws(base, extra) {
  const map = new Map();
  base.concat(extra).forEach((draw) => {
    if (draw && draw.date) map.set(draw.date, draw);
  });
  return Array.from(map.values()).sort((a, b) => a.date.localeCompare(b.date));
}

async function loadBundledDraws() {
  const response = await fetch("draws.json", { cache: "no-store" });
  if (!response.ok) throw new Error("Could not load the bundled Powerball archive.");
  return response.json();
}

async function fetchNyDraws() {
  const response = await fetch(NY_API, { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`NY Open Data request failed (${response.status})`);
  const rows = await response.json();
  return rows.map(parseNyRow).filter(Boolean);
}

const NY_CACHE_KEY = "pb-ny-draws-v1";

async function loadDraws(refresh = true) {
  const bundled = await loadBundledDraws();
  if (!refresh) return bundled;
  try {
    const latest = await fetchNyDraws();
    try {
      localStorage.setItem(NY_CACHE_KEY, JSON.stringify({ at: Date.now(), draws: latest }));
    } catch (_error) {
      /* ignore quota / private-mode failures */
    }
    return mergeDraws(bundled, latest);
  } catch (_error) {
    try {
      const cached = JSON.parse(localStorage.getItem(NY_CACHE_KEY) || "null");
      if (cached && Array.isArray(cached.draws) && cached.draws.length) {
        return mergeDraws(bundled, cached.draws);
      }
    } catch (_ignored) {
      /* fall through to bundled archive */
    }
    return bundled;
  }
}

async function lookupVisitorIp() {
  const sources = [
    async () => {
      const response = await fetch("https://api.ipify.org?format=json");
      const payload = await response.json();
      return payload.ip;
    },
    async () => {
      const response = await fetch("https://api64.ipify.org?format=json");
      const payload = await response.json();
      return payload.ip;
    },
    async () => {
      const response = await fetch("https://www.cloudflare.com/cdn-cgi/trace");
      const text = await response.text();
      const match = text.match(/^ip=(.+)$/m);
      return match ? match[1] : "";
    },
  ];
  for (const source of sources) {
    try {
      const ip = String((await source()) || "").trim();
      if (ip) return ip;
    } catch (_error) {
      /* try the next source */
    }
  }
  throw new Error("ip lookup failed");
}

async function hashValue(value) {
  const encoded = new TextEncoder().encode(String(value).trim().toLowerCase());
  if (globalThis.crypto && crypto.subtle) {
    const digest = await crypto.subtle.digest("SHA-256", encoded);
    return Array.from(new Uint8Array(digest))
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join("")
      .slice(0, 16);
  }
  return xmur3(String(value).trim().toLowerCase())().toString(16).padStart(8, "0");
}

async function resolveVisitorKey() {
  try {
    const ip = await lookupVisitorIp();
    return { key: await hashValue(ip), source: "ip" };
  } catch (_error) {
    let token = "";
    try {
      token = sessionStorage.getItem("pb-visitor-fallback") || "";
      if (!token) {
        token = crypto.randomUUID();
        sessionStorage.setItem("pb-visitor-fallback", token);
      }
    } catch (_ignored) {
      token = `session-${Date.now()}-${Math.random()}`;
    }
    return { key: await hashValue(token), source: "session" };
  }
}
