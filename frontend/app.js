const API = "http://localhost:8000";

// ── State ──────────────────────────────────────────────
const compareList = [];       // [{program data}]
const programStore = {};      // id → program data, avoids inline JSON in onclick
const uniStore = {};

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
async function loadUniversities() {
  const province = document.getElementById("uni-province").value;
  const url = province ? `${API}/universities/?province=${encodeURIComponent(province)}` : `${API}/universities/`;
  const grid = document.getElementById("uni-grid");
  grid.innerHTML = `<div class="loading">Loading…</div>`;
  try {
    const data = await fetch(url).then(r => r.json());
    if (!data.length) { grid.innerHTML = `<div class="empty">No universities found.</div>`; return; }
    data.forEach(u => { uniStore[u.id] = u; });
    grid.innerHTML = data.map(u => `
      <div class="card" data-uni-id="${u.id}">
        <div class="card-header">
          <h3>${u.name}</h3>
          <span class="badge">#${u.rankings.macleans} Maclean's</span>
        </div>
        <div class="card-meta">
          <div class="meta-row"><span class="meta-label">City</span><span class="meta-value">${u.city}, ${u.province}</span></div>
          <div class="meta-row"><span class="meta-label">QS World</span><span class="meta-value">${rank(u.rankings.qs_world)}</span></div>
          <div class="meta-row"><span class="meta-label">Acceptance Rate</span><span class="meta-value">${pct(u.admissions.acceptance_rate)}</span></div>
          <div class="meta-row"><span class="meta-label">Domestic Tuition</span><span class="meta-value">${cad(u.tuition_cad.domestic_min)} – ${cad(u.tuition_cad.domestic_max)}</span></div>
          <div class="meta-row"><span class="meta-label">Intl Tuition</span><span class="meta-value">${cad(u.tuition_cad.international_min)} – ${cad(u.tuition_cad.international_max)}</span></div>
        </div>
      </div>
    `).join("");
    grid.querySelectorAll(".card").forEach(card => {
      card.addEventListener("click", () => showUniDetail(uniStore[card.dataset.uniId]));
    });
  } catch {
    grid.innerHTML = `<div class="empty">Could not connect to API. Is the backend running?</div>`;
  }
}

function showUniDetail(u) {
  showModal(`
    <h2>${u.name}</h2>
    <div class="modal-section">
      <h4>Location &amp; Info</h4>
      <div class="modal-grid">
        <div class="modal-kv"><span>City: </span><span>${u.city}, ${u.province}</span></div>
        <div class="modal-kv"><span>Founded: </span><span>${u.established_year}</span></div>
        <div class="modal-kv"><span>Website: </span><span><a class="ext-link" href="${u.website}" target="_blank">Visit site ↗</a></span></div>
      </div>
    </div>
    <div class="modal-section">
      <h4>Rankings</h4>
      <div class="modal-grid">
        <div class="modal-kv"><span>Maclean's: </span><span>${rank(u.rankings.macleans)}</span></div>
        <div class="modal-kv"><span>QS World: </span><span>${rank(u.rankings.qs_world)}</span></div>
        <div class="modal-kv"><span>QS Canada: </span><span>${rank(u.rankings.qs_canada)}</span></div>
        <div class="modal-kv"><span>Times World: </span><span>${rank(u.rankings.times_world)}</span></div>
      </div>
    </div>
    <div class="modal-section">
      <h4>Admissions</h4>
      <div class="modal-grid">
        <div class="modal-kv"><span>Acceptance Rate: </span><span>${pct(u.admissions.acceptance_rate)}</span></div>
        <div class="modal-kv"><span>Intl Acceptance: </span><span>${pct(u.admissions.international_acceptance_rate)}</span></div>
      </div>
    </div>
    <div class="modal-section">
      <h4>Annual Tuition (CAD)</h4>
      <div class="modal-grid">
        <div class="modal-kv"><span>Domestic: </span><span>${cad(u.tuition_cad.domestic_min)} – ${cad(u.tuition_cad.domestic_max)}</span></div>
        <div class="modal-kv"><span>International: </span><span>${cad(u.tuition_cad.international_min)} – ${cad(u.tuition_cad.international_max)}</span></div>
      </div>
    </div>
  `);
}

document.getElementById("uni-province").addEventListener("change", loadUniversities);

