const api = async (path, opts = {}) => {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`${res.status} ${txt}`);
  }
  return res.json();
};

const el = (id) => document.getElementById(id);

const verticalSelect = el("vertical-select");
const dataVerticalSelect = el("data-vertical-select");
const fixtureSelect = el("fixture-select");
const fixtureDetails = el("fixture-details");

const runSingleStatus = el("run-single-status");
const runYamlStatus = el("run-yaml-status");
const queueStatus = el("queue-status");
const runsList = el("runs-list");

const dataLimit = el("data-limit");
const dataOffset = el("data-offset");

const signalsTable = el("signals-table");
const painsTable = el("pains-table");
const clustersTable = el("clusters-table");
const trendsTable = el("trends-table");
const logsBox = el("logs-box");
const logsService = el("logs-service");
const logsTail = el("logs-tail");

const setStatus = (target, text, type = "") => {
  target.textContent = text;
  target.dataset.type = type;
};

const renderQueue = (queues) => {
  queueStatus.innerHTML = "";
  Object.entries(queues).forEach(([name, stats]) => {
    const card = document.createElement("div");
    card.className = "queue-card";
    card.innerHTML = `
      <h4>${name}</h4>
      <span>pending: ${stats.pending}</span>
      <span>retry: ${stats.retry}</span>
      <span>dlq: ${stats.dlq}</span>
    `;
    queueStatus.appendChild(card);
  });
};

const renderRuns = (items) => {
  runsList.innerHTML = "";
  items.slice(-6).reverse().forEach((run) => {
    const row = document.createElement("div");
    row.className = "run-item";
    row.innerHTML = `
      <span>${run.mode} • ${run.status}</span>
      <span class="muted">${new Date(run.started_at * 1000).toLocaleTimeString()}</span>
    `;
    runsList.appendChild(row);
  });
};

const renderTable = (container, items, type) => {
  container.innerHTML = "";
  if (!items.length) {
    container.innerHTML = "<div class='muted'>Aucune donnée.</div>";
    return;
  }
  items.forEach((item) => {
    const row = document.createElement("div");
    row.className = "table-row";
    if (type === "signals") {
      row.innerHTML = `
        <div class="muted">#${item.id}</div>
        <div>${item.content?.slice(0, 140) || ""}</div>
        <div class="muted">${item.source}</div>
      `;
    } else if (type === "pains") {
      row.innerHTML = `
        <div class="muted">#${item.id}</div>
        <div>${item.breakdown?.label || item.breakdown?.summary || "pain"}</div>
        <div class="muted">score ${item.pain_score?.toFixed(2) || "0"}</div>
      `;
    } else if (type === "clusters") {
      row.innerHTML = `
        <div class="muted">#${item.id}</div>
        <div>${item.title || "(untitled)"}</div>
        <div class="muted">size ${item.size ?? 0}</div>
      `;
    } else {
      row.innerHTML = `
        <div class="muted">#${item.cluster_id}</div>
        <div>${item.title || "(untitled)"}</div>
        <div class="muted">score ${item.score?.toFixed(2) || "0"}</div>
      `;
    }
    container.appendChild(row);
  });
};

const loadVerticals = async () => {
  const data = await api("/verticals");
  verticalSelect.innerHTML = "";
  dataVerticalSelect.innerHTML = "";
  data.forEach((v) => {
    const opt = document.createElement("option");
    opt.value = v.id;
    opt.textContent = `${v.name} (#${v.id})`;
    verticalSelect.appendChild(opt.cloneNode(true));
    dataVerticalSelect.appendChild(opt);
  });
};

const loadFixtures = async () => {
  const data = await api("/ops/fixtures");
  fixtureSelect.innerHTML = "";
  data.items.forEach((fx) => {
    const opt = document.createElement("option");
    opt.value = fx.file;
    opt.textContent = fx.name;
    opt.dataset.details = JSON.stringify(fx);
    fixtureSelect.appendChild(opt);
  });
  updateFixtureDetails();
};

const updateFixtureDetails = () => {
  const opt = fixtureSelect.selectedOptions[0];
  if (!opt) {
    fixtureDetails.textContent = "";
    return;
  }
  const fx = JSON.parse(opt.dataset.details || "{}");
  const queries = (fx.default_queries || []).map((q) => `“${q}”`).join(", ");
  fixtureDetails.textContent = queries ? `Queries: ${queries}` : "Aucune query";
};

