// ── Data store (loaded once from static JSON) ──────────
let allUniversities = [];
let allPrograms     = [];
let allCourses      = [];

const uniStore     = {};   // id → university
const programStore = {};   // id → program
const compareList  = [];

async function loadData() {
  [allUniversities, allPrograms, allCourses] = await Promise.all([
    fetch("data/universities.json").then(r => r.json()),
    fetch("data/programs.json").then(r => r.json()),
    fetch("data/courses.json").then(r => r.json()),
  ]);
  allUniversities.forEach(u => { uniStore[u.id] = u; });
  allPrograms.forEach(p => { programStore[p.id] = p; });

  // Attach university name/short_name to programs and courses for display
  allPrograms.forEach(p => {
    const u = uniStore[p.university_id] || {};
    p.university_name  = u.name || "";
    p.university_short = u.short_name || "";
  });
  allCourses.forEach(c => {
    const u = uniStore[c.university_id] || {};
    c.university_name  = u.name || "";
    c.university_short = u.short_name || "";
  });

  populateUniFilter();
  renderUniversities();
  renderPrograms();
}

// ── Tab switching ──────────────────────────────────────
document.querySelectorAll(".tab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(s => s.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
  });
});

// ── Helpers ────────────────────────────────────────────
const pct  = v => v != null ? `${(v * 100).toFixed(0)}%` : "—";
const cad  = v => v != null ? `$${Number(v).toLocaleString("en-CA")}` : "—";
const rank = v => v != null ? `#${v}` : "—";

function showModal(html) {
  document.getElementById("modal-content").innerHTML = html;
  document.getElementById("modal-overlay").classList.remove("hidden");
}
document.getElementById("modal-close").addEventListener("click", () => {
  document.getElementById("modal-overlay").classList.add("hidden");
});
document.getElementById("modal-overlay").addEventListener("click", e => {
  if (e.target === document.getElementById("modal-overlay"))
    document.getElementById("modal-overlay").classList.add("hidden");
});

