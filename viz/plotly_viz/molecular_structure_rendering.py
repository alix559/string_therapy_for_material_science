"""Round-trip encode→decode summary for one or more SMILES (mat-gram)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import plotly.graph_objects as go

SERVICES = Path(__file__).resolve().parents[2] / "services"
if str(SERVICES) not in sys.path:
    sys.path.insert(0, str(SERVICES))

from matgram_client import extract_smiles  # noqa: E402
from matgram_client import roundtrip as fetch_roundtrip  # noqa: E402


def build_figure(
    smiles: str | list[str] | None = None,
    *,
    message: str | None = None,
    body: dict[str, Any] | None = None,
    **_: Any,
) -> go.Figure:
    meta: dict[str, Any] = {"placeholder": False, "source": "matgram"}

    if isinstance(smiles, str):
        mols = [smiles]
    elif smiles is None:
        mols = extract_smiles(message, min_count=1)[:8]
    else:
        mols = list(smiles)[:8]

    out = fetch_roundtrip(mols)
    inputs = out.get("input_smiles") or mols
    decoded = out.get("decoded_smiles") or []
    if len(decoded) < len(inputs):
        decoded = decoded + [""] * (len(inputs) - len(decoded))

    match = [int(a == b) for a, b in zip(inputs, decoded)]
    colors = ["#15803d" if m else "#b91c1c" for m in match]
    labels = [
        f"{a} → {b}" if b else f"{a} → ?"
        for a, b in zip(inputs, decoded)
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                x=list(range(len(inputs))),
                y=match,
                text=labels,
                textposition="outside",
                marker_color=colors,
                hovertemplate="%{text}<br>exact match=%{y}<extra></extra>",
            )
        ]
    )
    n_ok = sum(match)
    fig.update_layout(
        title=(
            f"Encode→decode round-trip ({n_ok}/{len(inputs)} exact) "
            "via mat-gram /roundtrip"
        ),
        xaxis_title="Molecule index",
        yaxis_title="Exact SMILES match",
        yaxis=dict(range=[-0.05, 1.25], tickvals=[0, 1], ticktext=["no", "yes"]),
        margin=dict(t=72, b=48),
    )
    meta.update({"model": out.get("model"), "mode": "embedding", "task": None})
    fig._matgram_meta = meta  # type: ignore[attr-defined]
    return fig
