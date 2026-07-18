"""Sample FastHTML UI: plain-English prompt → string_therapy → Plotly visualization."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fasthtml.common import (
    H1,
    H2,
    Main,
    P,
    Div,
    Form,
    Textarea,
    Button,
    Script,
    Style,
    A,
    Span,
    Pre,
    Details,
    Summary,
    fast_app,
)
from starlette.testclient import TestClient

REPO = Path(__file__).resolve().parents[1]
load_dotenv(REPO / '.env', override=True)

from string_therapy import create_app  # noqa: E402

PORT = int(os.getenv('CHAT_UI_PORT', '5020'))
OBSERVABLE_BASE = os.getenv('OBSERVABLE_UI_URL', 'http://127.0.0.1:3000')

_controller = TestClient(create_app())

CSS = """
:root {
  --bg: #f4f1eb;
  --ink: #1c1917;
  --muted: #57534e;
  --accent: #0f766e;
  --card: #fffdf8;
  --line: #d6d3d1;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  color: var(--ink);
  background:
    radial-gradient(circle at top left, #d9f0ea 0%, transparent 40%),
    linear-gradient(180deg, #efe8dc 0%, var(--bg) 45%, #e7e0d4 100%);
  min-height: 100vh;
}
main {
  max-width: 920px;
  margin: 0 auto;
  padding: 2.5rem 1.25rem 4rem;
}
h1 {
  font-size: clamp(2rem, 4vw, 2.75rem);
  letter-spacing: -0.03em;
  margin: 0 0 0.35rem;
}
.lead { color: var(--muted); margin: 0 0 1.75rem; max-width: 38rem; }
.panel {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 1.25rem;
  box-shadow: 0 18px 40px rgba(28, 25, 23, 0.06);
}
textarea {
  width: 100%;
  min-height: 7rem;
  resize: vertical;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 0.9rem 1rem;
  font: inherit;
  background: #fff;
}
.actions { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.85rem; }
button, .link-btn {
  appearance: none;
  border: 0;
  border-radius: 999px;
  padding: 0.7rem 1.2rem;
  background: var(--accent);
  color: white;
  font: inherit;
  font-size: 0.95rem;
  cursor: pointer;
  text-decoration: none;
}
button.secondary, .link-btn.secondary {
  background: transparent;
  color: var(--accent);
  border: 1px solid color-mix(in srgb, var(--accent) 45%, white);
}
#result { margin-top: 1.5rem; }
.meta {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 0.75rem;
  color: var(--muted);
  font-size: 0.95rem;
}
.pill {
  display: inline-block;
  border-radius: 999px;
  padding: 0.2rem 0.7rem;
  background: #ccfbf1;
  color: #115e59;
  font-size: 0.85rem;
}
#chart {
  width: 100%;
  min-height: 420px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: white;
}
details {
  margin-top: 1rem;
  color: var(--muted);
}
pre {
  overflow: auto;
  background: #1c1917;
  color: #f5f5f4;
  padding: 1rem;
  border-radius: 12px;
  font-size: 0.8rem;
}
.htmx-request button { opacity: 0.7; }
.error { color: #b91c1c; }
"""

app, rt = fast_app(
    hdrs=(
        Script(src='https://cdn.plot.ly/plotly-2.35.2.min.js'),
        Script(src='https://unpkg.com/htmx.org@2.0.4'),
        Style(CSS),
    ),
    pico=False,
)


def _extract_payload(data: dict[str, Any]) -> dict[str, Any]:
    parsed = data.get('parsed')
    if isinstance(parsed, dict) and parsed.get('plot'):
        return parsed
    response = data.get('response')
    if isinstance(response, dict) and response.get('plot'):
        return response
    if isinstance(response, str):
        try:
            obj = json.loads(response)
        except json.JSONDecodeError:
            return {}
        if isinstance(obj, dict) and obj.get('plot'):
            return obj
    return {}


def _plotly_figure(payload: dict[str, Any]) -> dict[str, Any] | None:
    plot = payload.get('plot') or {}
    kind = (payload.get('visualization') or plot.get('type') or '').lower()

    if kind == 'scatter' or plot.get('points'):
        points = plot.get('points') or []
        return {
            'data': [{
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': [p.get('x') for p in points],
                'y': [p.get('y') for p in points],
                'marker': {'size': 10, 'color': '#0f766e'},
                'line': {'color': '#0f766e'},
            }],
            'layout': {
                'title': 'Solubility scatter',
                'xaxis': {'title': plot.get('x_label') or 'x'},
                'yaxis': {'title': plot.get('y_label') or 'y'},
                'margin': {'t': 48, 'r': 24, 'b': 48, 'l': 56},
            },
        }

    if kind == 'heatmap' or plot.get('z') is not None:
        return {
            'data': [{
                'type': 'heatmap',
                'x': plot.get('x') or [],
                'y': [str(v) for v in (plot.get('y') or [])],
                'z': plot.get('z') or [],
                'colorscale': 'YlGnBu',
                'colorbar': {'title': plot.get('z_label') or 'z'},
            }],
            'layout': {
                'title': 'Solubility heatmap',
                'xaxis': {'title': plot.get('x_label') or 'x'},
                'yaxis': {'title': plot.get('y_label') or 'y'},
                'margin': {'t': 48, 'r': 24, 'b': 48, 'l': 56},
            },
        }

    if kind in {'timeseries', 'time_series'} or plot.get('series'):
        series = plot.get('series') or []
        return {
            'data': [{
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': [p.get('t') for p in series],
                'y': [p.get('y') for p in series],
                'marker': {'size': 9, 'color': '#c2410c'},
                'line': {'color': '#c2410c', 'width': 3},
            }],
            'layout': {
                'title': 'Solubility timeseries',
                'xaxis': {'title': plot.get('x_label') or 't'},
                'yaxis': {'title': plot.get('y_label') or 'y'},
                'margin': {'t': 48, 'r': 24, 'b': 48, 'l': 56},
            },
        }

    return None


def _observable_path(kind: str) -> str | None:
    mapping = {
        'scatter': '/scatter',
        'heatmap': '/heatmap',
        'timeseries': '/timeseries',
        'time_series': '/timeseries',
    }
    path = mapping.get((kind or '').lower())
    return f'{OBSERVABLE_BASE.rstrip("/")}{path}' if path else None


@rt('/')
def get():
    examples = [
        'Make a scatter plot of NaCl solubility vs temperature',
        'Show a heatmap of solubility across solvents and temperatures',
        'Plot solubility as a time series over 60 minutes',
    ]
    return Main(
        H1('Solubility visualizer'),
        P(
            'Type a request in plain English. '
            'string_therapy routes it to a viz endpoint, then this UI opens the chart.',
            cls='lead',
        ),
        Div(
            Form(
                Textarea(
                    name='message',
                    placeholder=examples[0],
                    required=True,
                ),
                Div(
                    Button('Visualize', type='submit'),
                    Button('Clear', type='button', cls='secondary', onclick='document.getElementById("result").innerHTML=""'),
                    cls='actions',
                ),
                hx_post='/ask',
                hx_target='#result',
                hx_indicator='.actions',
            ),
            P(
                Span('Try: ', style='color:var(--muted)'),
                *[
                    A(
                        ex,
                        href='#',
                        cls='link-btn secondary',
                        style='display:inline-block;margin:0.25rem 0.35rem 0.25rem 0;font-size:0.85rem',
                        onclick=(
                            'event.preventDefault();'
                            'const t=document.querySelector("textarea[name=message]");'
                            f't.value={json.dumps(ex)};'
                        ),
                    )
                    for ex in examples
                ],
            ),
            cls='panel',
        ),
        Div(id='result'),
    )


@rt('/ask')
def post(message: str = ''):
    message = (message or '').strip()
    if not message:
        return Div(P('Enter a message first.', cls='error'))

    try:
        response = _controller.post(
            '/controller',
            json={'message': message, 'response_format': 'json'},
        )
    except Exception as exc:  # noqa: BLE001
        return Div(P(f'Controller call failed: {exc}', cls='error'))

    try:
        data = response.json()
    except Exception:  # noqa: BLE001
        return Div(
            P(f'Controller returned HTTP {response.status_code}', cls='error'),
            Pre(response.text[:2000]),
        )

    if response.status_code >= 400:
        return Div(
            P(f'Controller error HTTP {response.status_code}', cls='error'),
            Pre(json.dumps(data, indent=2)[:3000]),
        )

    payload = _extract_payload(data)
    kind = (payload.get('visualization') or payload.get('endpoint') or 'unknown').replace('solubility_', '')
    figure = _plotly_figure(payload)
    obs = _observable_path(kind if kind in {'scatter', 'heatmap', 'timeseries'} else payload.get('visualization', ''))

    if figure is None:
        return Div(
            Div(
                Span('No plot payload in controller response', cls='pill'),
                cls='meta',
            ),
            P('The router may have failed, or the downstream service returned non-plot JSON.', cls='error'),
            Pre(json.dumps(data, indent=2)[:4000]),
            cls='panel',
        )

    fig_json = json.dumps(figure)
    meta_children = [
        Span(kind, cls='pill'),
        Span(f"request {data.get('request_id', '—')}"),
    ]
    if obs:
        meta_children.append(
            A('Open Observable page', href=obs, target='_blank', cls='link-btn secondary')
        )

    return Div(
        Div(*meta_children, cls='meta'),
        H2('Visualization'),
        Div(id='chart'),
        Script(
            f'const fig = {fig_json};\n'
            "Plotly.newPlot('chart', fig.data, fig.layout, {responsive: true});"
        ),
        Details(
            Summary('Raw string_therapy / API payload'),
            Pre(json.dumps({'controller': data, 'plot_payload': payload}, indent=2)[:8000]),
        ),
        cls='panel',
    )


if __name__ == '__main__':
    import uvicorn

    print(f'Chat UI on http://127.0.0.1:{PORT}')
    print('Prereq: pixi run serve-viz  (and seeded router graph)')
    uvicorn.run(app, host='127.0.0.1', port=PORT)
