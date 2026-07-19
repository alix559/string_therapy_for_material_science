# Solubility visualizations

UI for the three placeholder endpoints routed by `string_therapy`.

Prereq: start the APIs from the repo root with `pixi run serve-viz`.

<p><a href="./solubility"><strong>Solubility category</strong></a> — endpoint docs opened from the router graph node.</p>

<div class="grid grid-cols-3">
  <div class="card">
    <h2><a href="./scatter">Scatter</a></h2>
    <p class="muted">Solubility vs temperature / concentration</p>
  </div>
  <div class="card">
    <h2><a href="./heatmap">Heatmap</a></h2>
    <p class="muted">Solubility across solvents and temperatures</p>
  </div>
  <div class="card">
    <h2><a href="./timeseries">Timeseries</a></h2>
    <p class="muted">Solubility trend over time</p>
  </div>
</div>

```js
import {ENDPOINTS} from "./components/api.js";
```

| Chart | API |
|-------|-----|
| Scatter | `${ENDPOINTS.scatter}` |
| Heatmap | `${ENDPOINTS.heatmap}` |
| Timeseries | `${ENDPOINTS.timeseries}` |
