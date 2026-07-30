// Feature switcher + cross-feature summary strip — implements FE-031.
// Zones 1-4 are always scoped to one feature at a time, selected explicitly;
// this strip is the only place cross-feature aggregates are shown.

import { findOpenGates } from "./gates.js";

const el = document.getElementById("feature-switcher");

let selectedFeature = null;
let onChangeCallback = () => {};

export function onFeatureChange(callback) {
  onChangeCallback = callback;
}

export function getSelectedFeature() {
  return selectedFeature;
}

export function renderFeatureSwitcher(allLogEntries) {
  const features = uniqueFeatures(allLogEntries);

  if (selectedFeature === null || !features.includes(selectedFeature)) {
    selectedFeature = features[0] || null;
  }

  const openGateCount = findOpenGates(allLogEntries).length;

  const buttons = features
    .map(
      (f) => `
        <button
          class="feature-switcher__button ${f === selectedFeature ? "feature-switcher__button--active" : ""}"
          data-feature="${escapeHtml(f)}"
        >${escapeHtml(f)}</button>
      `
    )
    .join("");

  const summary =
    features.length > 0
      ? `<span class="totals-panel__label">${features.length} feature${features.length === 1 ? "" : "s"} · ${openGateCount} open gate${openGateCount === 1 ? "" : "s"}</span>`
      : "";

  el.innerHTML = `${buttons}${summary}`;

  el.querySelectorAll("button[data-feature]").forEach((btn) => {
    btn.addEventListener("click", () => {
      selectedFeature = btn.dataset.feature;
      onChangeCallback(selectedFeature);
    });
  });
}

function uniqueFeatures(entries) {
  const seen = new Set();
  const ordered = [];
  for (const e of entries) {
    if (e.feature && !seen.has(e.feature)) {
      seen.add(e.feature);
      ordered.push(e.feature);
    }
  }
  return ordered;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
