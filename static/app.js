const $ = (id) => document.getElementById(id);

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  return res.json();
}

// ---------------- Bit array canvas ----------------

function drawBits(bits) {
  const canvas = $("bit-canvas");
  const ctx = canvas.getContext("2d");
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = "#12151B";
  ctx.fillRect(0, 0, W, H);

  const n = bits.length;
  const cols = Math.ceil(Math.sqrt(n * (W / H)));
  const rows = Math.ceil(n / cols);
  const cellW = W / cols;
  const cellH = H / rows;
  const pad = 1;

  for (let i = 0; i < n; i++) {
    const col = i % cols;
    const row = Math.floor(i / cols);
    const x = col * cellW;
    const y = row * cellH;
    if (bits[i]) {
      ctx.fillStyle = "#4DE8C4";
      ctx.shadowColor = "#4DE8C4";
      ctx.shadowBlur = 3;
    } else {
      ctx.fillStyle = "#1B2027";
      ctx.shadowBlur = 0;
    }
    ctx.fillRect(x + pad, y + pad, cellW - pad * 2, cellH - pad * 2);
  }
  ctx.shadowBlur = 0;
}

// ---------------- Stats + hero ----------------

async function refreshStats() {
  const s = await api("/api/stats");
  $("metric-m").textContent = s.bit_array_size_m ?? "—";
  $("metric-k").textContent = s.hash_count_k ?? "—";
  $("k-inline").textContent = s.hash_count_k ?? "—";
  $("metric-fill").textContent = s.fill_ratio != null ? (s.fill_ratio * 100).toFixed(1) + "%" : "—";
  $("metric-fp").textContent = s.estimated_fp_rate != null ? (s.estimated_fp_rate * 100).toFixed(3) + "%" : "—";

  $("stat-added").textContent = s.items_added ?? 0;
  $("stat-dupes").textContent = s.duplicates_caught ?? 0;
  $("stat-fp").textContent = s.false_positives ?? 0;
  $("stat-log").textContent = s.log_size ?? 0;
}

async function refreshBits() {
  const data = await api("/api/bits");
  drawBits(data.bits);
}

async function refreshFeed() {
  const events = await api("/api/recent");
  const list = $("feed-list");
  if (!events.length) {
    list.innerHTML = '<li class="feed-empty">Nothing yet — add an item above.</li>';
    return;
  }
  list.innerHTML = events.map((e) => {
    let tag = '<span class="tag tag-added">added</span>';
    if (e.status === "duplicate") tag = '<span class="tag tag-dupe">duplicate</span>';
    else if (e.was_false_positive) tag = '<span class="tag tag-fp">false positive</span>';
    return `<li><span>${escapeHtml(e.item)}</span>${tag}</li>`;
  }).join("");
}

async function refreshStack() {
  const ops = await api("/api/stack");
  const el = $("stack-list");
  el.innerHTML = ops.length
    ? ops.map((o) => `<li>${o.op} <span class="muted">${escapeHtml(o.item)}</span></li>`).join("")
    : '<li class="muted">empty</li>';
}

