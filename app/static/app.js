"use strict";

const $ = (id) => document.getElementById(id);

async function api(path, opts) {
  const resp = await fetch(path, opts);
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(data.error || `HTTP ${resp.status}`);
  return data;
}

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s ?? "";
  return d.innerHTML;
}

/* ---------- theme ---------- */
function applyTheme(t) {
  document.documentElement.dataset.theme = t;
  $("theme-toggle").textContent = t === "dark" ? "☀️" : "🌙";
  localStorage.setItem("wiki-theme", t);
}
$("theme-toggle").addEventListener("click", () => {
  applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
});
applyTheme(localStorage.getItem("wiki-theme") || "light");

/* ---------- tabs ---------- */
document.querySelectorAll(".tabs button").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tabs button").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    btn.classList.add("active");
    $("tab-" + btn.dataset.tab).classList.add("active");
    if (btn.dataset.tab === "graph") initGraph();
    if (btn.dataset.tab === "ingest") loadInbox();
  });
});

/* ---------- health ---------- */
async function loadHealth() {
  try {
    const h = await api("/api/health");
    $("health").textContent = `${h.wiki_pages} 页 · ${h.raw_chapters} 章 · ${h.llm_configured ? "LLM 在线" : "本地模式"}`;
  } catch {
    $("health").textContent = "服务不可用";
  }
}
loadHealth();

/* ---------- browse ---------- */
async function showPages() {
  const { pages } = await api("/api/pages");
  $("results-title").textContent = `全部页面（${pages.length}）`;
  $("results").innerHTML = "";
  for (const p of pages) {
    $("results").appendChild(resultCard(p.title, p.type, p.path, "", () => openPage(p.path)));
  }
}

function resultCard(title, type, path, snippet, onClick) {
  const div = document.createElement("div");
  div.className = "result";
  div.innerHTML = `
    <div class="title">${esc(title)}</div>
    <div class="meta">${esc(type || "")} · ${esc(path)}</div>
    ${snippet ? `<div class="snip">${esc(snippet)}</div>` : ""}`;
  div.addEventListener("click", onClick);
  return div;
}

async function doSearch() {
  const q = ($("search-q").value.trim() || $("global-q").value.trim());
  if (!q) return showPages();
  $("search-q").value = q;
  const raw = $("search-raw").checked ? 1 : 0;
  const { results } = await api(`/api/search?q=${encodeURIComponent(q)}&raw=${raw}&top=30`);
  $("results-title").textContent = `搜索结果（${results.length}）`;
  $("results").innerHTML = "";
  for (const r of results) {
    $("results").appendChild(resultCard(r.title, r.kind, r.path, r.snippet, () => {
      if (r.kind === "wiki") openPage(r.path);
      else window.open("/api/raw?path=" + encodeURIComponent(r.path), "_blank");
    }));
  }
}

async function openPage(path) {
  const p = await api("/api/page?path=" + encodeURIComponent(path));
  $("page-view").innerHTML = p.html;
  const fm = p.frontmatter || {};
  $("page-meta").textContent =
    `verified=${fm.verified || "-"} · status=${fm.status || "-"} · sources=${fm.sources || "-"} · ${path}`;
  document.querySelector('.tabs button[data-tab="browse"]').click();
}

$("search-btn").addEventListener("click", doSearch);
$("global-search-btn").addEventListener("click", doSearch);
$("search-q").addEventListener("keydown", (e) => { if (e.key === "Enter") doSearch(); });
$("global-q").addEventListener("keydown", (e) => { if (e.key === "Enter") doSearch(); });
showPages().catch(console.error);

/* ---------- graph ---------- */
let graphData = null;
let graphReady = false;

const TYPE_COLORS = {
  domain: "#4f8ef7", entity: "#22b573", process: "#f2994a", concept: "#9b59b6",
  source: "#8f9bb3", coverage: "#e74c3c", overview: "#16a085", index: "#607d8b",
  inbox: "#f1c40f",
};

async function initGraph() {
  if (graphReady) return;
  graphData = await api("/api/graph");
  graphReady = true;
  const legend = $("graph-legend");
  const types = [...new Set(graphData.nodes.map((n) => n.type || "other"))];
  legend.innerHTML = types.map((t) => `<span style="color:${TYPE_COLORS[t] || "#94a3b8"}">● ${t}</span>`).join("");
  startGraph();
}