// ── Universities ───────────────────────────────────────
function renderUniversities() {
  const province = document.getElementById("uni-province").value;
  const grid = document.getElementById("uni-grid");
  let data = allUniversities;
  if (province) data = data.filter(u => u.province === province);
  if (!data.length) { grid.innerHTML = `<div class="empty">No universities found.</div>`; return; }

  grid.innerHTML = data.map(u => `
    <div class="card" data-uni-id="${u.id}">
      <div class="card-header">
        <h3>${u.name}</h3>
        ${u.macleans_rank ? `<span class="badge">#${u.macleans_rank} Maclean's</span>` : ""}
      </div>
      <div class="card-meta">
        <div class="meta-row"><span class="meta-label">City</span><span class="meta-value">${u.city}, ${u.province}</span></div>
        <div class="meta-row"><span class="meta-label">QS World</span><span class="meta-value">${rank(u.qs_world_rank)}</span></div>
        <div class="meta-row"><span class="meta-label">Acceptance Rate</span><span class="meta-value">${pct(u.overall_acceptance_rate)}</span></div>
        <div class="meta-row"><span class="meta-label">Domestic Tuition</span><span class="meta-value">${cad(u.domestic_tuition_min)} – ${cad(u.domestic_tuition_max)}</span></div>
        <div class="meta-row"><span class="meta-label">Intl Tuition</span><span class="meta-value">${cad(u.international_tuition_min)} – ${cad(u.international_tuition_max)}</span></div>
      </div>
    </div>
  `).join("");
  grid.querySelectorAll(".card").forEach(card => {
    card.addEventListener("click", () => showUniDetail(uniStore[card.dataset.uniId]));
  });
}

function showUniDetail(u) {
  const courses = allCourses.filter(c => c.university_id === u.id);
  const programs = allPrograms.filter(p => p.university_id === u.id);

  const courseRows = courses.slice(0, 300).map(c => `
    <tr>
      <td><strong>${c.code || "—"}</strong></td>
      <td>${c.name}</td>
      <td>${c.level || "—"}</td>
      <td>${c.prerequisites_text || "—"}</td>
    </tr>
  `).join("");

  const programCards = programs.map(p => `
    <div style="padding:.5rem 0;border-bottom:1px solid var(--border)">
      <strong>${p.name}</strong>
      <span style="color:var(--muted);font-size:.82rem;margin-left:.5rem">${p.degree_type} · ${p.faculty || ""}</span>
      <div style="font-size:.82rem;margin-top:.25rem;color:var(--muted)">
        Acceptance: ${pct(p.acceptance_rate)} &nbsp;|&nbsp; Domestic: ${cad(p.domestic_tuition)}/yr
      </div>
    </div>
  `).join("");

  showModal(`
    <h2>${u.name}</h2>
    <div class="modal-section">
      <div class="modal-grid">
        <div class="modal-kv"><span>City</span><span>${u.city}, ${u.province}</span></div>
        <div class="modal-kv"><span>Website</span><span><a class="ext-link" href="${u.website}" target="_blank">Visit site ↗</a></span></div>
        <div class="modal-kv"><span>Maclean's</span><span>${rank(u.macleans_rank)}</span></div>
        <div class="modal-kv"><span>QS World</span><span>${rank(u.qs_world_rank)}</span></div>
        <div class="modal-kv"><span>Acceptance Rate</span><span>${pct(u.overall_acceptance_rate)}</span></div>
        <div class="modal-kv"><span>Domestic Tuition</span><span>${cad(u.domestic_tuition_min)} – ${cad(u.domestic_tuition_max)}/yr</span></div>
        <div class="modal-kv"><span>Intl Tuition</span><span>${cad(u.international_tuition_min)} – ${cad(u.international_tuition_max)}/yr</span></div>
      </div>
    </div>

    ${programs.length ? `
    <div class="modal-section">
      <h4>Programs (${programs.length})</h4>
      ${programCards}
    </div>` : ""}

    ${courses.length ? `
    <div class="modal-section">
      <h4>Courses (${courses.length}${courses.length === 300 ? "+" : ""})</h4>
      <div style="overflow-x:auto">
        <table style="width:100%;font-size:.82rem;border-collapse:collapse">
          <thead><tr style="text-align:left;border-bottom:2px solid var(--border)">
            <th style="padding:.4rem .6rem">Code</th>
            <th style="padding:.4rem .6rem">Name</th>
            <th style="padding:.4rem .6rem">Level</th>
            <th style="padding:.4rem .6rem">Prerequisites</th>
          </tr></thead>
          <tbody>${courseRows}</tbody>
        </table>
      </div>
    </div>` : "<p style='color:var(--muted);font-size:.85rem'>No course data scraped yet for this university.</p>"}
  `);
}

document.getElementById("uni-province").addEventListener("change", renderUniversities);

// ── Programs ───────────────────────────────────────────
function renderPrograms() {
  const field   = document.getElementById("prog-field").value.trim().toLowerCase();
  const degree  = document.getElementById("prog-degree").value;

  const sortBy  = document.getElementById("prog-sort").value;
  const grid    = document.getElementById("prog-grid");

  let data = allPrograms;
  if (field) {
    // Expand common shorthand searches to related terms
    const ALIASES = {
      animal: ["animal", "veterinar", "wildlife", "marine", "aquatic", "fisheries", "ocean", "biology"],
      vet:    ["veterinar", "animal", "biomedical", "health science"],
      marine: ["marine", "ocean", "aquatic", "fisheries"],
    };
    const terms = ALIASES[field] || [field];
    data = data.filter(p => {
      const hay = `${p.name} ${p.field || ""} ${p.faculty || ""}`.toLowerCase();
      return terms.some(t => hay.includes(t));
    });
  }
  if (degree) data = data.filter(p => p.degree_type === degree);


  if (sortBy === "acceptance_rate") data.sort((a, b) => (a.acceptance_rate ?? 1) - (b.acceptance_rate ?? 1));
  else if (sortBy === "rank")       data.sort((a, b) => (a.program_rank_national ?? 999) - (b.program_rank_national ?? 999));
  else if (sortBy === "tuition")    data.sort((a, b) => (a.domestic_tuition ?? 0) - (b.domestic_tuition ?? 0));

  if (!data.length) { grid.innerHTML = `<div class="empty">No programs found.</div>`; return; }

  grid.innerHTML = data.map(p => {
    const inCompare = compareList.some(c => c.id === p.id);
    return `
      <div class="card" data-prog-id="${p.id}">
        <div class="card-header">
          <h3>${p.name}</h3>
          ${p.program_rank_national ? `<span class="badge">#${p.program_rank_national} CA</span>` : ""}
        </div>
        <div class="card-meta">
          <div class="meta-row"><span class="meta-label">University</span><span class="meta-value">${p.university_short}</span></div>
          <div class="meta-row"><span class="meta-label">Faculty</span><span class="meta-value">${p.faculty || "—"}</span></div>
          <div class="meta-row"><span class="meta-label">Acceptance Rate</span><span class="meta-value">${pct(p.acceptance_rate)}</span></div>
          <div class="meta-row"><span class="meta-label">Admission Avg</span><span class="meta-value">${p.typical_admission_average ? p.typical_admission_average + "%" : "—"}</span></div>
          <div class="meta-row"><span class="meta-label">Domestic Tuition</span><span class="meta-value">${cad(p.domestic_tuition)}/yr</span></div>
          <div class="meta-row"><span class="meta-label">Intl Tuition</span><span class="meta-value">${cad(p.international_tuition)}/yr</span></div>
        </div>
        <div class="card-actions">
          <button class="btn-sm compare-btn ${inCompare ? "compare-added" : ""}" data-prog-id="${p.id}">
            ${inCompare ? "✓ Comparing" : "+ Compare"}
          </button>
          ${p.url ? `<a class="btn-sm" href="${p.url}" target="_blank">View program ↗</a>` : ""}
        </div>
      </div>
    `;
  }).join("");

  grid.querySelectorAll(".card").forEach(card => {
    card.addEventListener("click", e => {
      if (e.target.closest(".compare-btn") || e.target.closest("a")) return;
      showProgDetail(programStore[card.dataset.progId]);
    });
  });
  grid.querySelectorAll(".compare-btn").forEach(btn => {
    btn.addEventListener("click", e => {
      e.stopPropagation();
      toggleCompare(programStore[btn.dataset.progId], btn);
    });
  });
}

function showProgDetail(p) {
  showModal(`
    <h2>${p.name}</h2>
    <p style="color:var(--muted);font-size:.85rem;margin-bottom:1rem">${p.university_name} · ${p.faculty || ""}</p>
    <div class="modal-section">
      <h4>Admissions</h4>
      <div class="modal-grid">
        <div class="modal-kv"><span>Acceptance Rate</span><span>${pct(p.acceptance_rate)}</span></div>
        <div class="modal-kv"><span>Min Average</span><span>${p.min_admission_average ? p.min_admission_average + "%" : "—"}</span></div>
        <div class="modal-kv"><span>Typical Average</span><span>${p.typical_admission_average ? p.typical_admission_average + "%" : "—"}</span></div>
      </div>
    </div>
    <div class="modal-section">
      <h4>Tuition &amp; Fees (Annual, CAD)</h4>
      <div class="modal-grid">
        <div class="modal-kv"><span>Domestic</span><span>${cad(p.domestic_tuition)}</span></div>
        <div class="modal-kv"><span>International</span><span>${cad(p.international_tuition)}</span></div>
      </div>
    </div>
    <div class="modal-section">
      <h4>Rankings</h4>
      <div class="modal-grid">
        <div class="modal-kv"><span>National</span><span>${rank(p.program_rank_national)}</span></div>
      </div>
    </div>
    ${p.url ? `<a class="ext-link" href="${p.url}" target="_blank">View official program page ↗</a>` : ""}
  `);
}

document.getElementById("prog-search-btn").addEventListener("click", renderPrograms);

// ── Courses ────────────────────────────────────────────
function populateUniFilter() {
  const sel = document.getElementById("course-uni");
  allUniversities.forEach(u => {
    const o = document.createElement("option");
    o.value = u.id; o.text = u.short_name;
    sel.add(o);
  });
}

function renderCourses() {
  const search = document.getElementById("course-search").value.trim().toLowerCase();
  const uniId  = document.getElementById("course-uni").value;
  const level  = document.getElementById("course-level").value;
  const tbody  = document.getElementById("course-tbody");

  if (!search && !uniId && !level) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty">Enter a search term or select a university.</td></tr>`;
    return;
  }

  let data = allCourses;
  if (uniId)  data = data.filter(c => c.university_id == uniId);
  if (level)  data = data.filter(c => c.level == parseInt(level));
  if (search) data = data.filter(c =>
    c.name.toLowerCase().includes(search) ||
    (c.code || "").toLowerCase().includes(search) ||
    (c.description || "").toLowerCase().includes(search)
  );

  if (!data.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty">No courses found.</td></tr>`;
    return;
  }

  tbody.innerHTML = data.slice(0, 200).map(c => `
    <tr style="cursor:pointer" data-course-id="${c.id}">
      <td><strong>${c.code || "—"}</strong></td>
      <td>${c.name}</td>
      <td>${c.university_short || "—"}</td>
      <td>${c.level || "—"}</td>
      <td>${c.credits || "—"}</td>
      <td class="prereq-text">${c.prerequisites_text || "—"}</td>
    </tr>
  `).join("");

  tbody.querySelectorAll("tr").forEach(row => {
    row.addEventListener("click", () => showCourseDetail(allCourses.find(c => c.id == row.dataset.courseId)));
  });
}

