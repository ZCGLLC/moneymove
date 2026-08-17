const pickDate = document.getElementById("pick-date");
const refreshBtn = document.getElementById("refresh-btn");
const generateBtn = document.getElementById("generate-btn");
const statusEl = document.getElementById("status");
const disclaimer = document.getElementById("disclaimer");
const tickets = document.getElementById("tickets");
const pickMeta = document.getElementById("pick-meta");
const visitorNote = document.getElementById("visitor-note");

let draws = [];
let visitorKey = "";
let visitorSource = "";
let generation = 1;
let sessionUsed = [];
let syncTimer = null;

function todayIso() {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

pickDate.value = todayIso();
boot();
scheduleDrawSync();

pickDate.addEventListener("change", () => {
  generation = 1;
  sessionUsed = [];
  showPicks();
});
refreshBtn.addEventListener("click", () => boot());
generateBtn.addEventListener("click", () => {
  if (!draws.length || !visitorKey) return;
  generation += 1;
  showPicks();
});

async function boot() {
  setStatus("Loading every official Powerball drawing and preparing your unique tickets…");
  refreshBtn.disabled = true;
  generateBtn.disabled = true;
  try {
    const [latestDraws, visitor] = await Promise.all([loadDraws(true), resolveVisitorKey()]);
    draws = latestDraws;
    visitorKey = visitor.key;
    visitorSource = visitor.source;
    generation = 1;
    sessionUsed = [];
    showPicks();
    setStatus(`Archive current through ${formatDate(draws[draws.length - 1].date)}. New official draws are pulled automatically.`);
  } catch (error) {
    setStatus(error.message || "Could not load picks.");
  } finally {
    refreshBtn.disabled = false;
    generateBtn.disabled = false;
  }
}

function showPicks() {
  if (!draws.length || !visitorKey) return;
  const data = generateDailyPicks(draws, pickDate.value || todayIso(), visitorKey, generation, sessionUsed);
  data.tickets.forEach((ticket) => {
    sessionUsed.push(`${ticket.white.join(",")}|${ticket.powerball}`);
  });
  render(data);
}

function render(data) {
  pickMeta.textContent = `${data.analyzed_draws.toLocaleString()} official draws analyzed · ${formatDate(data.first_draw)} through ${formatDate(data.last_draw)} · next drawing ${formatDate(data.next_draw)}`;
  disclaimer.textContent = data.disclaimer;
  const sourceLabel =
    visitorSource === "ip"
      ? "These tickets are unique to your IP address and are not shared with other visitors."
      : "Your public IP could not be read, so this browser session is used instead to keep your tickets unique.";
  visitorNote.textContent = `${sourceLabel} Round ${data.generation}. Click Generate new numbers for another unique trio.`;
  tickets.innerHTML = data.tickets
    .map(
      (ticket) => `
      <article class="ticket">
        <h2>${ticket.name}</h2>
        <p>${ticket.summary}</p>
        <div class="balls">
          ${ticket.white.map((n) => ball(n)).join("")}
          ${ball(ticket.powerball, true)}
        </div>
      </article>`
    )
    .join("");

  fillList("hot-white", data.stats.hottest_white, "draws");
  fillList("due-white", data.stats.overdue_white, "draws ago");
  fillList("hot-pb", data.stats.hottest_powerball, "draws");
  fillList("all-white", data.stats.hottest_white_all_time, "all-time draws");

  const body = document.getElementById("recent-body");
  body.innerHTML = data.stats.recent_draws
    .map(
      (draw) => `
      <tr>
        <td>${formatDate(draw.date)}</td>
        <td>${draw.white.map((n) => pad(n)).join(" · ")}</td>
        <td>${pad(draw.powerball)}</td>
        <td>${draw.multiplier ? draw.multiplier + "x" : "—"}</td>
      </tr>`
    )
    .join("");
}

function fillList(id, rows, unit) {
  document.getElementById(id).innerHTML = rows
    .map(([number, count]) => `<li><span>${pad(number)}</span><span>${count} ${unit}</span></li>`)
    .join("");
}

function ball(number, power = false) {
  return `<span class="ball${power ? " power" : ""}">${pad(number)}</span>`;
}

function pad(number) {
  return String(number).padStart(2, "0");
}

function formatDate(iso) {
  const [year, month, day] = iso.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function setStatus(message) {
  statusEl.hidden = !message;
  statusEl.textContent = message;
}

function easternNow() {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/New_York",
    weekday: "short",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(new Date());
  const read = (type) => parts.find((part) => part.type === type)?.value;
  return { weekday: read("weekday"), hour: Number(read("hour")), minute: Number(read("minute")) };
}

function afterDrawWindow() {
  const { weekday, hour } = easternNow();
  const drawNight = weekday === "Mon" || weekday === "Wed" || weekday === "Sat";
  const followingMorning = weekday === "Tue" || weekday === "Thu" || weekday === "Sun";
  return (drawNight && hour >= 22) || (followingMorning && hour < 8);
}

function scheduleDrawSync() {
  if (syncTimer) clearInterval(syncTimer);
  const tick = async () => {
    try {
      const latest = await loadDraws(true);
      const previousLast = draws.length ? draws[draws.length - 1].date : "";
      const nextLast = latest.length ? latest[latest.length - 1].date : "";
      draws = latest;
      if (nextLast && nextLast !== previousLast) {
        generation = 1;
        sessionUsed = [];
        showPicks();
        setStatus(`New official drawing added for ${formatDate(nextLast)}. Your tickets now include that result.`);
      }
    } catch (_error) {
      /* keep the last successful archive */
    }
    scheduleDrawSync();
  };
  const delay = afterDrawWindow() ? 3 * 60 * 1000 : 15 * 60 * 1000;
  syncTimer = setTimeout(tick, delay);
}
