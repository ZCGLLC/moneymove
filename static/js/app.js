const pickDate = document.getElementById("pick-date");
const refreshBtn = document.getElementById("refresh-btn");
const statusEl = document.getElementById("status");
const disclaimer = document.getElementById("disclaimer");
const tickets = document.getElementById("tickets");
const pickMeta = document.getElementById("pick-meta");

function todayIso() {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

pickDate.value = todayIso();
loadPicks();

pickDate.addEventListener("change", loadPicks);
refreshBtn.addEventListener("click", () => loadPicks(true));

async function loadPicks(refresh = false) {
  setStatus(refresh ? "Refreshing official draws from NY Open Data…" : "Scoring historical draws…");
  refreshBtn.disabled = true;
  try {
    const date = pickDate.value || todayIso();
    const response = await fetch(refresh ? `/api/refresh?date=${date}` : `/api/picks?date=${date}`, {
      method: refresh ? "POST" : "GET",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      throw new Error(`Request failed (${response.status})`);
    }
    const data = await response.json();
    render(data);
    setStatus("");
  } catch (error) {
    setStatus(error.message || "Could not load picks.");
  } finally {
    refreshBtn.disabled = false;
  }
}

function render(data) {
  pickMeta.textContent = `${data.analyzed_draws.toLocaleString()} draws analyzed · ${formatDate(data.first_draw)} through ${formatDate(data.last_draw)} · next drawing ${formatDate(data.next_draw)}`;
  disclaimer.textContent = data.disclaimer;
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