function showCourseDetail(c) {
  if (!c) return;
  showModal(`
    <h2>${c.code ? c.code + " – " : ""}${c.name}</h2>
    <p style="color:var(--muted);font-size:.85rem;margin-bottom:1rem">${c.university_name || ""}</p>
    ${c.description ? `<p style="font-size:.88rem;margin-bottom:1rem">${c.description}</p>` : ""}
    <div class="modal-section">
      <h4>Details</h4>
      <div class="modal-grid">
        <div class="modal-kv"><span>Level</span><span>${c.level || "—"}</span></div>
        <div class="modal-kv"><span>Credits</span><span>${c.credits || "—"}</span></div>
      </div>
    </div>
    ${c.prerequisites_text ? `<div class="modal-section"><h4>Prerequisites</h4><p style="font-size:.85rem">${c.prerequisites_text}</p></div>` : ""}
    ${c.url ? `<a class="ext-link" href="${c.url}" target="_blank">View on university site ↗</a>` : ""}
  `);
}

document.getElementById("course-search-btn").addEventListener("click", renderCourses);
document.getElementById("course-search").addEventListener("keydown", e => { if (e.key === "Enter") renderCourses(); });

// ── Compare ────────────────────────────────────────────
function toggleCompare(prog, btn) {
  const idx = compareList.findIndex(c => c.id === prog.id);
  if (idx >= 0) {
    compareList.splice(idx, 1);
    btn.classList.remove("compare-added");
    btn.textContent = "+ Compare";
  } else {
    if (compareList.length >= 4) { alert("Compare up to 4 programs at a time."); return; }
    compareList.push(prog);
    btn.classList.add("compare-added");
    btn.textContent = "✓ Comparing";
  }
  renderCompare();
}

