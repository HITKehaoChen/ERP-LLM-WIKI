"use strict";

const $ = (id) => document.getElementById(id);

async function json(url, opts) {
  const resp = await fetch(url, opts);
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(data.error || `HTTP ${resp.status}`);
  return data;
}

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s ?? "";
  return d.innerHTML;
}

// ---------- tabs ----------
document.querySelectorAll(".tabs button").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tabs button").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    btn.classList.add("active");
    $("tab-" + btn.dataset.tab).classList.add("active");
  });
});

// ---------- health ----------
async function loadHealth() {
  try {
    const h = await json("/api/health");
    $("health").textContent =
      `wiki 页 ${h.wiki_pages} · 官方章节 ${h.raw_chapters} · LLM ${h.llm_configured ? `已配置（${h.model}）` : "未配置（本地检索模式）"}`;
  } catch (e) {
    $("health").textContent = "服务不可用";
  }
}
loadHealth();

// ---------- browse ----------
async function showPages() {
  const { pages } = await json("/api/pages");
  $("results-title").textContent = `全部页面（${pages.length}）`;
  $("results").innerHTML = "";
  for (const p of pages) {
    const div = document.createElement("div");
    div.className = "result";
    div.innerHTML = `<div class="title">${esc(p.title)}</div><div class="meta">${esc(p.type)} · ${esc(p.path)}</div>`;
    div.addEventListener("click", () => openPage(p.path));
    $("results").appendChild(div);
  }
}

async function openPage(path) {
  try {
    const p = await json("/api/page?path=" + encodeURIComponent(path));
    $("page-view").innerHTML = `<div class="page-body">${p.html}</div>`;
    const fm = p.frontmatter || {};
    $("page-meta").textContent =
      `verified=${fm.verified || "-"} · status=${fm.status || "-"} · sources=${fm.sources || "-"} · ${path}`;
  } catch (e) {
    $("page-view").innerHTML = `<p>无法打开：${esc(e.message)}</p>`;
  }
}

async function doSearch() {
  const q = $("search-q").value.trim();
  if (!q) return showPages();
  const raw = $("search-raw").checked ? 1 : 0;
  const { results } = await json(`/api/search?q=${encodeURIComponent(q)}&raw=${raw}&top=20`);
  $("results-title").textContent = `搜索结果（${results.length}）`;
  $("results").innerHTML = "";
  for (const r of results) {
    const div = document.createElement("div");
    div.className = "result";
    div.innerHTML = `
      <div class="title">${esc(r.title)}</div>
      <div class="meta">${esc(r.kind)} · ${esc(r.path)} · 得分 ${r.score}</div>
      <div class="snip">${esc(r.snippet)}</div>`;
    div.addEventListener("click", () => {
      if (r.kind === "wiki") openPage(r.path);
      else window.open("/api/raw?path=" + encodeURIComponent(r.path), "_blank");
    });
    $("results").appendChild(div);
  }
}

$("search-btn").addEventListener("click", doSearch);
$("search-q").addEventListener("keydown", (e) => { if (e.key === "Enter") doSearch(); });
showPages().catch(console.error);

// ---------- ask ----------
let lastPrompt = "";

async function doAsk() {
  const question = $("ask-q").value.trim();
  if (!question) return;
  $("answer").innerHTML = "<p class=muted>检索中…</p>";
  $("ask-mode").textContent = "";
  $("citations").innerHTML = "";
  $("copy-prompt").style.display = "none";
  try {
    const r = await json("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, raw: $("ask-raw").checked }),
    });
    $("ask-mode").textContent = r.mode === "llm" ? "LLM 回答" : "本地检索（未配置 LLM）";
    $("ask-mode").className = "badge" + (r.mode === "local" ? " local" : "");
    $("answer").innerHTML = `<div class="page-body">${await renderAnswer(r.answer)}</div>`;
    $("citations").innerHTML = "<h2>引用</h2>" + r.citations.map((c, i) => `
      <div class="cit">
        <b>${i + 1}. ${esc(c.title)}</b> <span class="path">${esc(c.path)}</span><br>
        ${esc(c.snippet)}
      </div>`).join("");
    lastPrompt = r.prompt;
    $("copy-prompt").style.display = "inline-block";
  } catch (e) {
    $("answer").innerHTML = `<p>提问失败：${esc(e.message)}</p>`;
  }
}

async function renderAnswer(md) {
  const r = await fetch("/api/render-md", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ md }),
  });
  const data = await r.json().catch(() => ({ html: md }));
  return data.html || md;
}

$("ask-btn").addEventListener("click", doAsk);
$("copy-prompt").addEventListener("click", () => {
  navigator.clipboard.writeText(lastPrompt).then(
    () => { $("copy-prompt").textContent = "已复制"; setTimeout(() => { $("copy-prompt").textContent = "复制给 Codex 的 Prompt"; }, 1500); },
    () => {}
  );
});

// ---------- ingest ----------
async function doIngest() {
  const title = $("in-title").value.trim();
  const content = $("in-content").value.trim();
  const source_url = $("in-url").value.trim();
  if (!title || !content) { $("in-result").textContent = "标题和内容必填"; return; }
  $("in-result").textContent = "保存中…";
  try {
    const r = await json("/api/ingest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content, source_url }),
    });
    $("in-result").textContent = `已保存：${r.path}`;
    $("in-title").value = ""; $("in-content").value = ""; $("in-url").value = "";
  } catch (e) {
    $("in-result").textContent = "保存失败：" + e.message;
  }
}
$("in-btn").addEventListener("click", doIngest);

async function loadInbox() {
  try {
    const { items } = await json("/api/inbox");
    const box = $("inbox-list");
    box.innerHTML = items.length
      ? items.map((it) => `
        <div class="result">
          <div class="title">${esc(it.title)}</div>
          <div class="meta">${esc(it.status)} · ${esc(it.path)}</div>
          ${it.source_url ? `<div class="snip">来源：${esc(it.source_url)}</div>` : ""}
        </div>`).join("")
      : "<p class=muted>暂无待摄入内容。</p>";
  } catch (e) {
    $("inbox-list").innerHTML = `<p class=muted>读取失败：${esc(e.message)}</p>`;
  }
}
loadInbox();
