// Zone 1: attention band — implements FE-002, FE-003.
// Exactly one of: idle state, or gate-open state naming the gate, the
// feature, the exact move set, and a link to the artifact.

import { GATE_STAGES, findOpenGates } from "./gates.js";

const el = document.getElementById("attention-band");
const textEl = el.querySelector(".attention-band__text");

export function renderAttentionBand({ logEntries, panesAvailable, panes }) {
  const openGates = findOpenGates(logEntries || []);

  if (openGates.length > 0) {
    renderGateOpen(openGates);
    return;
  }

  renderIdle({ panesAvailable, panes });
}

function renderGateOpen(openGates) {
  const gate = openGates[0];
  const meta = GATE_STAGES[gate.stage];

  el.classList.remove("attention-band--idle");
  el.classList.add("attention-band--gate-open");

  const otherCount = openGates.length - 1;
  const otherLine =
    otherCount > 0
      ? `<div class="attention-band__other-gates">+${otherCount} other gate${otherCount === 1 ? "" : "s"} also waiting</div>`
      : "";

  // Best-effort artifact link: the API does not yet return an explicit
  // artifact path per gate entry, so this constructs a plausible relative
  // path by convention (specs/<feature>/). If a real deployment's artifact
  // layout differs, this link target needs adjusting — flagged in NOTES.md.
  const artifactHref = `specs/${encodeURIComponent(gate.feature || "")}/`;

  textEl.innerHTML = `
    <strong>${meta ? meta.label : gate.stage}</strong> open on
    <span class="data-mono">${escapeHtml(gate.feature || "")}</span>
    — moves: ${meta ? meta.moves.join(" / ") : "unknown"}
    <a class="attention-band__link" href="${artifactHref}">Read the artifact</a>
    ${otherLine}
  `;
}

function renderIdle({ panesAvailable, panes }) {
  el.classList.remove("attention-band--gate-open");
  el.classList.add("attention-band--idle");

  if (panesAvailable === false) {
    textEl.textContent = "Nothing needs you — pane status is temporarily unavailable.";
    return;
  }

  const running = (panes || []).find((p) => p.status === "running");
  if (running) {
    const role = running.role || "a pane";
    const task = running.current_task || "its current task";
    textEl.textContent = `Nothing needs you — ${role} is working on ${task}.`;
  } else {
    textEl.textContent = "Nothing needs you.";
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
