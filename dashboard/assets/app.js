// Main orchestrator — polling loop, per the runtime stack concept's decision
// (polling, not SSE/WebSockets). Wires the API layer to each zone's render
// function and to the feature switcher's selection state.

import { api } from "./api.js";
import { renderAttentionBand } from "./attention-band.js";
import { renderStepReports } from "./step-reports.js";
import { renderTaskBoard } from "./task-board.js";
import { renderTotalsPanel } from "./totals-panel.js";
import { renderFeatureSwitcher, onFeatureChange, getSelectedFeature } from "./feature-switcher.js";

const POLL_INTERVAL_MS = 4000;

onFeatureChange(() => {
  // A feature-scoped re-render without waiting for the next poll tick keeps
  // switching features feeling immediate.
  tick();
});

async function tick() {
  try {
    // Unscoped log fetch drives the feature switcher (needs to see every
    // feature) and the attention band (needs to see every open gate, not
    // just the selected feature's).
    const allLog = await api.log();
    renderFeatureSwitcher(allLog.entries);

    const selected = getSelectedFeature();

    const [scopedLog, panesResult, tasksResult] = await Promise.all([
      selected ? api.log({ feature: selected }) : Promise.resolve(allLog),
      api.panes(),
      // Scoped to the selected feature when one is chosen -- previously
      // /tasks had no idea which feature was selected at all, so switching
      // features in the UI never changed which tasks.md it returned.
      selected ? api.tasks({ feature: selected }) : api.tasks(),
    ]);

    renderAttentionBand({
      logEntries: allLog.entries,
      panesAvailable: panesResult.panes_unavailable === false,
      panes: panesResult.panes,
    });

    renderStepReports(scopedLog.entries);

    renderTaskBoard({
      phases: tasksResult.phases,
      panes: panesResult.panes,
      logEntries: scopedLog.entries,
    });

    renderTotalsPanel(panesResult.panes);
  } catch (err) {
    // A failed poll cycle should not crash the page — surface it quietly and
    // try again next tick, per "calm by default" even under backend errors.
    console.error("dashboard poll failed:", err);
  }
}

tick();
setInterval(tick, POLL_INTERVAL_MS);
