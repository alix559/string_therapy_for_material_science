"""Latent-space interpolation between two molecules via embed → lerp → decode."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import plotly.graph_objects as go

SERVICES = Path(__file__).resolve().parents[2] / "services"
if str(SERVICES) not in sys.path:
    sys.path.insert(0, str(SERVICES))

from matgram_client import decode as fetch_decode  # noqa: E402
from matgram_client import embeddings as fetch_embeddings  # noqa: E402
from matgram_client import extract_smiles  # noqa: E402


def build_figure(
    smiles_a: str | None = None,
    smiles_b: str | None = None,
    steps: int = 8,
    *,
    message: str | None = None,
    body: dict[str, Any] | None = None,
    **_: Any,
) -> go.Figure:
    meta: dict[str, Any] = {"placeholder": False, "source": "matgram"}
    body = body or {}
    steps = int(body.get("steps") or steps)
    steps = max(3, min(steps, 24))

    mols = extract_smiles(message, min_count=2)
    a = smiles_a or mols[0]
    b = smiles_b or (mols[1] if len(mols) > 1 else "c1ccccc1")

    out = fetch_embeddings([a, b])
    vectors = np.asarray(out.get("embeddings") or [], dtype=float)
    if len(vectors) < 2:
        raise RuntimeError("mat-gram did not return embeddings for both endpoints")
    z_start, z_end = vectors[0], vectors[1]
    interpolated = np.linspace(z_start, z_end, steps)

    decoded = fetch_decode(interpolated.tolist())
    decoded_smiles = decoded.get("smiles") or []
    if len(decoded_smiles) != steps:
        # Fall back to endpoint labels if decode length mismatches.
        decoded_smiles = [
            a if i == 0 else b if i == steps - 1 else f"INT_{i}"
            for i in range(steps)
        ]

    preds = out.get("predictions")
    if preds is not None and len(preds) >= 2:
        # Linear blend of scalar property predictions for the y-axis.
        y = np.linspace(float(preds[0]), float(preds[1]), steps)
        y_title = f"interpolated prediction ({out.get('task') or 'property'})"
    else:
        y = np.linalg.norm(interpolated, axis=1)
        y_title = "‖z‖₂ along path"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(steps)),
            y=y,
            mode="lines+markers+text",
            text=decoded_smiles,
            textposition="top center",
            hovertemplate=(
                "Step %{x}<br>Decoded: %{text}<br>"
                + y_title
                + ": %{y:.4f}<extra></extra>"
            ),
            marker=dict(size=10, color="#0f766e"),
            line=dict(color="#0f766e", width=2),
        )
    )
    fig.update_layout(
        title=f"Latent interpolation: {a} → {b} (mat-gram embed/decode)",
        xaxis_title="Step",
        yaxis_title=y_title,
        margin=dict(t=72, b=64),
    )
    meta.update(
        {
            "model": out.get("model") or decoded.get("model"),
            "mode": out.get("mode"),
            "task": out.get("task"),
        }
    )
    fig._matgram_meta = meta  # type: ignore[attr-defined]
    return fig
