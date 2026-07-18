# Heatmap

Fetches `POST /data-visualizations/heatmap` and renders with Observable Plot.

```js
import {fetchViz} from "./components/api.js";
import {heatmapPlot} from "./components/charts.js";
```

```js
const message = view(Inputs.text({
  label: "Message forwarded to the API",
  value: "heatmap of solubility across solvents",
  width: "100%",
}));
```

```js
const payload = await fetchViz("heatmap", message);
```

```js
display(heatmapPlot(payload));
```

```js
display(Inputs.textarea({
  label: "Raw API response",
  value: JSON.stringify(payload, null, 2),
  rows: 14,
  disabled: true,
  width: "100%",
}));
```