async function refreshBst() {
  const items = await api("/api/bst-traversal");
  const el = $("bst-list");
  el.innerHTML = items.length
    ? items.slice(0, 12).map((i) => `<li>${escapeHtml(i)}</li>`).join("")
    : '<li class="muted">empty</li>';
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

async function refreshAll() {
  await Promise.all([refreshStats(), refreshBits(), refreshFeed(), refreshStack(), refreshBst()]);
}

// ---------------- Collision graph (circular layout, no deps) ----------------

async function refreshGraph() {
  const data = await api("/api/graph");
  $("graph-nodes").textContent = data.nodes.length;
  $("graph-clusters").textContent = data.cluster_count;

  const svg = $("graph-svg");
  svg.innerHTML = "";
  const W = 600, H = 360, cx = W / 2, cy = H / 2, r = Math.min(W, H) / 2 - 50;

  const positions = {};
  data.nodes.forEach((node, i) => {
    const angle = (2 * Math.PI * i) / Math.max(1, data.nodes.length);
    positions[node.id] = {
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle),
    };
  });

  const ns = "http://www.w3.org/2000/svg";

  data.edges.forEach((e) => {
    const a = positions[e.source], b = positions[e.target];
    if (!a || !b) return;
    const line = document.createElementNS(ns, "line");
    line.setAttribute("x1", a.x); line.setAttribute("y1", a.y);
    line.setAttribute("x2", b.x); line.setAttribute("y2", b.y);
    line.setAttribute("stroke", "#6C7CE0");
    line.setAttribute("stroke-width", "1");
    line.setAttribute("opacity", "0.5");
    svg.appendChild(line);
  });

  data.nodes.forEach((node) => {
    const p = positions[node.id];
    const circle = document.createElementNS(ns, "circle");
    circle.setAttribute("cx", p.x); circle.setAttribute("cy", p.y);
    circle.setAttribute("r", 4);
    circle.setAttribute("fill", "#4DE8C4");
    const title = document.createElementNS(ns, "title");
    title.textContent = node.id;
    circle.appendChild(title);
    svg.appendChild(circle);
  });

  if (!data.nodes.length) {
    const text = document.createElementNS(ns, "text");
    text.setAttribute("x", cx); text.setAttribute("y", cy);
    text.setAttribute("fill", "#7C8593");
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("font-family", "IBM Plex Mono, monospace");
    text.setAttribute("font-size", "13");
    text.textContent = "No items yet";
    svg.appendChild(text);
  }
}

// ---------------- Benchmark (Phase 3) ----------------

async function runBenchmark() {
  const data = await api("/api/benchmark", { method: "POST", body: JSON.stringify({}) });
  if (data.error) {
    $("bench-target").textContent = "Add some items first.";
    return;
  }
  $("bench-target").textContent = `target: "${data.target}"`;
  const rows = Object.entries(data.results).map(([method, r]) => `
    <tr>
      <td>${method.replaceAll("_", " ")}</td>
      <td>${r.found}</td>
      <td>${r.steps}</td>
      <td>${r.time_us}</td>
    </tr>`).join("");
  $("bench-table").querySelector("tbody").innerHTML = rows;
}

// ---------------- Greedy allocator (Phase 4) ----------------

async function runGreedy() {
  const data = await api("/api/greedy", { method: "POST", body: JSON.stringify({}) });
  const maxBits = Math.max(...data.map((d) => d.bits), 1);
  $("greedy-bars").innerHTML = data.map((d) => `
    <div class="greedy-row">
      <div class="greedy-name">${d.name}</div>
      <div class="greedy-track"><div class="greedy-fill" style="width:${(d.bits / maxBits) * 100}%"></div></div>
      <div class="greedy-val">${d.bits.toLocaleString()} bits</div>
    </div>
    <div class="greedy-row" style="margin-top:-10px">
      <div></div>
      <div class="muted" style="font-size:12px">fp rate: ${(d.fp_rate * 100).toFixed(4)}% · ${d.items} items</div>
      <div></div>
    </div>
  `).join("");
}

// ---------------- Event wiring ----------------

$("add-btn").addEventListener("click", async () => {
  const input = $("item-input");
  const item = input.value.trim();
  if (!item) return;
  await api("/api/add", { method: "POST", body: JSON.stringify({ item }) });
  input.value = "";
  refreshAll();
});

$("item-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") $("add-btn").click();
});

$("seed-btn").addEventListener("click", async () => {
  await api("/api/seed", { method: "POST", body: JSON.stringify({ count: 50, duplicate_ratio: 0.25 }) });
  refreshAll();
});

$("reset-btn").addEventListener("click", async () => {
  await api("/api/reset", { method: "POST", body: JSON.stringify({}) });
  refreshAll();
  refreshGraph();
});

$("graph-refresh").addEventListener("click", refreshGraph);
$("bench-btn").addEventListener("click", runBenchmark);
$("greedy-btn").addEventListener("click", runGreedy);

// initial load
refreshAll();
refreshGraph();
