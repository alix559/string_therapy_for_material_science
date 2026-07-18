# Timeseries

Fetches `POST /data-visualizations/timeseries` and renders with Observable Plot.

```js
import {fetchViz} from "./components/api.js";
import {timeseriesPlot} from "./components/charts.js";
```

```js
const message = view(Inputs.text({
  label: "Message forwarded to the API",
  value: "solubility over 60 minutes",
  width: "100%",
}));
```

```js
const payload = await fetchViz("timeseries", message);
```

```js
display(timeseriesPlot(payload));
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
