const state = { recommendations: [] };
const form = document.getElementById("recommendationForm");
const resultsContainer = document.getElementById("resultsContainer");
const statusText = document.getElementById("statusText");
const themeSwitch = document.getElementById("themeSwitch");

function escapeHtml(text) { return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\"/g, "&quot;").replace(/'/g, "&#039;"); }
function selectedDomains() { return Array.from(document.getElementById("domains").selectedOptions).map((option) => option.value); }
function selectedCoreSkills() { return Array.from(document.getElementById("core_skills").selectedOptions).map((option) => option.value); }

function parseOtherSkills() {
  const raw = document.getElementById("other_skills").value || "";
  return raw.split(",").map((s) => s.trim()).filter(Boolean);
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
  return `<article class="card"><h3>${escapeHtml(item.title)}</h3>
    <div class="badges"><span class="badge">${escapeHtml(domainBadge)}</span><span class="badge">${escapeHtml(item.difficulty)}</span><span class="badge ${escapeHtml(item.type)}">${escapeHtml(item.type)}</span></div>
    <small>Match score: ${percent}%</small><div class="progress-bar"><div class="progress-fill" style="width:${percent}%"></div></div>
    <p><strong>Problem:</strong> ${escapeHtml(item.problem_statement || "")}</p>
    <p><strong>Description:</strong> ${escapeHtml(item.project_description || "")}</p>
    <div class="badges">${stack}</div>
    <ol>${steps}</ol>
    <p>${escapeHtml(item.reason || "")}</p>
    <a class="dataset-link" href="${escapeHtml(datasetLink)}" target="_blank" rel="noopener noreferrer">${escapeHtml(datasetName)}</a></article>`;
}

function renderRecommendations(items) {
  resultsContainer.innerHTML = items.length ? items.map(recommendationCard).join("") : "<p>No recommendations found.</p>";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  statusText.textContent = "Generating recommendations...";
  const coreSkills = selectedCoreSkills();
  const otherSkills = parseOtherSkills();
  const allSkills = [...coreSkills, ...otherSkills];
  const payload = {
    skills: allSkills,
    core_skills: coreSkills,
    other_skills: otherSkills,
    skill_confidence_level: document.getElementById("skill_confidence_level").value,
    interests: document.getElementById("interests").value,
    experience_level: document.getElementById("experience_level").value,
    time_available: document.getElementById("time_available").value,
    domain_preference: selectedDomains(),
    project_complexity_preference: document.getElementById("project_complexity_preference").value,
    team_or_individual: document.getElementById("team_or_individual").value,
    hardware_availability: document.getElementById("hardware_availability").value,
    preferred_project_type: document.getElementById("preferred_project_type").value,
    dataset_comfort: document.getElementById("dataset_comfort").value,
    learning_vs_execution: document.getElementById("learning_vs_execution").value,
    stretch_willingness: document.getElementById("stretch_willingness").value,
  };
  try {
    const response = await fetch("/recommend", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Request failed");
    state.recommendations = data.recommendations || [];
    renderRecommendations(state.recommendations);
    statusText.textContent = `${state.recommendations.length} recommendations generated`;
  } catch (error) {
    statusText.textContent = "Failed to generate recommendations";
    resultsContainer.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
  }
});

const savedTheme = localStorage.getItem("theme");
if (savedTheme === "dark") { document.body.classList.add("dark"); themeSwitch.checked = true; }
themeSwitch.addEventListener("change", (event) => {
  document.body.classList.toggle("dark", event.target.checked);
  localStorage.setItem("theme", event.target.checked ? "dark" : "light");
});