function renderCompare() {
  const grid = document.getElementById("compare-grid");
  const hint = document.querySelector(".hint");
  hint.style.display = compareList.length ? "none" : "block";
  grid.innerHTML = compareList.map(p => `
    <div class="compare-card">
      <h4>${p.university_short} – ${p.field || p.name}</h4>
      <div class="compare-row"><span>Degree</span><span>${p.degree_type}</span></div>
      <div class="compare-row"><span>Acceptance</span><span>${pct(p.acceptance_rate)}</span></div>
      <div class="compare-row"><span>Typical Avg</span><span>${p.typical_admission_average ? p.typical_admission_average + "%" : "—"}</span></div>
      <div class="compare-row"><span>Domestic</span><span>${cad(p.domestic_tuition)}/yr</span></div>
      <div class="compare-row"><span>International</span><span>${cad(p.international_tuition)}/yr</span></div>
      <div class="compare-row"><span>National Rank</span><span>${rank(p.program_rank_national)}</span></div>
    </div>
  `).join("");
}

document.getElementById("clear-compare").addEventListener("click", () => {
  compareList.length = 0;
  renderCompare();
  document.querySelectorAll(".btn-sm.compare-added").forEach(b => {
    b.classList.remove("compare-added");
    b.textContent = "+ Compare";
  });
});

// ── Init ───────────────────────────────────────────────
loadData();
