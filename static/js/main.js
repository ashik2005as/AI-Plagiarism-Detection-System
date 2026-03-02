/* =========================================================
   AI Plagiarism Detector – Frontend JavaScript
   ========================================================= */

"use strict";

// ---------------------------------------------------------------------------
// Dark mode toggle
// ---------------------------------------------------------------------------
(function () {
  const html = document.documentElement;
  const btn = document.getElementById("themeToggle");
  const icon = document.getElementById("themeIcon");

  const STORAGE_KEY = "plagiarism-theme";
  const saved = localStorage.getItem(STORAGE_KEY);

  if (saved) {
    html.setAttribute("data-theme", saved);
    icon.textContent = saved === "dark" ? "☀️" : "🌙";
  }

  if (btn) {
    btn.addEventListener("click", () => {
      const current = html.getAttribute("data-theme") || "light";
      const next = current === "dark" ? "light" : "dark";
      html.setAttribute("data-theme", next);
      icon.textContent = next === "dark" ? "☀️" : "🌙";
      localStorage.setItem(STORAGE_KEY, next);
    });
  }
})();

// ---------------------------------------------------------------------------
// Tab switching
// ---------------------------------------------------------------------------
(function () {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.tab;

      tabBtns.forEach((b) => b.classList.remove("active"));
      tabContents.forEach((c) => c.classList.remove("active"));

      btn.classList.add("active");
      const content = document.getElementById(target);
      if (content) content.classList.add("active");
    });
  });
})();

// ---------------------------------------------------------------------------
// Character counters
// ---------------------------------------------------------------------------
(function () {
  function attachCounter(textareaId, counterId) {
    const ta = document.getElementById(textareaId);
    const counter = document.getElementById(counterId);
    if (!ta || !counter) return;

    const update = () => {
      counter.textContent = `${ta.value.length.toLocaleString()} characters`;
    };

    ta.addEventListener("input", update);
    update();
  }

  attachCounter("text1", "count1");
  attachCounter("text2", "count2");
})();

// ---------------------------------------------------------------------------
// File drag-and-drop + label update
// ---------------------------------------------------------------------------
(function () {
  function setupDropZone(zoneId, inputId, nameDisplayId) {
    const zone = document.getElementById(zoneId);
    const input = document.getElementById(inputId);
    const nameDisplay = nameDisplayId ? document.getElementById(nameDisplayId) : null;
    if (!zone || !input) return;

    zone.addEventListener("dragover", (e) => {
      e.preventDefault();
      zone.classList.add("drag-over");
    });

    zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));

    zone.addEventListener("drop", (e) => {
      e.preventDefault();
      zone.classList.remove("drag-over");
      const files = e.dataTransfer.files;
      if (files.length) {
        // Use DataTransfer to set files on the input
        try {
          const dt = new DataTransfer();
          Array.from(files).forEach((f) => dt.items.add(f));
          input.files = dt.files;
          input.dispatchEvent(new Event("change"));
        } catch (_) {
          // Safari fallback: just show names
          if (nameDisplay) {
            nameDisplay.textContent = Array.from(files)
              .map((f) => f.name)
              .join(", ");
          }
        }
      }
    });

    // Click on zone triggers file input (except on label / input itself)
    zone.addEventListener("click", (e) => {
      if (e.target !== input && e.target.tagName !== "LABEL") {
        input.click();
      }
    });

    input.addEventListener("change", () => {
      const names = Array.from(input.files).map((f) => f.name);
      if (nameDisplay && names.length) {
        nameDisplay.textContent = names.join(", ");
      }
    });
  }

  setupDropZone("dropZone1", "file1", "fileName1");
  setupDropZone("dropZone2", "file2", "fileName2");

  // Batch zone – shows file list
  const batchZone = document.getElementById("dropZoneBatch");
  const batchInput = document.getElementById("batchFiles");
  const batchList = document.getElementById("batchFileList");

  if (batchZone && batchInput) {
    batchZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      batchZone.classList.add("drag-over");
    });

    batchZone.addEventListener("dragleave", () =>
      batchZone.classList.remove("drag-over")
    );

    batchZone.addEventListener("drop", (e) => {
      e.preventDefault();
      batchZone.classList.remove("drag-over");
      const files = e.dataTransfer.files;
      if (files.length) {
        try {
          const dt = new DataTransfer();
          Array.from(files).forEach((f) => dt.items.add(f));
          batchInput.files = dt.files;
          batchInput.dispatchEvent(new Event("change"));
        } catch (_) {
          updateBatchList(Array.from(files).map((f) => f.name));
        }
      }
    });

    batchZone.addEventListener("click", (e) => {
      if (e.target !== batchInput && e.target.tagName !== "LABEL") {
        batchInput.click();
      }
    });

    batchInput.addEventListener("change", () => {
      updateBatchList(Array.from(batchInput.files).map((f) => f.name));
    });

    function updateBatchList(names) {
      if (!batchList) return;
      batchList.innerHTML = names
        .map((n) => `<li>${escapeHtml(n)}</li>`)
        .join("");
    }
  }
})();

// ---------------------------------------------------------------------------
// Loading spinner – show on form submission
// ---------------------------------------------------------------------------
(function () {
  const overlay = document.getElementById("loadingOverlay");

  function attachLoader(formId) {
    const form = document.getElementById(formId);
    if (!form || !overlay) return;
    form.addEventListener("submit", () => {
      overlay.classList.add("active");
    });
  }

  attachLoader("textForm");
  attachLoader("fileForm");
  attachLoader("batchForm");
})();

// ---------------------------------------------------------------------------
// Download report button
// ---------------------------------------------------------------------------
(function () {
  const btn = document.getElementById("downloadBtn");
  if (!btn) return;

  btn.addEventListener("click", () => {
    // resultData is injected by results.html
    if (typeof resultData === "undefined") return;

    let text = "AI PLAGIARISM DETECTION REPORT\n";
    text += "================================\n\n";
    text += `Date: ${(resultData.timestamp || "").replace("T", " ")} UTC\n\n`;

    if (resultData.mode === "pair") {
      text += `Similarity: ${resultData.similarity_percentage}%\n`;
      text += `Level: ${resultData.plagiarism_level}\n\n`;
      if (resultData.sentence_matches && resultData.sentence_matches.length) {
        text += "TOP SENTENCE MATCHES\n";
        text += "--------------------\n";
        resultData.sentence_matches.forEach((m, i) => {
          text += `\n[${i + 1}] Similarity: ${(m.similarity * 100).toFixed(1)}%\n`;
          text += `  Doc 1: ${m.sentence1}\n`;
          text += `  Doc 2: ${m.sentence2}\n`;
        });
      }
    } else if (resultData.mode === "multi") {
      text += `Documents compared: ${resultData.document_count}\n\n`;
      text += "SIMILARITY MATRIX\n";
      text += "-----------------\n";
      const names = resultData.document_names || [];
      names.forEach((name, i) => {
        text += `${name}:\n`;
        resultData.similarity_matrix[i].forEach((val, j) => {
          text += `  vs ${names[j]}: ${val}%\n`;
        });
        text += "\n";
      });
    }

    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "plagiarism-report.txt";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });
})();

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------
function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