// ── Programs ───────────────────────────────────────────
async function loadPrograms() {
  const field    = document.getElementById("prog-field").value.trim();
  const degree   = document.getElementById("prog-degree").value;
  const tuition  = document.getElementById("prog-tuition").value;
  const sortBy   = document.getElementById("prog-sort").value;

  const params = new URLSearchParams({ sort_by: sortBy, max_domestic_tuition: tuition });
  if (field)  params.set("field", field);
  if (degree) params.set("degree_type", degree);

  const grid = document.getElementById("prog-grid");
  grid.innerHTML = `<div class="loading">Loading…</div>`;
  try {
    const data = await fetch(`${API}/programs/?${params}`).then(r => r.json());
    if (!data.length) { grid.innerHTML = `<div class="empty">No programs found.</div>`; return; }

    // Populate uni filter for courses tab on first load
    const uniSel = document.getElementById("course-uni");
    if (uniSel.options.length === 1) {
      const unis = [...new Map(data.map(p => [p.university_id, p])).values()];
      unis.forEach(p => {
        const o = document.createElement("option");
        o.value = p.university_id; o.text = p.university_short;
        uniSel.add(o);
      });
    }

    data.forEach(p => { programStore[p.id] = p; });
    grid.innerHTML = data.map(p => {
      const inCompare = compareList.some(c => c.id === p.id);
      return `
        <div class="card" data-prog-id="${p.id}">
          <div class="card-header">
            <h3>${p.name}</h3>
            ${p.rankings.national ? `<span class="badge">#${p.rankings.national} CA</span>` : ""}
          </div>
          <div class="card-meta">
            <div class="meta-row"><span class="meta-label">University</span><span class="meta-value">${p.university_short}</span></div>
            <div class="meta-row"><span class="meta-label">Faculty</span><span class="meta-value">${p.faculty || "—"}</span></div>
            <div class="meta-row"><span class="meta-label">Acceptance Rate</span><span class="meta-value">${pct(p.admissions.acceptance_rate)}</span></div>
            <div class="meta-row"><span class="meta-label">Admission Avg</span><span class="meta-value">${p.admissions.typical_admission_average ? p.admissions.typical_admission_average + "%" : "—"}</span></div>
            <div class="meta-row"><span class="meta-label">Domestic Tuition</span><span class="meta-value">${cad(p.tuition_cad.domestic)}/yr</span></div>
            <div class="meta-row"><span class="meta-label">Intl Tuition</span><span class="meta-value">${cad(p.tuition_cad.international)}/yr</span></div>
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
    // Attach events after render
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
  } catch (e) {
    grid.innerHTML = `<div class="empty">Could not connect to API. Is the backend running?</div>`;
  }
}

function showProgDetail(p) {
  showModal(`
    <h2>${p.name}</h2>
    <p style="color:var(--muted);font-size:.85rem;margin-bottom:1rem">${p.university_name} · ${p.faculty || ""}</p>
    <div class="modal-section">
      <h4>Admissions</h4>
      <div class="modal-grid">
        <div class="modal-kv"><span>Acceptance Rate: </span><span>${pct(p.admissions.acceptance_rate)}</span></div>
        <div class="modal-kv"><span>Min Average: </span><span>${p.admissions.min_admission_average ? p.admissions.min_admission_average + "%" : "—"}</span></div>
        <div class="modal-kv"><span>Typical Average: </span><span>${p.admissions.typical_admission_average ? p.admissions.typical_admission_average + "%" : "—"}</span></div>
      </div>
      ${p.admissions.required_courses ? `<p style="font-size:.82rem;margin-top:.5rem;color:var(--muted)">Required HS courses: ${p.admissions.required_courses}</p>` : ""}
    </div>
    <div class="modal-section">
      <h4>Tuition &amp; Fees (Annual, CAD)</h4>
      <div class="modal-grid">
        <div class="modal-kv"><span>Domestic: </span><span>${cad(p.tuition_cad.domestic)}</span></div>
        <div class="modal-kv"><span>International: </span><span>${cad(p.tuition_cad.international)}</span></div>
        <div class="modal-kv"><span>Ancillary Fees: </span><span>${cad(p.tuition_cad.ancillary_fees)}</span></div>
      </div>
    </div>
    <div class="modal-section">
      <h4>Rankings</h4>
      <div class="modal-grid">
        <div class="modal-kv"><span>National: </span><span>${rank(p.rankings.national)}</span></div>
        <div class="modal-kv"><span>QS Subject: </span><span>${rank(p.rankings.qs_subject)}</span></div>
        ${p.rankings.qs_subject_area ? `<div class="modal-kv" style="grid-column:1/-1"><span>QS Area: </span><span>${p.rankings.qs_subject_area}</span></div>` : ""}
      </div>
    </div>
    ${p.url ? `<a class="ext-link" href="${p.url}" target="_blank">View official program page ↗</a>` : ""}
  `);
}

document.getElementById("prog-search-btn").addEventListener("click", loadPrograms);
document.getElementById("prog-tuition").addEventListener("input", e => {
  document.getElementById("prog-tuition-val").textContent = cad(e.target.value);
});

// ── Courses ────────────────────────────────────────────
async function loadCourses() {
  const search = document.getElementById("course-search").value.trim();
  const uniId  = document.getElementById("course-uni").value;
  const level  = document.getElementById("course-level").value;

  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (uniId)  params.set("university_id", uniId);
  if (level)  params.set("level", level);

  const tbody = document.getElementById("course-tbody");
  tbody.innerHTML = `<tr><td colspan="6" class="loading">Loading…</td></tr>`;
  try {
    const data = await fetch(`${API}/courses/?${params}`).then(r => r.json());
    if (!data.length) {
      tbody.innerHTML = `<tr><td colspan="6" class="empty">No courses found.</td></tr>`;
      return;
    }
    tbody.innerHTML = data.slice(0, 200).map(c => `
      <tr style="cursor:pointer" onclick="loadCourseDetail(${c.id})">
        <td><strong>${c.code || "—"}</strong></td>
        <td>${c.name}</td>
        <td>${c.university_name || "—"}</td>
        <td>${c.level || "—"}</td>
        <td>${c.credits || "—"}</td>
        <td class="prereq-text">${c.prerequisites_text || "—"}</td>
      </tr>
    `).join("");
  } catch {
    tbody.innerHTML = `<tr><td colspan="6" class="empty">Could not connect to API.</td></tr>`;
  }
}

async function loadCourseDetail(id) {
  const c = await fetch(`${API}/courses/${id}`).then(r => r.json());
  showModal(`
    <h2>${c.code ? c.code + " – " : ""}${c.name}</h2>
    <p style="color:var(--muted);font-size:.85rem;margin-bottom:1rem">${c.university_name || ""}</p>
    ${c.description ? `<p style="font-size:.88rem;margin-bottom:1rem">${c.description}</p>` : ""}
    <div class="modal-section">
      <h4>Details</h4>
      <div class="modal-grid">
        <div class="modal-kv"><span>Level: </span><span>${c.level || "—"}</span></div>
        <div class="modal-kv"><span>Credits: </span><span>${c.credits || "—"}</span></div>
        <div class="modal-kv"><span>Semester: </span><span>${c.semester || "—"}</span></div>
      </div>
    </div>
    ${c.prerequisites_text ? `<div class="modal-section"><h4>Prerequisites</h4><p style="font-size:.85rem">${c.prerequisites_text}</p></div>` : ""}
    ${c.corequisites_text  ? `<div class="modal-section"><h4>Corequisites</h4><p style="font-size:.85rem">${c.corequisites_text}</p></div>` : ""}
    ${c.exclusions_text    ? `<div class="modal-section"><h4>Exclusions</h4><p style="font-size:.85rem">${c.exclusions_text}</p></div>` : ""}
    ${(c.prerequisites||[]).length ? `
      <div class="modal-section">
        <h4>Prerequisite Courses</h4>
        ${c.prerequisites.map(p => `<span class="rank-chip">${p.code}</span> `).join("")}
      </div>` : ""}
    ${c.url ? `<a class="ext-link" href="${c.url}" target="_blank">View on university site ↗</a>` : ""}
  `);
}

document.getElementById("course-search-btn").addEventListener("click", loadCourses);
document.getElementById("course-search").addEventListener("keydown", e => { if (e.key === "Enter") loadCourses(); });

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
      <h4>${p.university_short} – ${p.field}</h4>
      <div class="compare-row"><span>Degree</span><span>${p.degree_type}</span></div>
      <div class="compare-row"><span>Acceptance</span><span>${pct(p.admissions.acceptance_rate)}</span></div>
      <div class="compare-row"><span>Typical Avg</span><span>${p.admissions.typical_admission_average ? p.admissions.typical_admission_average + "%" : "—"}</span></div>
      <div class="compare-row"><span>Domestic</span><span>${cad(p.tuition_cad.domestic)}/yr</span></div>
      <div class="compare-row"><span>International</span><span>${cad(p.tuition_cad.international)}/yr</span></div>
      <div class="compare-row"><span>National Rank</span><span>${rank(p.rankings.national)}</span></div>
      <div class="compare-row"><span>QS Subject</span><span>${rank(p.rankings.qs_subject)}</span></div>
    </div>
  `).join("");
}

document.getElementById("clear-compare").addEventListener("click", () => {
  compareList.length = 0;
  renderCompare();
  // Reset all compare buttons
  document.querySelectorAll(".btn-sm.compare-added").forEach(b => {
    b.classList.remove("compare-added");
    b.textContent = "+ Compare";
  });
});

// ── Init ───────────────────────────────────────────────
loadUniversities();
loadPrograms();
