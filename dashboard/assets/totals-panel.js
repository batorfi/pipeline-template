// Zone 4b: totals panel — implements FE-030.
// Real per-pane token usage, aggregated across currently-open panes.
// Cost tracking (dollar spend) was never real: factory-log.md's usage
// blocks are always logged as a 0.0 placeholder, since cmux exposes no
// cost/pricing data of any kind. Token counts ARE real, read from each
// open pane's own local Claude Code session transcript (see /panes,
// token_usage_reader.py) — but only for panes currently open; a pane
// that's already closed leaves no trace here, so this is a live snapshot,
// not a full-feature historical total.

const el = document.getElementById("totals-panel");

export function renderTotalsPanel(panes) {
  const withTokens = (panes || []).filter((p) => p.tokens && p.tokens.available);

  if (withTokens.length === 0) {
    el.innerHTML = `<div class="empty-state">No live token data yet — no Claude Code panes currently open.</div>`;
    return;
  }

  const totals = withTokens.reduce(
    (acc, p) => ({
      total: acc.total + p.tokens.total_tokens,
      input: acc.input + p.tokens.input_tokens,
      output: acc.output + p.tokens.output_tokens,
    }),
    { total: 0, input: 0, output: 0 }
  );

  el.innerHTML = `
    <h2 class="section-heading">Live Token Usage</h2>
    <div class="totals-panel__grid">
      <div class="totals-panel__figure-block">
        <div class="totals-panel__figure">${formatTokenCount(totals.total)}</div>
        <div class="totals-panel__label">Total tokens · ${withTokens.length} active pane${withTokens.length === 1 ? "" : "s"}</div>
      </div>
      <div class="totals-panel__figure-block">
        <div class="totals-panel__figure">${formatTokenCount(totals.input)}</div>
        <div class="totals-panel__label">Input tokens</div>
      </div>
      <div class="totals-panel__figure-block">
        <div class="totals-panel__figure">${formatTokenCount(totals.output)}</div>
        <div class="totals-panel__label">Output tokens</div>
      </div>
    </div>
    <p class="totals-panel__note">Live snapshot of currently-open panes only — not a full-feature historical total. Closed panes aren't tracked yet.</p>
  `;
}

function formatTokenCount(n) {
  if (typeof n !== "number") return "0";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(n);
}
