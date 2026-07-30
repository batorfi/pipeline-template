// Shared gate metadata — the exact move set per gate stage, per the pipeline
// concept. Used by both the attention band and (later) any gate-detail view.

export const GATE_STAGES = {
  concept_gate: { label: "Concept gate", moves: ["approve", "revise", "reject"] },
  architecture_gate: { label: "Architecture gate", moves: ["approve", "revise", "reject"] },
  spec_gate: { label: "Spec gate", moves: ["approve", "revise"] },
  plan_gate: { label: "Plan gate", moves: ["approve", "revise"] },
  checkpoint_gate: { label: "Checkpoint gate", moves: ["approve", "revise"] },
  review_gate: { label: "Review gate", moves: ["approve", "restart"] },
  verification_gate: { label: "Verification gate", moves: ["approve", "reject"] },
  docs_gate: { label: "Docs gate", moves: ["approve", "revise", "reject"] },
  pr_gate: { label: "PR gate", moves: ["approve", "revise", "reject"] },
};

export function isGateStage(stage) {
  return Object.prototype.hasOwnProperty.call(GATE_STAGES, stage);
}

// An "open" gate is the most recent entry for a given (feature, stage) pair
// where decision is still null — presented, not yet answered.
export function findOpenGates(logEntries) {
  const latestByKey = new Map();

  // logEntries from /log are newest-first; keep only the first (=latest) we
  // see per (feature, stage) key.
  for (const entry of logEntries) {
    if (!isGateStage(entry.stage)) continue;
    const key = `${entry.feature}::${entry.stage}`;
    if (!latestByKey.has(key)) {
      latestByKey.set(key, entry);
    }
  }

  const open = [...latestByKey.values()].filter((e) => e.decision === null || e.decision === undefined);
  // oldest open gate first
  open.sort((a, b) => (a.timestamp < b.timestamp ? -1 : a.timestamp > b.timestamp ? 1 : 0));
  return open;
}
