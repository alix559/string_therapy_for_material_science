"""Plotly dashboards for solubility / SMI-TED (mat-gram) viz routes."""

from __future__ import annotations

from .encode_pass import build_figure as build_encode_pass_figure
from .latent_space_interpolation import build_figure as build_latent_interpolation_figure
from .molecular_structure_rendering import build_figure as build_molecular_structure_figure
from .property_prediction_diagnostics import build_figure as build_parity_figure
from .roundtrip_decode import build_figure as build_roundtrip_figure
from .similarity_attention_heat_map import build_figure as build_attention_heatmap_figure

__all__ = [
    "build_encode_pass_figure",
    "build_attention_heatmap_figure",
    "build_parity_figure",
    "build_latent_interpolation_figure",
    "build_molecular_structure_figure",
    "build_roundtrip_figure",
]
