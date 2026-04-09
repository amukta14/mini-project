const state = { recommendations: [] };
const resultsContainer = document.getElementById("resultsContainer");
const statusText = document.getElementById("statusText");
const themeSwitch = document.getElementById("themeSwitch");
const searchInput = document.getElementById("searchInput");
const typeFilter = document.getElementById("typeFilter");
const domainFilter = document.getElementById("domainFilter");
const archFilter = document.getElementById("archFilter");
const compareBtn = document.getElementById("compareBtn");
const selected = new Set();
const compareModal = document.getElementById("compareModal");
const compareBody = document.getElementById("compareBody");
const compareCloseBtn = document.getElementById("compareCloseBtn");

function escapeHtml(text) { return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\"/g, "&quot;").replace(/'/g, "&#039;"); }
function loadFromSession() {
  try {
    const raw = sessionStorage.getItem("projectiq:lastRecommendations");
    if (!raw) return [];
    return JSON.parse(raw) || [];
  } catch {
    return [];
  }
}

function recommendationCard(item) {
  const percent = Math.round((item.score || 0) * 100);
  const domainBadge = (Array.isArray(item.domain) ? item.domain : [item.domain]).join(", ");
  const steps = Array.isArray(item.implementation_approach)
    ? item.implementation_approach.map((s) => `<li>${escapeHtml(s)}</li>`).join("")
    : "";
  const stack = Array.isArray(item.tech_stack)
    ? item.tech_stack.map((s) => `<span class="badge">${escapeHtml(s)}</span>`).join("")
    : "";
  const datasetLink = item.dataset && item.dataset.link ? item.dataset.link : "";
  const datasetName = item.dataset && item.dataset.name ? item.dataset.name : "Dataset";
  const archetype = item.archetype ? `<span class="badge">${escapeHtml(item.archetype.replaceAll("_", " "))}</span>` : "";
  const matchedSkills = Array.isArray(item.matched_skills) && item.matched_skills.length
    ? item.matched_skills.map((s) => `<span class="badge doable">${escapeHtml(s)}</span>`).join("")
    : `<span class="muted">No direct skill overlap (semantic match carried this).</span>`;
  const breakdown = item.score_breakdown || {};
  const w = breakdown.weights || { semantic: 0.6, skill: 0.25, feasibility: 0.15 };
  const semantic = Number(breakdown.semantic || 0);
  const skill = Number(breakdown.skill || 0);
  const feas = Number(breakdown.feasibility || 0);
  const weightedTotal = (w.semantic * semantic) + (w.skill * skill) + (w.feasibility * feas);
  const seg = (val) => Math.max(0, Math.min(100, Math.round(val * 100)));
  const segSemantic = seg((w.semantic * semantic) / (weightedTotal || 1));
  const segSkill = seg((w.skill * skill) / (weightedTotal || 1));
  const segFeas = Math.max(0, 100 - segSemantic - segSkill);
  const feasibilityNotes = Array.isArray(item.feasibility_notes) && item.feasibility_notes.length
    ? `<ul class="mini-list">${item.feasibility_notes.map((n) => `<li>${escapeHtml(n)}</li>`).join("")}</ul>`
    : `<div class="muted">No feasibility flags for your profile.</div>`;
  const id = String(item.__rid ?? item.title ?? "");
  const key = escapeHtml(id);
  const checked = selected.has(id) ? "checked" : "";
  return `<article class="card"><h3>${escapeHtml(item.title)}</h3>
    <label class="compare-toggle"><input type="checkbox" data-ck="${key}" data-raw="${escapeHtml(id)}" ${checked} />Compare</label>
    <div class="badges"><span class="badge">${escapeHtml(domainBadge)}</span>${archetype}<span class="badge">${escapeHtml(item.difficulty)}</span><span class="badge ${escapeHtml(item.type)}">${escapeHtml(item.type)}</span></div>
    <small>Match score: ${percent}%</small><div class="progress-bar"><div class="progress-fill" style="width:${percent}%"></div></div>
    <p><strong>Problem:</strong> ${escapeHtml(item.problem_statement || "")}</p>
    <p><strong>Description:</strong> ${escapeHtml(item.project_description || "")}</p>
    <div class="badges">${stack}</div>
    <details class="card-details">
      <summary>Why this matched</summary>
      <div class="subhead">Matched skills</div>
      <div class="badges">${matchedSkills}</div>
      <div class="subhead">Score breakdown</div>
      <div class="scorebar" role="img" aria-label="Score breakdown">
        <span class="seg seg-sem" style="width:${segSemantic}%"></span>
        <span class="seg seg-skill" style="width:${segSkill}%"></span>
        <span class="seg seg-feas" style="width:${segFeas}%"></span>
      </div>
      <div class="mini-grid">
        <div><span class="k">Semantic</span><span class="v">${Math.round(semantic * 100)}%</span></div>
        <div><span class="k">Skills</span><span class="v">${Math.round(skill * 100)}%</span></div>
        <div><span class="k">Feasibility</span><span class="v">${Math.round(feas * 100)}%</span></div>
      </div>
      <div class="subhead">Feasibility notes</div>
      ${feasibilityNotes}
    </details>
    <details class="card-details">
      <summary>View implementation plan</summary>
      <ol>${steps}</ol>
    </details>
    <p>${escapeHtml(item.reason || "")}</p>
    <a class="dataset-link" href="${escapeHtml(datasetLink)}" target="_blank" rel="noopener noreferrer">${escapeHtml(datasetName)}</a></article>`;
}

function renderCompareModal(items) {
  if (!compareBody || !compareModal) return;
  compareBody.innerHTML = items
    .map((item) => {
      const domains = (Array.isArray(item.domain) ? item.domain : [item.domain]).filter(Boolean).join(", ");
      const breakdown = item.score_breakdown || {};
      const semantic = Math.round(Number(breakdown.semantic || 0) * 100);
      const skill = Math.round(Number(breakdown.skill || 0) * 100);
      const feas = Math.round(Number(breakdown.feasibility || 0) * 100);
      const matchedSkills = Array.isArray(item.matched_skills) && item.matched_skills.length
        ? item.matched_skills.map((s) => `<span class="badge doable">${escapeHtml(s)}</span>`).join("")
        : `<span class="muted">No direct overlap</span>`;
      const notes = Array.isArray(item.feasibility_notes) && item.feasibility_notes.length
        ? `<ul class="mini-list">${item.feasibility_notes.map((n) => `<li>${escapeHtml(n)}</li>`).join("")}</ul>`
        : `<div class="muted">No feasibility flags</div>`;
      return `<section class="compare-col">
        <div class="compare-top">
          <div class="compare-h">${escapeHtml(item.title || "Project")}</div>
          <div class="badges">
            <span class="badge">${escapeHtml(domains || "")}</span>
            ${item.archetype ? `<span class="badge">${escapeHtml(String(item.archetype).replaceAll("_", " "))}</span>` : ""}
            <span class="badge ${escapeHtml(item.type || "")}">${escapeHtml(item.type || "")}</span>
          </div>
        </div>
        <div class="compare-block">
          <div class="subhead">Problem</div>
          <div class="muted">${escapeHtml(item.problem_statement || "")}</div>
        </div>
        <div class="compare-block">
          <div class="subhead">Score breakdown</div>
          <div class="mini-grid">
            <div><span class="k">Semantic</span><span class="v">${semantic}%</span></div>
            <div><span class="k">Skills</span><span class="v">${skill}%</span></div>
            <div><span class="k">Feasibility</span><span class="v">${feas}%</span></div>
          </div>
        </div>
        <div class="compare-block">
          <div class="subhead">Matched skills</div>
          <div class="badges">${matchedSkills}</div>
        </div>
        <div class="compare-block">
          <div class="subhead">Feasibility notes</div>
          ${notes}
        </div>
      </section>`;
    })
    .join("");
}

function openCompare() {
  if (!compareModal) return;
  const ids = Array.from(selected);
  const items = ids
    .map((id) => state.recommendations.find((x) => String(x.__rid) === String(id)))
    .filter(Boolean);
  if (items.length < 2) return;
  renderCompareModal(items);
  compareModal.hidden = false;
  document.body.style.overflow = "hidden";
}

function closeCompare() {
  if (!compareModal) return;
  compareModal.hidden = true;
  document.body.style.overflow = "";
}

function normText(item) {
  return [
    item.title,
    item.problem_statement,
    item.project_description,
    Array.isArray(item.domain) ? item.domain.join(" ") : item.domain,
    item.archetype,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

function applyFilters(items) {
  const q = (searchInput?.value || "").trim().toLowerCase();
  const t = typeFilter?.value || "";
  const d = domainFilter?.value || "";
  const a = archFilter?.value || "";

  return items.filter((item) => {
    if (t && item.type !== t) return false;
    if (d) {
      const domains = Array.isArray(item.domain) ? item.domain : [item.domain];
      if (!domains.includes(d)) return false;
    }
    if (a && item.archetype !== a) return false;
    if (q && !normText(item).includes(q)) return false;
    return true;
  });
}

function renderRecommendations(items) {
  const filtered = applyFilters(items);
  resultsContainer.innerHTML = filtered.length ? filtered.map(recommendationCard).join("") : "<p>No recommendations found.</p>";
  if (statusText && items.length) statusText.textContent = `${filtered.length}/${items.length} shown`;
  wireCompareToggles();
}

// initial load from prior questionnaire submission
(function init() {
  const items = loadFromSession();
  if (!items.length) {
    statusText.textContent = "Fill the questionnaire to generate project ideas.";
    resultsContainer.innerHTML = '<p>No recommendations cached. <a href="/questionnaire">Go to questionnaire</a>.</p>';
    return;
  }
  state.recommendations = items;
  // Stable client-side IDs for compare selection
  state.recommendations.forEach((it, idx) => {
    if (!it.__rid) it.__rid = `rec_${idx}_${String(it.title || "project").slice(0, 24)}`;
  });
  // Populate filter dropdowns
  const domains = new Set();
  const archetypes = new Set();
  items.forEach((it) => {
    const ds = Array.isArray(it.domain) ? it.domain : [it.domain];
    ds.filter(Boolean).forEach((x) => domains.add(x));
    if (it.archetype) archetypes.add(it.archetype);
  });
  if (domainFilter) {
    Array.from(domains).sort().forEach((x) => {
      const opt = document.createElement("option");
      opt.value = x;
      opt.textContent = x;
      domainFilter.appendChild(opt);
    });
  }
  if (archFilter) {
    Array.from(archetypes).sort().forEach((x) => {
      const opt = document.createElement("option");
      opt.value = x;
      opt.textContent = String(x).replaceAll("_", " ");
      archFilter.appendChild(opt);
    });
  }
  renderRecommendations(state.recommendations);
  statusText.textContent = `${state.recommendations.length} recommendations generated`;
})();

const savedTheme = localStorage.getItem("theme");
if (savedTheme === "dark") { document.body.classList.add("dark"); themeSwitch.checked = true; }
themeSwitch.addEventListener("change", (event) => {
  document.body.classList.toggle("dark", event.target.checked);
  localStorage.setItem("theme", event.target.checked ? "dark" : "light");
});

function wireCompareToggles() {
  document.querySelectorAll('input[type="checkbox"][data-ck]').forEach((el) => {
    el.addEventListener("change", (e) => {
      const raw = e.target.getAttribute("data-raw");
      if (!raw) return;
      if (e.target.checked) selected.add(raw);
      else selected.delete(raw);
      if (compareBtn) {
        compareBtn.textContent = `Compare (${selected.size})`;
        compareBtn.disabled = selected.size < 2;
      }
    });
  });
  if (compareBtn) {
    compareBtn.textContent = `Compare (${selected.size})`;
    compareBtn.disabled = selected.size < 2;
  }
}

[searchInput, typeFilter, domainFilter, archFilter].forEach((el) => {
  if (!el) return;
  el.addEventListener("input", () => renderRecommendations(state.recommendations));
  el.addEventListener("change", () => renderRecommendations(state.recommendations));
});

if (compareBtn) compareBtn.addEventListener("click", openCompare);
if (compareCloseBtn) compareCloseBtn.addEventListener("click", closeCompare);
if (compareModal) {
  compareModal.addEventListener("click", (e) => {
    if (e.target && e.target.getAttribute && e.target.getAttribute("data-close") === "1") closeCompare();
  });
}
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeCompare();
});
