const state = {
  data: null,
  activeView: "overview",
  currentRunId: null,
  pollTimer: null,
};

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const fmtCount = (arr) => (Array.isArray(arr) ? arr.length : 0);

function setStatus(text, meta) {
  $("#status-text").textContent = text;
  $("#status-meta").textContent = meta;
}

function setRunnerStatus(kind, meta = "") {
  const el = $("#runner-status");
  el.className = `runner-status ${kind}`;
  el.textContent = kind[0].toUpperCase() + kind.slice(1);
  $("#runner-meta").textContent = meta;
}

function renderStats(data) {
  const stats = [
    { label: "Collections", value: fmtCount(data.collections), detail: "MongoDB entities used by the API" },
    { label: "Update groups", value: fmtCount(data.sections), detail: "Major product areas shown on the dashboard" },
    { label: "Endpoint groups", value: fmtCount(data.endpoints), detail: "Quick routes for testing flows" },
    { label: "Major updates", value: fmtCount(data.major_updates), detail: "Key backend capabilities" },
  ];
  const root = $("#stats-grid");
  root.innerHTML = stats.map((s) => `
    <div class="stat">
      <div class="label">${s.label}</div>
      <div class="value">${s.value}</div>
      <div class="detail">${s.detail}</div>
    </div>
  `).join("");
}

function renderUpdates(data) {
  const tpl = $("#card-template");
  const root = $("#updates-grid");
  root.innerHTML = "";
  data.major_updates.forEach((item, idx) => {
    const node = tpl.content.cloneNode(true);
    $(".card h3", node).textContent = `Update ${idx + 1}`;
    $(".pill", node).textContent = idx === 0 ? "Live" : "Ready";
    $(".card p", node).textContent = item;
    $(".tag-list", node).innerHTML = `
      <span class="tag">Backend</span>
      <span class="tag">Testable</span>
      <span class="tag">Modern</span>
    `;
    root.appendChild(node);
  });
}

function renderEndpoints(data) {
  const tpl = $("#endpoint-template");
  const root = $("#endpoint-groups");
  root.innerHTML = "";
  data.endpoints.forEach((group) => {
    const node = tpl.content.cloneNode(true);
    $(".endpoint-head h3", node).textContent = group.group;
    const btn = $(".copy-btn", node);
    btn.addEventListener("click", async () => {
      const text = group.items.join("\n");
      await navigator.clipboard.writeText(text);
      btn.textContent = "Copied";
      setTimeout(() => (btn.textContent = "Copy"), 1200);
    });
    const ul = $("ul", node);
    ul.innerHTML = group.items.map((item) => `<li><code>${item}</code></li>`).join("");
    root.appendChild(node);
  });
}

function renderCollections(data) {
  const tpl = $("#card-template");
  const root = $("#collections-grid");
  root.innerHTML = "";
  data.collections.forEach((col) => {
    const node = tpl.content.cloneNode(true);
    $(".card h3", node).textContent = col.name;
    $(".pill", node).textContent = "MongoDB";
    $(".card p", node).textContent = col.purpose;
    $(".tag-list", node).innerHTML = col.hot_fields.map((f) => `<span class="tag">${f}</span>`).join("");
    root.appendChild(node);
  });
}

function renderAll(data) {
  $("#dashboard-title").textContent = data.title;
  $("#dashboard-subtitle").textContent = data.subtitle;
  renderStats(data);
  renderUpdates(data);
  renderEndpoints(data);
  renderCollections(data);
}

function setView(view) {
  state.activeView = view;
  $$(".nav-item").forEach((btn) => btn.classList.toggle("active", btn.dataset.view === view));
  $$(".view").forEach((panel) => panel.classList.toggle("hidden", panel.dataset.panel !== view));
}

function renderRun(run) {
  if (!run) return;
  setRunnerStatus(run.status || "idle", `${run.kind}${run.target ? ` • ${run.target}` : ""}`);
  $("#runner-log").textContent = run.tail || (Array.isArray(run.lines) ? run.lines.join("\n") : "");
}

async function pollRun(runId) {
  if (!runId) return;
  const res = await fetch(`/api/dashboard/test-runs/${runId}`);
  if (!res.ok) return;
  const run = await res.json();
  renderRun(run);
  if (run.status === "completed" || run.status === "failed") {
    clearInterval(state.pollTimer);
    state.pollTimer = null;
    state.currentRunId = null;
    setStatus(run.status === "completed" ? "Tests completed" : "Tests failed", `Exit code: ${run.exit_code}`);
  }
}

async function startRun(kind) {
  const target = ($("#test-target")?.value || "").trim();
  const payload = { kind, ...(target ? { target } : {}) };
  const res = await fetch("/api/dashboard/test-runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const msg = await res.text();
    setRunnerStatus("failed", msg);
    return;
  }
  const run = await res.json();
  state.currentRunId = run.run_id;
  $("#runner-log").textContent = `Started ${kind}...\n${run.command.join(" ")}`;
  setRunnerStatus("running", `Run id: ${run.run_id}`);
  setStatus("Test run started", kind);
  clearInterval(state.pollTimer);
  state.pollTimer = setInterval(() => pollRun(run.run_id), 1000);
  pollRun(run.run_id);
}

async function init() {
  setStatus("Loading dashboard...", "Fetching backend snapshot");
  const res = await fetch("/api/dashboard/data");
  if (!res.ok) {
    setStatus("Dashboard unavailable", `HTTP ${res.status}`);
    return;
  }
  const data = await res.json();
  state.data = data;
  renderAll(data);
  setStatus("Backend online", `${fmtCount(data.endpoints)} endpoint groups ready`);

  $$(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => setView(btn.dataset.view));
  });

  $$("[data-run]").forEach((btn) => {
    btn.addEventListener("click", () => startRun(btn.dataset.run));
  });
  setView("overview");
  setRunnerStatus("idle", "Ready to run tests");
}

init().catch((err) => {
  console.error(err);
  setStatus("Dashboard error", String(err.message || err));
});