const loadQueues = async () => {
  const data = await api("/ops/queues");
  renderQueue(data.queues);
};

const loadRuns = async () => {
  const data = await api("/ops/runs");
  renderRuns(data.items || []);
};

const loadSignals = async () => {
  const vid = dataVerticalSelect.value;
  const limit = dataLimit.value;
  const offset = dataOffset.value;
  const data = await api(`/signals?vertical_id=${vid}&limit=${limit}&offset=${offset}`);
  renderTable(signalsTable, data.items || [], "signals");
};

const loadPains = async () => {
  const vid = dataVerticalSelect.value;
  const limit = dataLimit.value;
  const offset = dataOffset.value;
  const data = await api(`/pains?vertical_id=${vid}&limit=${limit}&offset=${offset}`);
  renderTable(painsTable, data.items || [], "pains");
};

const loadTrends = async () => {
  const vid = dataVerticalSelect.value;
  const limit = dataLimit.value;
  const offset = dataOffset.value;
  const data = await api(`/trending?vertical_id=${vid}&limit=${limit}&offset=${offset}`);
  renderTable(trendsTable, data.items || [], "trends");
};

const loadClusters = async () => {
  const vid = dataVerticalSelect.value;
  const limit = dataLimit.value;
  const offset = dataOffset.value;
  const data = await api(`/clusters?vertical_id=${vid}&limit=${limit}&offset=${offset}`);
  renderTable(clustersTable, data.items || [], "clusters");
};

const loadLogs = async () => {
  const svc = logsService.value;
  const tail = logsTail.value || 200;
  try {
    const data = await api(`/ops/logs?service=${encodeURIComponent(svc)}&tail=${tail}`);
    logsBox.textContent = (data.lines || []).join("\n") || "Aucun log.";
  } catch (err) {
    logsBox.textContent = `Erreur logs: ${err}`;
  }
};

const refreshAll = async () => {
  try {
    await api("/health");
    el("api-status").textContent = "API: OK";
  } catch {
    el("api-status").textContent = "API: ERROR";
  }
  await Promise.all([loadQueues(), loadRuns()]);
};

const runSingle = async () => {
  runSingleStatus.textContent = "Envoi…";
  const payload = {
    mode: "single",
    vertical_id: Number(verticalSelect.value),
    source: el("source-select").value,
    query: el("query-input").value,
    limit: Number(el("limit-input").value),
  };
  const res = await api("/ops/run", { method: "POST", body: JSON.stringify(payload) });
  runSingleStatus.textContent = `Run ${res.run_id} lancé`;
  await refreshAll();
};

const runYaml = async () => {
  runYamlStatus.textContent = "Envoi…";
  const payload = {
    mode: "yaml",
    fixture: fixtureSelect.value,
    source: "reddit",
    limit: Number(el("yaml-limit-input").value),
  };
  const res = await api("/ops/run", { method: "POST", body: JSON.stringify(payload) });
  runYamlStatus.textContent = `Run ${res.run_id} lancé`;
  await refreshAll();
};

const refreshData = async () => {
  const activeTab = document.querySelector(".tab.active")?.dataset.tab;
  if (activeTab === "signals") return loadSignals();
  if (activeTab === "pains") return loadPains();
  if (activeTab === "clusters") return loadClusters();
  if (activeTab === "logs") return loadLogs();
  return loadTrends();
};

const initTabs = () => {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
      tab.classList.add("active");
      el(`tab-${tab.dataset.tab}`).classList.add("active");
      refreshData();
    });
  });
};

const boot = async () => {
  await loadVerticals();
  await loadFixtures();
  initTabs();
  await refreshAll();
  await refreshData();
  setInterval(refreshAll, 5000);
};

fixtureSelect.addEventListener("change", updateFixtureDetails);
el("run-single").addEventListener("click", runSingle);
el("run-yaml").addEventListener("click", runYaml);
el("refresh-all").addEventListener("click", refreshAll);
el("refresh-data").addEventListener("click", refreshData);
el("refresh-logs").addEventListener("click", loadLogs);

boot();
