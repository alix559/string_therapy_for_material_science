# Scatter

Fetches `POST /data-visualizations/scatter` and renders with Observable Plot.

```js
import {fetchViz} from "./components/api.js";
import {scatterPlot} from "./components/charts.js";
```

```js
const message = view(Inputs.text({
  label: "Message forwarded to the API",
  value: "plot NaCl solubility vs temperature",
  width: "100%",
}));
```

```js
const payload = await fetchViz("scatter", message);
```

```js
display(scatterPlot(payload));
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
