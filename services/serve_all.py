"""Run all placeholder solubility visualization servers."""

from __future__ import annotations

import signal
import subprocess
import sys
from pathlib import Path

SCRIPTS = (
    'serve_scatter.py',
    'serve_heatmap.py',
    'serve_timeseries.py',
)


def main() -> int:
    root = Path(__file__).resolve().parent
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

    for name in SCRIPTS:
        procs.append(subprocess.Popen([sys.executable, str(root / name)]))

    try:
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        shutdown()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
