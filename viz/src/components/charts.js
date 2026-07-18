import * as Plot from "npm:@observablehq/plot";

export function scatterPlot(payload) {
  const plot = payload?.plot ?? {};
  const points = plot.points ?? [];
  return Plot.plot({
    title: payload?.endpoint ?? "scatter",
    subtitle: payload?.placeholder ? "placeholder data from API" : null,
    x: {label: plot.x_label ?? "x", grid: true},
    y: {label: plot.y_label ?? "y", grid: true},
    marks: [
      Plot.frame(),
      Plot.dot(points, {x: "x", y: "y", r: 6, fill: "steelblue", tip: true}),
      Plot.line(points, {x: "x", y: "y", stroke: "steelblue", strokeOpacity: 0.35}),
    ],
  });
}

export function heatmapPlot(payload) {
  const plot = payload?.plot ?? {};
  const xs = plot.x ?? [];
  const ys = plot.y ?? [];
  const zs = plot.z ?? [];
  const cells = [];
  for (let i = 0; i < ys.length; i++) {
    for (let j = 0; j < xs.length; j++) {
      cells.push({
        x: xs[j],
        y: String(ys[i]),
        z: zs[i]?.[j] ?? null,
      });
    }
  }
  return Plot.plot({
    title: payload?.endpoint ?? "heatmap",
    subtitle: payload?.placeholder ? "placeholder data from API" : null,
    x: {label: plot.x_label ?? "x", domain: xs},
    y: {label: plot.y_label ?? "y", domain: ys.map(String)},
    color: {legend: true, label: plot.z_label ?? "z", scheme: "YlGnBu"},
    marks: [
      Plot.cell(cells, {x: "x", y: "y", fill: "z", tip: true}),
      Plot.text(cells, {
        x: "x",
        y: "y",
        text: (d) => (d.z == null ? "" : d.z.toFixed(1)),
        fill: "black",
        fontSize: 11,
      }),
    ],
  });
}

export function timeseriesPlot(payload) {
  const plot = payload?.plot ?? {};
  const series = plot.series ?? [];
  return Plot.plot({
    title: payload?.endpoint ?? "timeseries",
    subtitle: payload?.placeholder ? "placeholder data from API" : null,
    x: {label: plot.x_label ?? "t", grid: true},
    y: {label: plot.y_label ?? "y", grid: true},
    marks: [
      Plot.frame(),
      Plot.line(series, {x: "t", y: "y", stroke: "darkorange", strokeWidth: 2}),
      Plot.dot(series, {x: "t", y: "y", r: 5, fill: "darkorange", tip: true}),
    ],
  });
}
