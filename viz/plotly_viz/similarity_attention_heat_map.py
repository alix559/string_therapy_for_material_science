"""Pairwise embedding cosine-similarity heatmap via mat-gram ``/embeddings``.

Named for the original attention route; the MAX serve API does not expose
token attention, so this surfaces a real model signal instead.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import plotly.express as px
import plotly.graph_objects as go

SERVICES = Path(__file__).resolve().parents[2] / "services"
if str(SERVICES) not in sys.path:
    sys.path.insert(0, str(SERVICES))

from matgram_client import embeddings as fetch_embeddings  # noqa: E402
from matgram_client import extract_smiles  # noqa: E402


def _cosine_sim(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-12, None)
    unit = matrix / norms
    return unit @ unit.T


def build_figure(
    smiles: str | list[str] | None = None,
    attention_weights: np.ndarray | None = None,
    *,
    message: str | None = None,
    body: dict[str, Any] | None = None,
    **_: Any,
) -> go.Figure:
    meta: dict[str, Any] = {"placeholder": False, "source": "matgram"}

    if attention_weights is not None and smiles is not None:
        tokens = list(smiles) if isinstance(smiles, str) else list(smiles)
        sim = np.asarray(attention_weights, dtype=float)
        title = "Token similarity (caller-supplied)"
        meta["placeholder"] = True
        meta["source"] = "caller"
    else:
        if isinstance(smiles, str):
            mols = [smiles]
        elif smiles is None:
            mols = extract_smiles(message, min_count=3)
        else:
            mols = list(smiles)
        # Cap for readable heatmaps.
        mols = mols[:16]
        out = fetch_embeddings(mols)
        vectors = np.asarray(out.get("embeddings") or [], dtype=float)
        if len(vectors) < 2:
            raise RuntimeError("need at least 2 SMILES for a similarity heatmap")
        mols = mols[: len(vectors)]
        sim = _cosine_sim(vectors)
        tokens = mols
        title = "SMI-TED embedding cosine similarity (mat-gram /embeddings)"
        meta.update(
            {
                "model": out.get("model"),
                "mode": out.get("mode"),
                "task": out.get("task"),
            }
        )

    fig = px.imshow(
        sim,
        x=tokens,
        y=tokens,
        color_continuous_scale="Blues",
        zmin=float(np.min(sim)),
        zmax=1.0,
        title=title,
        labels=dict(x="SMILES", y="SMILES", color="cosine"),
    )
    fig.update_layout(width=720, height=640)
    fig.update_xaxes(tickangle=45)
    fig._matgram_meta = meta  # type: ignore[attr-defined]
    return fig