function startGraph() {
  const canvas = $("graph-canvas");
  const ctx = canvas.getContext("2d");
  const wrap = canvas.parentElement;
  let W = 0, H = 0, DPR = window.devicePixelRatio || 1;

  const nodes = graphData.nodes.map((n) => ({
    ...n, x: Math.random() * 800 - 400, y: Math.random() * 600 - 300,
    vx: 0, vy: 0, r: n.size || 5,
  }));
  const nodeMap = new Map(nodes.map((n) => [n.id, n]));
  const links = graphData.links
    .map((l) => ({ s: nodeMap.get(l.source), t: nodeMap.get(l.target) }))
    .filter((l) => l.s && l.t);

  let view = { x: 0, y: 0, scale: 1 };
  let drag = null;
  let hover = null;
  let running = true;

  function resize() {
    const rect = wrap.getBoundingClientRect();
    W = rect.width; H = rect.height;
    canvas.width = W * DPR; canvas.height = H * DPR;
    canvas.style.width = W + "px"; canvas.style.height = H + "px";
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }
  resize();
  window.addEventListener("resize", resize);

  function sim() {
    const k = 0.045;
    for (const n of nodes) {
      let fx = 0, fy = 0;
      for (const o of nodes) {
        if (n === o) continue;
        let dx = n.x - o.x, dy = n.y - o.y;
        let d2 = dx * dx + dy * dy || 1;
        const f = 9000 / d2;
        fx += dx / Math.sqrt(d2) * f;
        fy += dy / Math.sqrt(d2) * f;
      }
      fx += -n.x * 0.02; fy += -n.y * 0.02;
      n.vx = (n.vx + fx * k) * 0.85;
      n.vy = (n.vy + fy * k) * 0.85;
      n.x += n.vx; n.y += n.vy;
    }
    for (const l of links) {
      const dx = l.t.x - l.s.x, dy = l.t.y - l.s.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const target = 90;
      const f = (dist - target) * 0.008;
      const ux = dx / dist, uy = dy / dist;
      l.s.x += ux * f; l.s.y += uy * f;
      l.t.x -= ux * f; l.t.y -= uy * f;
    }
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    ctx.save();
    ctx.translate(view.x + W / 2, view.y + H / 2);
    ctx.scale(view.scale, view.scale);
    ctx.strokeStyle = "rgba(148,163,184,.35)";
    ctx.lineWidth = 1 / view.scale;
    for (const l of links) {
      ctx.beginPath();
      ctx.moveTo(l.s.x, l.s.y);
      ctx.lineTo(l.t.x, l.t.y);
      ctx.stroke();
    }
    for (const n of nodes) {
      const c = TYPE_COLORS[n.type] || "#94a3b8";
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r / view.scale, 0, Math.PI * 2);
      ctx.fillStyle = c + "cc";
      ctx.fill();
      if (n === hover || n.r >= 8) {
        ctx.fillStyle = "var(--ink)";
        ctx.font = `${11 / view.scale}px Inter, sans-serif`;
        ctx.textAlign = "center";
        ctx.fillText(n.title.slice(0, 18), n.x, n.y - n.r / view.scale - 4);
      }
    }
    ctx.restore();
  }

  function tick() {
    if (!running) return;
    sim();
    draw();
    requestAnimationFrame(tick);
  }
  tick();

  function toWorld(e) {
    const rect = canvas.getBoundingClientRect();
    return {
      x: (e.clientX - rect.left - view.x - W / 2) / view.scale,
      y: (e.clientY - rect.top - view.y - H / 2) / view.scale,
    };
  }

  canvas.addEventListener("pointerdown", (e) => {
    const p = toWorld(e);
    const hit = nodes.find((n) => Math.hypot(n.x - p.x, n.y - p.y) < Math.max(n.r, 8));
    drag = hit ? { n: hit, dx: hit.x - p.x, dy: hit.y - p.y } : { pan: { x: e.clientX, y: e.clientY } };
    canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener("pointermove", (e) => {
    const p = toWorld(e);
    const hit = nodes.find((n) => Math.hypot(n.x - p.x, n.y - p.y) < Math.max(n.r, 8));
    hover = hit || null;
    if (drag) {
      if (drag.n) { drag.n.x = p.x + drag.dx; drag.n.y = p.y + drag.dy; drag.n.vx = drag.n.vy = 0; }
      else { view.x += e.clientX - drag.pan.x; view.y += e.clientY - drag.pan.y; drag.pan = { x: e.clientX, y: e.clientY }; }
    }
  });
  canvas.addEventListener("pointerup", (e) => {
    if (drag && drag.n) {
      openPage(drag.n.id).catch(() => {});
    }
    drag = null;
  });
  canvas.addEventListener("wheel", (e) => {
    e.preventDefault();
    const f = e.deltaY < 0 ? 1.1 : 0.9;
    view.scale = Math.min(3, Math.max(0.25, view.scale * f));
  }, { passive: false });
  $("graph-reload").addEventListener("click", () => {
    for (const n of nodes) { n.x = Math.random() * 800 - 400; n.y = Math.random() * 600 - 300; n.vx = n.vy = 0; }
    view = { x: 0, y: 0, scale: 1 };
  });
}

/* ---------- ask ---------- */
let lastPrompt = "";

function addMsg(role, html) {
  const wrap = document.createElement("div");
  wrap.className = "msg " + role;
  wrap.innerHTML = `<div class="avatar">${role === "user" ? "🙋" : "🤖"}</div><div class="bubble">${html}</div>`;
  $("chat").appendChild(wrap);
  $("chat").scrollTop = $("chat").scrollHeight;
  return wrap;
}

async function renderMarkdown(md) {
  const r = await api("/api/render-md", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ md }),
  });
  return r.html || esc(md);
}

