"""SMI-TED embedding-space scatter via local mat-gram ``/embeddings``."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.manifold import TSNE

SERVICES = Path(__file__).resolve().parents[2] / "services"
if str(SERVICES) not in sys.path:
    sys.path.insert(0, str(SERVICES))

from matgram_client import embeddings as fetch_embeddings  # noqa: E402
from matgram_client import extract_smiles  # noqa: E402


def build_figure(
    embeddings: np.ndarray | None = None,
    smiles: list[str] | None = None,
    props: np.ndarray | None = None,
    *,
    message: str | None = None,
    body: dict[str, Any] | None = None,
    **_: Any,
) -> go.Figure:
    meta: dict[str, Any] = {"placeholder": False, "source": "matgram"}
    color_label = "property"

    if embeddings is None:
        smiles = smiles or extract_smiles(message, min_count=3)
        out = fetch_embeddings(smiles)
        vectors = out.get("embeddings") or []
        if not vectors:
            raise RuntimeError("mat-gram returned no embeddings")
        embeddings = np.asarray(vectors, dtype=float)
        smiles = smiles[: len(embeddings)]
        preds = out.get("predictions")
        if preds is not None:
            props = np.asarray(preds, dtype=float)
            color_label = f"prediction ({out.get('task') or 'property'})"
        else:
            props = np.linalg.norm(embeddings, axis=1)
            color_label = "‖z‖₂"
        meta.update(
            {
                "model": out.get("model"),
                "mode": out.get("mode"),
                "task": out.get("task"),
            }
        )
    else:
        embeddings = np.asarray(embeddings, dtype=float)
        if smiles is None:
            smiles = [f"mol_{i}" for i in range(len(embeddings))]
        if props is None:
            props = np.linalg.norm(embeddings, axis=1)

    n = len(embeddings)
    if n < 2:
        raise RuntimeError("need at least 2 SMILES for an encode-pass scatter")
    perplexity = max(2, min(30, n - 1))
    proj = TSNE(
        n_components=2,
        init="pca",
        perplexity=perplexity,
        random_state=0,
    ).fit_transform(embeddings)

    df = pd.DataFrame(
        {
            "x": proj[:, 0],
            "y": proj[:, 1],
            "smiles": smiles,
            "property": props,
        }
    )
    fig = px.scatter(
        df,
        x="x",
        y="y",
        color="property",
        hover_data=["smiles"],
        title="SMI-TED embedding space (mat-gram /embeddings)",
        color_continuous_scale="viridis",
        labels={"property": color_label, "x": "t-SNE 1", "y": "t-SNE 2"},
    )
    fig.update_traces(marker=dict(size=9, opacity=0.85))
    fig._matgram_meta = meta  # type: ignore[attr-defined]
    return fig
