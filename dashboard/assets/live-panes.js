// Zone 2: what's running right now. Distinct from the attention band's
// "does it need you" — this is "what is actually happening right now."

const listEl = document.getElementById("live-panes-list");

export function renderLivePanes({ panes, panesAvailable }) {
  if (panesAvailable === false) {
    listEl.innerHTML = `<div class="empty-state">Pane status is temporarily unavailable — cmux may not be reachable right now.</div>`;
    return;
  }

  const active = (panes || []).filter((p) => p.status === "running" || p.status === "idle");
  if (active.length === 0) {
    listEl.innerHTML = `<div class="empty-state">No panes currently active.</div>`;
    return;
  }

  listEl.innerHTML = active.map(renderPane).join("");
}

function renderPane(pane) {
  const tierBadge = pane.tier ? `<span class="tier-badge tier-badge--${pane.tier}">${pane.tier}</span>` : "";
  const statusBadgeClass = pane.status === "running" ? "status-badge--healthy" : "status-badge--caution";
  // cmux has no concept of "pipeline role" (researcher/worker/etc.) — role
  // is genuinely unknown, not a display bug. Rather than an alarming
  // "unknown role" label, fall back to the workspace name, which cmux does
  // actually know and which the backend always supplies.
  const title = pane.role || (pane.workspace ? `${pane.workspace} workspace` : "Pane");
  const workspaceLine = pane.role && pane.workspace ? `<span class="data-mono">${escapeHtml(pane.workspace)}</span> · ` : "";
  return `
    <div class="card">
      <div class="card__header">
        <span class="card__title">${escapeHtml(title)}</span>
        <span>${tierBadge} <span class="status-badge ${statusBadgeClass}">${escapeHtml(pane.status)}</span></span>
      </div>
      <div class="card__body">
        ${workspaceLine}${pane.current_task ? escapeHtml(pane.current_task) : ""}
      </div>
    </div>
  `;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
