(() => {
    "use strict";

    // ── State ────────────────────────────────────────────────────────
    let allSymptoms = [];
    let selectedSymptoms = [];
    let petType = "dog";
    let acIndex = -1; // autocomplete highlight index

    // ── DOM refs ─────────────────────────────────────────────────────
    const $ = (s) => document.querySelector(s);
    const input = $("#symptom-input");
    const chipsEl = $("#selected-chips");
    const dropdown = $("#autocomplete-dropdown");
    const diagnoseBtn = $("#diagnose-btn");
    const resultsSection = $("#results-section");
    const resultsGrid = $("#results-grid");
    const btnDog = $("#btn-dog");
    const btnCat = $("#btn-cat");
    const hintEl = $("#symptom-hint");

    // ── Init ─────────────────────────────────────────────────────────
    async function init() {
        try {
            const res = await fetch("/symptoms");
            const data = await res.json();
            allSymptoms = data.symptoms || [];
        } catch (e) {
            console.error("Failed to load symptoms", e);
        }

        // Pet toggle
        btnDog.addEventListener("click", () => setPet("dog"));
        btnCat.addEventListener("click", () => setPet("cat"));

        // Input events
        input.addEventListener("input", onInput);
        input.addEventListener("keydown", onKeydown);
        input.addEventListener("focus", onInput);

        // Click on wrapper focuses input
        $("#symptom-input-wrapper").addEventListener("click", () => input.focus());

        // Close dropdown on outside click
        document.addEventListener("click", (e) => {
            if (!e.target.closest("#symptom-input-wrapper")) closeDropdown();
        });

        // Diagnose
        diagnoseBtn.addEventListener("click", diagnose);
    }

    // ── Pet type ─────────────────────────────────────────────────────
    function setPet(type) {
        petType = type;
        btnDog.classList.toggle("active", type === "dog");
        btnCat.classList.toggle("active", type === "cat");
    }

    // ── Chips ────────────────────────────────────────────────────────
    function renderChips() {
        chipsEl.innerHTML = selectedSymptoms
            .map(
                (s) =>
                    `<span class="chip">${formatSymptom(s)}<span class="chip-x" data-sym="${s}">&times;</span></span>`
            )
            .join("");

        // Remove handlers
        chipsEl.querySelectorAll(".chip-x").forEach((el) =>
            el.addEventListener("click", (e) => {
                e.stopPropagation();
                removeSymptom(el.dataset.sym);
            })
        );

        diagnoseBtn.disabled = selectedSymptoms.length === 0;
        hintEl.textContent =
            selectedSymptoms.length === 0
                ? "Select at least one symptom to get a diagnosis"
                : `${selectedSymptoms.length} symptom${selectedSymptoms.length > 1 ? "s" : ""} selected`;
    }

    function addSymptom(sym) {
        if (!selectedSymptoms.includes(sym)) {
            selectedSymptoms.push(sym);
            renderChips();
        }
        input.value = "";
        closeDropdown();
        input.focus();
    }

    function removeSymptom(sym) {
        selectedSymptoms = selectedSymptoms.filter((s) => s !== sym);
        renderChips();
    }

    // ── Autocomplete ─────────────────────────────────────────────────
    function onInput() {
        const q = input.value.trim().toLowerCase();
        const filtered = allSymptoms.filter(
            (s) => s.includes(q) && !selectedSymptoms.includes(s)
        );

        if (filtered.length === 0 || q.length === 0) {
            // Still show all if focused and empty
            if (document.activeElement === input && q.length === 0) {
                showDropdown(allSymptoms.filter((s) => !selectedSymptoms.includes(s)).slice(0,12), "");
            } else {
                closeDropdown();
            }
            return;
        }
        showDropdown(filtered.slice(0, 12), q);
    }

    function showDropdown(items, query) {
        if (items.length === 0) { closeDropdown(); return; }
        acIndex = -1;
        dropdown.innerHTML = items
            .map((s, i) => {
                const label = formatSymptom(s);
                const highlighted = query
                    ? label.replace(new RegExp(`(${escReg(query)})`, "gi"), "<mark>$1</mark>")
                    : label;
                return `<div class="ac-item" data-index="${i}" data-sym="${s}">${highlighted}</div>`;
            })
            .join("");
        dropdown.classList.add("open");

        dropdown.querySelectorAll(".ac-item").forEach((el) => {
            el.addEventListener("click", () => addSymptom(el.dataset.sym));
        });
    }

    function closeDropdown() {
        dropdown.classList.remove("open");
        acIndex = -1;
    }

    function onKeydown(e) {
        const items = dropdown.querySelectorAll(".ac-item");
        if (e.key === "ArrowDown") {
            e.preventDefault();
            acIndex = Math.min(acIndex + 1, items.length - 1);
            highlightItem(items);
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            acIndex = Math.max(acIndex - 1, 0);
            highlightItem(items);
        } else if (e.key === "Enter") {
            e.preventDefault();
            if (acIndex >= 0 && items[acIndex]) {
                addSymptom(items[acIndex].dataset.sym);
            }
        } else if (e.key === "Backspace" && input.value === "" && selectedSymptoms.length) {
            removeSymptom(selectedSymptoms[selectedSymptoms.length - 1]);
        }
    }

    function highlightItem(items) {
        items.forEach((el, i) => el.classList.toggle("active", i === acIndex));
        if (items[acIndex]) items[acIndex].scrollIntoView({ block: "nearest" });
    }

    // ── Diagnose ─────────────────────────────────────────────────────
    async function diagnose() {
        if (selectedSymptoms.length === 0) return;

        diagnoseBtn.classList.add("loading");
        diagnoseBtn.disabled = true;
        resultsSection.classList.add("hidden");

        try {
            const res = await fetch("/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ pet_type: petType, symptoms: selectedSymptoms }),
            });
            const data = await res.json();
            renderResults(data.predictions);
        } catch (err) {
            console.error(err);
            resultsGrid.innerHTML = `<p style="color:var(--danger);text-align:center">Something went wrong. Please try again.</p>`;
            resultsSection.classList.remove("hidden");
        } finally {
            diagnoseBtn.classList.remove("loading");
            diagnoseBtn.disabled = selectedSymptoms.length === 0;
        }
    }

    function renderResults(predictions) {
        const labels = ["Most Likely", "2nd Possible", "3rd Possible"];
        resultsGrid.innerHTML = predictions
            .map(
                (p, i) => `
            <div class="result-card ${p.emergency ? 'emergency-card' : ''}">
                <div class="result-header">
                    <span class="result-rank">${labels[i] || ""}</span>
                    <span class="result-confidence">${p.confidence}%</span>
                </div>
                <div class="result-disease">
                    ${p.disease}
                    ${p.emergency ? '<span class="emergency-badge">🚨 EMERGENCY</span>' : ''}
                </div>
                <p class="result-desc">${p.description}</p>
                <div class="result-remedies">
                    <strong>Recommended Action:</strong> ${p.remedies}
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: 0%;" data-w="${p.confidence}"></div>
                </div>
            </div>`
            )
            .join("");

        resultsSection.classList.remove("hidden");

        // Animate confidence bars
        requestAnimationFrame(() => {
            resultsGrid.querySelectorAll(".confidence-fill").forEach((el) => {
                el.style.width = el.dataset.w + "%";
            });
        });

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // ── Helpers ───────────────────────────────────────────────────────
    function formatSymptom(s) {
        return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
    }
    function escReg(s) {
        return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

    // ── Boot ─────────────────────────────────────────────────────────
    init();
})();
