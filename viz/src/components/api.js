/** Downstream placeholder APIs used by string_therapy routes. */
export const ENDPOINTS = {
  scatter: "http://127.0.0.1:8004/data-visualizations/scatter",
  heatmap: "http://127.0.0.1:8002/data-visualizations/heatmap",
  timeseries: "http://127.0.0.1:8003/data-visualizations/timeseries",
};

export async function fetchViz(kind, message = "") {
  const url = ENDPOINTS[kind];
  if (!url) throw new Error(`Unknown visualization: ${kind}`);
  const response = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message}),
  });
  if (!response.ok) {
    throw new Error(`${kind} request failed (${response.status})`);
  }
  return response.json();
}
