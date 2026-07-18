"""Shared Starlette helpers for placeholder viz services."""

from __future__ import annotations

from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route


def make_app(routes: list[Route]) -> Starlette:
    app = Starlette(routes=routes)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
