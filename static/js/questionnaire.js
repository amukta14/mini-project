const qForm = document.getElementById("questionnaireForm");
const overlay = document.getElementById("questionnaireOverlay");
const qThemeSwitch = document.getElementById("themeSwitch");
const qBackBtn = document.getElementById("qBackBtn");
const qNextBtn = document.getElementById("qNextBtn");
const qSubmitBtn = document.getElementById("qSubmitBtn");
const qSteps = Array.from(document.querySelectorAll(".q-step"));
const qStepperDots = Array.from(document.querySelectorAll(".stepper .step"));
let qStepIdx = 0;

// Always reset overlay on page load (handles browser back/forward cache)
if (overlay) {
  overlay.hidden = true;
  overlay.style.display = "none";
}

function qEscape(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function qSelected(selectId) {
  const el = document.getElementById(selectId);
  if (!el) return [];
  if (el.tagName === "SELECT") {
    return Array.from(el.selectedOptions).map((o) => o.value);
  }
  // For custom multi-select: hidden input stores comma-separated values.
  return String(el.value || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

function qParseOtherSkills() {
  const raw = document.getElementById("other_skills").value || "";
  return raw.split(",").map((s) => s.trim()).filter(Boolean);
}

qForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  overlay.hidden = false;
  overlay.style.display = "flex";

  const coreSkills = qSelected("core_skills");
  const otherSkills = qParseOtherSkills();
  const payload = {
    skills: [...coreSkills, ...otherSkills],
    core_skills: coreSkills,
    other_skills: otherSkills,
    skill_confidence_level: document.getElementById("skill_confidence_level").value,
    interests: document.getElementById("interests").value,
    experience_level: document.getElementById("experience_level").value,
    time_available: document.getElementById("time_available").value,
    domain_preference: qSelected("domains"),
    project_complexity_preference: document.getElementById("project_complexity_preference").value,
    team_or_individual: document.getElementById("team_or_individual").value,
    hardware_availability: document.getElementById("hardware_availability").value,
    preferred_project_type: document.getElementById("preferred_project_type").value,
    dataset_comfort: document.getElementById("dataset_comfort").value,
    learning_vs_execution: document.getElementById("learning_vs_execution").value,
    stretch_willingness: document.getElementById("stretch_willingness").value,
  };

  try {
    const response = await fetch("/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Request failed");
    sessionStorage.setItem("projectiq:lastRecommendations", JSON.stringify(data.recommendations || []));
    window.location.href = "/dashboard";
  } catch (err) {
    overlay.hidden = true;
    alert(qEscape(err.message));
  }
});

const savedThemeQ = localStorage.getItem("theme");
if (savedThemeQ === "dark") {
  document.body.classList.add("dark");
  if (qThemeSwitch) qThemeSwitch.checked = true;
}
if (qThemeSwitch) {
  qThemeSwitch.addEventListener("change", (event) => {
    document.body.classList.toggle("dark", event.target.checked);
    localStorage.setItem("theme", event.target.checked ? "dark" : "light");
  });
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = value && String(value).trim() ? value : "—";
}

function renderChips(containerId, items, limit = 8) {
  const el = document.getElementById(containerId);
  if (!el) return;
  const list = Array.isArray(items) ? items : [];
  const trimmed = list.slice(0, limit);
  el.innerHTML = trimmed
    .map((s) => `<span class="chip">${escapeHtml(s)}</span>`)
    .join("");
}

function refreshPreview() {
  const interests = document.getElementById("interests")?.value || "";
  const domains = qSelected("domains");
  const exp = document.getElementById("experience_level")?.value || "";
  const time = document.getElementById("time_available")?.value || "";
  const coreSkills = qSelected("core_skills");
  const otherSkills = qParseOtherSkills();
  const skills = [...coreSkills, ...otherSkills];

  setText("pv_interests", interests);
  setText("pv_domains", domains.join(", "));
  setText("pv_experience", exp ? exp.charAt(0).toUpperCase() + exp.slice(1) : "");
  setText("pv_time", time ? time.charAt(0).toUpperCase() + time.slice(1) : "");
  renderChips("pv_skills", skills);
}

["core_skills", "domains", "interests", "experience_level", "time_available", "other_skills"].forEach((id) => {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener("change", refreshPreview);
  el.addEventListener("input", refreshPreview);
});

refreshPreview();

// Custom multi-select dropdowns (chips + menu)
function msInit(root) {
  const hidden = document.getElementById(root.dataset.ms);
  const trigger = root.querySelector(".ms-trigger");
  const menu = root.querySelector(".ms-menu");
  const chips = root.querySelector(".ms-chips");
  const checkboxes = Array.from(root.querySelectorAll('input[type="checkbox"]'));

  function getSelected() {
    return checkboxes.filter((c) => c.checked).map((c) => c.value);
  }

  function syncHidden() {
    if (!hidden) return;
    hidden.value = getSelected().join(", ");
  }

  function render() {
    const items = getSelected();
    trigger.textContent = items.length ? `${items.length} selected` : "Select options";
    chips.innerHTML = items
      .slice(0, 10)
      .map((s) => `<span class="chip">${escapeHtml(s)}<button type="button" data-x="${escapeHtml(s)}" aria-label="Remove">×</button></span>`)
      .join("");
    syncHidden();
    refreshPreview();
  }

  trigger.addEventListener("click", () => {
    const isOpen = !menu.hidden;
    menu.hidden = isOpen;
    root.classList.toggle("open", !isOpen);
  });

  root.addEventListener("change", (e) => {
    if (e.target && e.target.matches('input[type="checkbox"]')) render();
  });

  chips.addEventListener("click", (e) => {
    const btn = e.target && e.target.closest("button[data-x]");
    if (!btn) return;
    const value = btn.getAttribute("data-x");
    const cb = checkboxes.find((c) => c.value === value);
    if (cb) cb.checked = false;
    render();
  });

  document.addEventListener("click", (e) => {
    if (!root.contains(e.target)) {
      menu.hidden = true;
      root.classList.remove("open");
    }
  });

  // Initial fill from hidden value (if any)
  const initial = String(hidden?.value || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  if (initial.length) {
    checkboxes.forEach((c) => (c.checked = initial.includes(c.value)));
  }
  render();
}

document.querySelectorAll(".ms[data-ms]").forEach((root) => msInit(root));

function qSetStep(idx) {
  qStepIdx = Math.max(0, Math.min(idx, qSteps.length - 1));
  qSteps.forEach((s, i) => {
    s.hidden = i !== qStepIdx;
  });
  qStepperDots.forEach((d, i) => {
    d.classList.toggle("active", i === qStepIdx);
  });

  const isFirst = qStepIdx === 0;
  const isLast = qStepIdx === qSteps.length - 1;
  if (qBackBtn) qBackBtn.disabled = isFirst;
  if (qNextBtn) qNextBtn.hidden = isLast;
  if (qSubmitBtn) qSubmitBtn.hidden = !isLast;
  qValidateStep();
  // Keep the scroll position consistent between steps
  document.querySelector(".form-panel")?.scrollTo({ top: 0, behavior: "smooth" });
}

function qValidateStep() {
  if (!qNextBtn) return true;
  let ok = true;

  if (qStepIdx === 0) {
    // Require at least one skill
    ok = qSelected("core_skills").length + qParseOtherSkills().length > 0;
  } else if (qStepIdx === 1) {
    // Require interest or at least one domain
    const interests = String(document.getElementById("interests")?.value || "").trim();
    ok = interests.length >= 3 || qSelected("domains").length > 0;
  } else if (qStepIdx === 2) {
    // Require feasibility essentials
    const exp = String(document.getElementById("experience_level")?.value || "").trim();
    const time = String(document.getElementById("time_available")?.value || "").trim();
    ok = Boolean(exp && time);
  }

  qNextBtn.disabled = !ok;
  if (qSubmitBtn) qSubmitBtn.disabled = !ok;
  return ok;
}

function qWireValidation() {
  const ids = [
    "core_skills",
    "other_skills",
    "skill_confidence_level",
    "interests",
    "domains",
    "experience_level",
    "time_available",
  ];
  ids.forEach((id) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("change", qValidateStep);
    el.addEventListener("input", qValidateStep);
  });
}

if (qBackBtn) qBackBtn.addEventListener("click", () => qSetStep(qStepIdx - 1));
if (qNextBtn)
  qNextBtn.addEventListener("click", () => {
    if (!qValidateStep()) return;
    qSetStep(qStepIdx + 1);
  });

qWireValidation();
qSetStep(0);

