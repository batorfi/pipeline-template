// Zone 4a: task board — implements FE-020.
// Grouped by user-story phase, per-phase checkpoint status at the phase
// header, overlaid with live pane status for any task currently in flight.

const listEl = document.getElementById("task-board-list");

export function renderTaskBoard({ phases, panes, logEntries }) {
  if (!phases || phases.length === 0) {
    listEl.innerHTML = `<div class="empty-state">No tasks yet — tasks.md hasn't been generated for the current feature.</div>`;
    return;
  }

  listEl.innerHTML = phases.map((phase) => renderPhase(phase, panes || [], logEntries || [])).join("");
}

function renderPhase(phase, panes, logEntries) {
  const checkpointStatus = checkpointStatusFor(phase.phase, logEntries);

  const rows = phase.tasks
    .map((task) => {
      const inFlightPane = panes.find(
        (p) => p.current_task && task.id && p.current_task.includes(task.id)
      );
      const statusCell = task.checked
        ? `<span class="status-badge status-badge--healthy">done</span>`
        : inFlightPane
        ? `<span class="status-badge status-badge--caution">${escapeHtml(inFlightPane.status)}</span>`
        : `<span class="status-badge status-badge--attention">pending</span>`;

      return `
        <tr>
          <td class="data-mono">${escapeHtml(task.id)}</td>
          <td>${task.parallel ? "[P]" : ""}</td>
          <td>${task.story ? escapeHtml(task.story) : ""}</td>
          <td class="data-mono">${escapeHtml(task.file_path || "")}</td>
          <td>${statusCell}</td>
        </tr>
      `;
    })
    .join("");

  return `
    <div class="task-board__phase">
      <div class="task-board__phase-header">
        <span>${escapeHtml(phase.phase)}</span>
        <span class="status-badge ${checkpointStatus.className}">${checkpointStatus.label}</span>
      </div>
      <table class="task-board__table">
        <thead>
          <tr><th>ID</th><th>P</th><th>Story</th><th>File</th><th>Status</th></tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function checkpointStatusFor(phaseLabel, logEntries) {
  const checkpointEntries = logEntries.filter((e) => e.stage === "checkpoint_gate" && e.phase === phaseLabel);
  if (checkpointEntries.length === 0) {
    return { label: "pending", className: "status-badge--attention" };
  }
  const latest = checkpointEntries[0]; // newest-first from /log
  if (latest.decision === "approve") {
    return { label: "passed", className: "status-badge--healthy" };
  }
  if (latest.decision === "revise") {
    return { label: "revised", className: "status-badge--caution" };
  }
  return { label: "pending", className: "status-badge--attention" };
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
