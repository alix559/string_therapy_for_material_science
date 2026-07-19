"""Detailed round-trip visualization: input vs decoded SMILES + embedding norms."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

SERVICES = Path(__file__).resolve().parents[2] / "services"
if str(SERVICES) not in sys.path:
    sys.path.insert(0, str(SERVICES))

from matgram_client import extract_smiles  # noqa: E402
from matgram_client import roundtrip as fetch_roundtrip  # noqa: E402


def build_figure(
    smiles: list[str] | None = None,
    *,
    message: str | None = None,
    body: dict[str, Any] | None = None,
    **_: Any,
) -> go.Figure:
    meta: dict[str, Any] = {"placeholder": False, "source": "matgram"}
    mols = smiles or extract_smiles(message, min_count=1)
    mols = mols[:10]

    out = fetch_roundtrip(mols)
    inputs = out.get("input_smiles") or mols
    decoded = out.get("decoded_smiles") or []
    vectors = np.asarray(out.get("embeddings") or [], dtype=float)
    if len(decoded) < len(inputs):
        decoded = list(decoded) + [""] * (len(inputs) - len(decoded))
    norms = (
        np.linalg.norm(vectors, axis=1)
        if len(vectors)
        else np.zeros(len(inputs))
    )
    match = [a == b for a, b in zip(inputs, decoded)]

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.55, 0.45],
        subplot_titles=("Embedding ‖z‖₂", "Exact decode match"),
        vertical_spacing=0.12,
    )
    fig.add_trace(
        go.Bar(
            x=[f"{i}:{s}" for i, s in enumerate(inputs)],
            y=norms,
            marker_color="#0369a1",
            hovertemplate="%{x}<br>decoded=%{customdata}<br>‖z‖=%{y:.3f}<extra></extra>",
            customdata=decoded,
            name="‖z‖₂",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=[f"{i}:{s}" for i, s in enumerate(inputs)],
            y=[1 if m else 0 for m in match],
            marker_color=["#15803d" if m else "#b91c1c" for m in match],
            hovertemplate="%{x}<br>decoded=%{customdata}<extra></extra>",
            customdata=decoded,
            name="match",
            showlegend=False,
        ),
        row=2,
        col=1,
    )
    n_ok = sum(match)
    fig.update_layout(
        title=f"SMI-TED round-trip ({n_ok}/{len(inputs)} exact) — mat-gram /roundtrip",
        height=640,
    )
    fig.update_yaxes(title_text="‖z‖₂", row=1, col=1)
    fig.update_yaxes(
        title_text="match",
        range=[-0.05, 1.25],
        tickvals=[0, 1],
        ticktext=["no", "yes"],
        row=2,
        col=1,
    )
    fig.update_xaxes(tickangle=35, row=2, col=1)
    meta.update({"model": out.get("model"), "mode": "embedding"})
    fig._matgram_meta = meta  # type: ignore[attr-defined]
    return fig
