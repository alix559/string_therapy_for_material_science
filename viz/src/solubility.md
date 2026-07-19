# Solubility

Category from the router graph. Endpoints below are what the materials router can invoke for solubility visualizations.

```js
const graph = FileAttachment("./data/router_graph.json").json();
```

```js
const category = graph.nodes.find((n) => n.node_type === "category" && n.intent === "solubility");
const byId = new Map(graph.nodes.map((n) => [n.id, n]));
const endpoints = graph.edges
  .filter((e) => e.source === category.id)
  .map((e) => byId.get(e.target))
  .filter((n) => n && n.node_type === "endpoint");

const pageFor = (intent) => {
  if (intent.includes("scatter")) return "./scatter";
  if (intent.includes("heatmap")) return "./heatmap";
  if (intent.includes("timeseries") || intent.includes("time_series")) return "./timeseries";
  return "./";
};
```

```js
display(html`<p class="muted">${category.description}</p>`);
```

```js
for (const ep of endpoints) {
  display(html`
    <div class="card" style="margin-bottom:1rem">
      <h2><a href="${pageFor(ep.intent)}">${ep.intent}</a></h2>
      <p>${ep.description || ""}</p>
      <p class="muted"><code>${(ep.method || "").toUpperCase()}</code> ${ep.url || ""}</p>
      <p class="muted">params: ${(ep.parameters || []).join(", ") || "—"}</p>
      ${Array.isArray(ep.instruction) && ep.instruction.length
        ? html`<ul>${ep.instruction.map((line) => html`<li>${line}</li>`)}</ul>`
        : ""}
    </div>
  `);
}
```

```js
display(Inputs.textarea({
  label: "Raw endpoint JSON",
  value: JSON.stringify(endpoints, null, 2),
  rows: 16,
  disabled: true,
  width: "100%",
}));
```
