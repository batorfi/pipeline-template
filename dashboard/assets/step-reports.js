// Zone 3: step-report feed — implements FE-010.
// Collapses consecutive same-stage loop-internal entries (polish rounds,
// checkpoint retries, mitigation rounds) into one expandable group by
// default; everything else renders as its own card, newest first.

const listEl = document.getElementById("step-reports-list");

// The poll loop re-renders this zone every tick by replacing innerHTML
// wholesale, which would otherwise silently collapse any <details> the user
// had open — the DOM node is destroyed and rebuilt from scratch each time,
// with no memory of its own open/closed state. Track which loop-groups are
// open across re-renders here, keyed by feature+stage (stable across ticks
// since groups form from consecutive same feature+stage entries), and
// re-apply it on every render.
const openGroupKeys = new Set();

export function renderStepReports(logEntries) {
  const entries = logEntries || [];
  if (entries.length === 0) {
    listEl.innerHTML = `<div class="empty-state">No activity logged yet.</div>`;
    return;
  }

  const groups = groupConsecutiveByStage(entries);
  listEl.innerHTML = groups.map(renderGroup).join("");

  for (const details of listEl.querySelectorAll("details.step-reports__loop-group")) {
    details.addEventListener("toggle", () => {
      const key = details.dataset.groupKey;
      if (details.open) {
        openGroupKeys.add(key);
      } else {
        openGroupKeys.delete(key);
      }
    });
  }
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
  const key = `${group.feature}::${group.stage}`;
  const openAttr = openGroupKeys.has(key) ? " open" : "";
  return `
    <details class="step-reports__loop-group" data-group-key="${escapeHtml(key)}"${openAttr}>
      <summary>${escapeHtml(group.stage)} — ${group.entries.length} attempts (latest shown, click to expand all)</summary>
      ${renderCard(latest)}
      ${rest.map(renderCard).join("")}
    </details>
  `;
}

// factory-log.md logs the raw imperative move name (approve/revise/
// reject/restart, per docs/human-gates.md) — displayed here as the past
// tense of what actually happened, since this badge always describes a
// decision already made, not an instruction still pending.
const DECISION_LABELS = {
  approve: "approved",
  revise: "revised",
  reject: "rejected",
  restart: "restarted",
};

const DECISION_BADGE_CLASSES = {
  approve: "status-badge--healthy",
  revise: "status-badge--caution",
  reject: "status-badge--attention",
  restart: "status-badge--attention",
};

function renderCard(entry) {
  const tierBadge = entry.tier ? `<span class="tier-badge tier-badge--${entry.tier}">${entry.tier}</span>` : "";
  // Cost figures removed: factory-log.md's usage.estimated_cost_usd is
  // always logged as a 0.0 placeholder (cmux exposes no pricing data of any
  // kind) — showing it read as "this cost nothing," which isn't true, it's
  // just not measured. See dashboard/assets/totals-panel.js for real token
  // counts instead, which read from actual Claude Code session transcripts.
  const decisionLabel = DECISION_LABELS[entry.decision] || entry.decision;
  const decisionClass = DECISION_BADGE_CLASSES[entry.decision] || "status-badge--healthy";
  const decision = entry.decision ? `<span class="status-badge ${decisionClass}">${escapeHtml(decisionLabel)}</span>` : "";

  return `
    <div class="card">
      <div class="card__header">
        <span class="card__title">${escapeHtml(entry.stage)}</span>
        <span>${tierBadge} ${decision}</span>
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
