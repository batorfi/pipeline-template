// Thin fetch wrapper — same-origin only, per the zero-external-calls
// requirement (FE-050). No base URL configuration point that could be
// pointed at an external host.

async function getJSON(path) {
  const response = await fetch(path, { credentials: "same-origin" });
  if (!response.ok) {
    throw new Error(`${path} responded ${response.status}`);
  }
  return response.json();
}

export const api = {
  log: (params = {}) => getJSON(`/log${toQuery(params)}`),
  tasks: (params = {}) => getJSON(`/tasks${toQuery(params)}`),
  panes: () => getJSON("/panes"),
  config: () => getJSON("/config"),
  stats: (params = {}) => getJSON(`/stats${toQuery(params)}`),
};

function toQuery(params) {
  const entries = Object.entries(params).filter(([, v]) => v !== undefined && v !== null);
  if (entries.length === 0) return "";
  return "?" + new URLSearchParams(entries).toString();
}
