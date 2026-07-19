"""Launch LangGraph viz (from nbs/04_langgraph_viz.ipynb) + settings."""

from __future__ import annotations

import signal
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    procs: list[subprocess.Popen[bytes]] = []

    def shutdown(*_: object) -> None:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        for p in procs:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Viz: exported module from nbs/04_langgraph_viz.ipynb
    procs.append(
        subprocess.Popen(
            [sys.executable, "-m", "string_therapy_for_material_science.langgraph_viz"],
            cwd=str(REPO),
        )
    )
    # Settings lifecycle (MAX start/load/stop)
    procs.append(
        subprocess.Popen([sys.executable, str(Path(__file__).parent / "serve_settings.py")])
    )

    try:
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
