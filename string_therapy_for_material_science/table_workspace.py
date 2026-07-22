"""Tables workspace for the Graph tab — multi-query Excel/HTML tables.

Edit alongside ``ui/table_client.js``. Used by ``main01`` instead of category app widgets.
"""

from __future__ import annotations

from fasthtml.common import *


def lucide_icon(name: str, cls: str = "w-5 h-5"):
    return I(data_lucide=name, cls=cls)


def table_workspace():
    """Graph tab body: tab strip + scrollable HTML tables (filled by table_client.js)."""
    return Div(
        Div(
            lucide_icon("table-2", cls="w-4 h-4"),
            Span("Tables", cls="font-medium"),
            Span("", id="table-count-badge", cls="badge badge-primary badge-sm ml-2 hidden"),
            cls="px-4 py-2 border-b border-base-300 bg-base-100/70 flex items-center gap-2",
        ),
        Div(
            id="table-tabs",
            cls="flex items-center gap-1 px-2 py-1.5 border-b border-base-300 bg-base-100 overflow-x-auto min-h-10",
        ),
        Div(
            Div(
                lucide_icon("sheet", cls="w-10 h-10 opacity-40"),
                P(
                    "Run a ZINC query in chat to load a table here",
                    id="table-empty-msg",
                    cls="text-sm opacity-60 mt-3 text-center max-w-xs",
                ),
                id="table-empty",
                cls="flex flex-col items-center justify-center flex-1 min-h-0 p-8",
            ),
            Div(id="table-panels", cls="flex flex-col flex-1 min-h-0"),
            cls="flex flex-col flex-1 min-h-0 bg-base-200/40",
        ),
        id="graph-workspace",
        cls="flex flex-col flex-1 min-h-0",
    )