async function doAsk() {
  const question = $("ask-q").value.trim();
  if (!question) return;
  $("ask-q").value = "";
  addMsg("user", esc(question));
  const waiting = addMsg("assistant", '<span class="typing">正在检索与思考</span>');
  try {
    const r = await api("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, raw: $("ask-raw").checked }),
    });
    const html = await renderMarkdown(r.answer);
    const cites = r.citations.length
      ? `<div class="cites"><b>引用（${r.citations.length}）</b>` +
        r.citations.slice(0, 8).map((c) =>
          `<div class="cit"><a href="/api/raw?path=${encodeURIComponent(c.path)}" target="_blank">${esc(c.title)}</a> · <span class="muted">${esc(c.path)}</span></div>`).join("") +
        `</div>`
      : "";
    waiting.innerHTML = html + cites;
    const copyBtn = document.createElement("button");
    copyBtn.className = "secondary small";
    copyBtn.textContent = "复制 Prompt 给 Codex";
    copyBtn.style.marginTop = "8px";
    copyBtn.addEventListener("click", () => {
      navigator.clipboard.writeText(r.prompt).then(() => { copyBtn.textContent = "已复制"; });
    });
    waiting.querySelector(".bubble").appendChild(copyBtn);
    lastPrompt = r.prompt;
  } catch (e) {
    waiting.innerHTML = `<p class="muted">提问失败：${esc(e.message)}</p>`;
  }
}

$("ask-btn").addEventListener("click", doAsk);
$("ask-q").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); doAsk(); }
});

/* ---------- ingest ---------- */
$("ingest-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = $("in-title").value.trim();
  const content = $("in-content").value.trim();
  if (!title || !content) { $("in-result").textContent = "标题和内容必填"; return; }
  $("in-result").textContent = "保存中…";
  try {
    const r = await api("/api/ingest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content, source_url: $("in-url").value.trim() }),
    });
    $("in-result").textContent = `已保存：${r.path}`;
    $("in-title").value = ""; $("in-content").value = ""; $("in-url").value = "";
    loadInbox();
  } catch (err) {
    $("in-result").textContent = "保存失败：" + err.message;
  }
});

async function loadInbox() {
  try {
    const { items } = await api("/api/inbox");
    const box = $("inbox-list");
    box.innerHTML = items.length
      ? items.map((it) => `
        <div class="result">
          <div class="title">${esc(it.title)}</div>
          <div class="meta">${esc(it.status)} · ${esc(it.path)}</div>
          ${it.source_url ? `<div class="snip">来源：${esc(it.source_url)}</div>` : ""}
        </div>`).join("")
      : "<p class=muted>暂无待摄入内容。</p>";
  } catch (err) {
    $("inbox-list").innerHTML = `<p class=muted>读取失败：${esc(err.message)}</p>`;
  }
}
