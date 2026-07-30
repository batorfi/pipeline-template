// Zone 4b: totals panel — implements FE-030.
// Cumulative spend by tier, and the budget_trend early-warning flag,
// visually distinct from the routine figures around it.

const el = document.getElementById("totals-panel");

export function renderTotalsPanel(stats) {
  if (!stats || stats.total_cost === undefined) {
    el.innerHTML = `<div class="empty-state">No cost data yet.</div>`;
    return;
  }

  const tierFigures = Object.entries(stats.cost_by_tier || {})
    .map(
      ([tier, amount]) => `
        <div class="totals-panel__figure-block">
          <span class="tier-badge tier-badge--${tier}">${tier}</span>
          <div class="totals-panel__figure">$${amount.toFixed(2)}</div>
          <div class="totals-panel__label">${(stats.cost_by_tier_pct[tier] ?? 0).toFixed(1)}% of total</div>
        </div>
      `
    )
    .join("");

  const budgetTrend = stats.budget_trend
    ? renderBudgetTrend(stats.budget_trend)
    : "";

  el.innerHTML = `
    <h2 class="section-heading">Totals</h2>
    <div class="totals-panel__grid">
      <div class="totals-panel__figure-block">
        <div class="totals-panel__figure">$${stats.total_cost.toFixed(2)}</div>
        <div class="totals-panel__label">Total spend</div>
      </div>
      ${tierFigures}
    </div>
    ${budgetTrend}
  `;
}

function renderBudgetTrend(trend) {
  const overClass = trend.over_ceiling ? "totals-panel__bar-fill--over" : "";
  const badgeClass = trend.over_ceiling ? "status-badge--attention" : "status-badge--healthy";
  const widthPct = Math.min(100, trend.opus_share_pct);
  return `
    <div class="totals-panel__budget-trend">
      <div class="card__header">
        <span class="card__title">Opus share of spend</span>
        <span class="status-badge ${badgeClass}">${trend.opus_share_pct.toFixed(1)}% / ${trend.ceiling_pct}% ceiling</span>
      </div>
      <div class="totals-panel__bar-track">
        <div class="totals-panel__bar-fill ${overClass}" style="width: ${widthPct}%"></div>
      </div>
    </div>
  `;
}
