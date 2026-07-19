"""Parity plot for property predictions via mat-gram property-mode ``/embeddings``."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import plotly.graph_objects as go
from sklearn.metrics import r2_score

SERVICES = Path(__file__).resolve().parents[2] / "services"
if str(SERVICES) not in sys.path:
    sys.path.insert(0, str(SERVICES))

from matgram_client import ESOL_DEMO  # noqa: E402
from matgram_client import embeddings as fetch_embeddings  # noqa: E402
from matgram_client import extract_labeled_pairs  # noqa: E402
from matgram_client import extract_smiles  # noqa: E402


def build_figure(
    y_true: np.ndarray | None = None,
    y_pred: np.ndarray | None = None,
    *,
    message: str | None = None,
    body: dict[str, Any] | None = None,
    **_: Any,
) -> go.Figure:
    meta: dict[str, Any] = {"placeholder": False, "source": "matgram"}

    if y_true is None or y_pred is None:
        pairs = extract_labeled_pairs(message)
        if pairs:
            smiles = [p[0] for p in pairs]
            y_true = np.asarray([p[1] for p in pairs], dtype=float)
        else:
            smiles = extract_smiles(message, min_count=4)
            # Prefer molecules that have demo labels.
            labeled = [s for s in smiles if s in ESOL_DEMO]
            if len(labeled) < 3:
                smiles = list(ESOL_DEMO.keys())
            else:
                smiles = labeled
            y_true = np.asarray([ESOL_DEMO[s] for s in smiles], dtype=float)

        out = fetch_embeddings(smiles)
        mode = out.get("mode") or "embedding"
        preds = out.get("predictions")
        if preds is None:
            raise RuntimeError(
                "mat-gram is in embedding mode; load a finetune checkpoint "
                "(task=esol|bbbp|lipo) via POST /load before using parity plots"
            )
        y_pred = np.asarray(preds, dtype=float)[: len(y_true)]
        y_true = y_true[: len(y_pred)]
        smiles = smiles[: len(y_pred)]
        meta.update(
            {
                "model": out.get("model"),
                "mode": mode,
                "task": out.get("task"),
            }
        )
        hover = smiles
        task = out.get("task") or "property"
    else:
        y_true = np.asarray(y_true, dtype=float)
        y_pred = np.asarray(y_pred, dtype=float)
        hover = [f"mol_{i}" for i in range(len(y_true))]
        task = "property"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=y_true,
            y=y_pred,
            mode="markers",
            text=hover,
            marker=dict(
                size=9,
                opacity=0.75,
                color=np.abs(y_true - y_pred),
                colorscale="Reds",
                colorbar=dict(title="|err|"),
            ),
            hovertemplate=(
                "%{text}<br>Actual: %{x:.3f}<br>Predicted: %{y:.3f}<extra></extra>"
            ),
            name="Predictions",
        )
    )
    min_val = float(min(y_true.min(), y_pred.min()))
    max_val = float(max(y_true.max(), y_pred.max()))
    fig.add_trace(
        go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode="lines",
            line=dict(dash="dash", color="gray"),
            name="Perfect prediction",
        )
    )
    r2 = r2_score(y_true, y_pred) if len(y_true) > 1 else float("nan")
    fig.update_layout(
        title=f"Parity — {task} (R² = {r2:.3f}) via mat-gram /embeddings",
        xaxis_title="Actual",
        yaxis_title="Predicted",
    )
    fig._matgram_meta = meta  # type: ignore[attr-defined]
    return fig
