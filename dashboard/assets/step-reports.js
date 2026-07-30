// Zone 3: step-report feed — implements FE-010.
// Collapses consecutive same-stage loop-internal entries (polish rounds,
// checkpoint retries, mitigation rounds) into one expandable group by
// default; everything else renders as its own card, newest first.

const listEl = document.getElementById("step-reports-list");

export function renderStepReports(logEntries) {
  const entries = logEntries || [];
  if (entries.length === 0) {
    listEl.innerHTML = `<div class="empty-state">No activity logged yet.</div>`;
    return;
  }

  const groups = groupConsecutiveByStage(entries);
  listEl.innerHTML = groups.map(renderGroup).join("");
}

function groupConsecutiveByStage(entries) {
  const groups = [];
  for (const entry of entries) {
    const last = groups[groups.length - 1];
    if (last && last.feature === entry.feature && last.stage === entry.stage) {
      last.entries.push(entry);
    } else {
      groups.push({ feature: entry.feature, stage: entry.stage, entries: [entry] });
    }
  }
  return groups;
}

function renderGroup(group) {
  if (group.entries.length === 1) {
    return renderCard(group.entries[0]);
  }
  // Loop-internal group: show the latest as the visible summary, rest
  // collapsed under a <details> the user can expand.
  const [latest, ...rest] = group.entries;
  return `
    <details class="step-reports__loop-group">
      <summary>${escapeHtml(group.stage)} — ${group.entries.length} attempts (latest shown, click to expand all)</summary>
      ${renderCard(latest)}
      ${rest.map(renderCard).join("")}
    </details>
  `;
}

function renderCard(entry) {
  const tierBadge = entry.tier ? `<span class="tier-badge tier-badge--${entry.tier}">${entry.tier}</span>` : "";
  const usage = entry.usage
    ? `<span class="data-mono">$${(entry.usage.estimated_cost_usd ?? 0).toFixed(2)}</span>`
    : "";
  const decision = entry.decision ? `<span class="status-badge status-badge--healthy">${entry.decision}</span>` : "";

  return `
    <div class="card">
      <div class="card__header">
        <span class="card__title">${escapeHtml(entry.stage)}</span>
        <span>${tierBadge} ${usage} ${decision}</span>
      </div>
      <div class="card__body">
        <span class="data-mono">${escapeHtml(entry.feature || "")}</span>
        · <span class="data-mono">${escapeHtml(entry.timestamp || "")}</span>
      </div>
      ${entry.summary ? `<p class="card__summary">${escapeHtml(entry.summary)}</p>` : ""}
    </div>
  `;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
