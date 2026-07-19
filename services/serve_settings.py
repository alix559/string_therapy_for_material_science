"""Settings endpoints: start MAX / connect weights via local mat-gram API."""

from __future__ import annotations

from typing import Any

import uvicorn
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from cors_app import make_app
from matgram_client import (
    DEFAULT_WEIGHT_PATH,
    MatgramError,
    load as matgram_load,
    parse_load_request,
    status as matgram_status,
    stop as matgram_stop,
)

PORT = 8011


def _panel(title: str, st: dict[str, Any], *, action: str, note: str = "") -> dict[str, Any]:
    rows = [
        ["ready", str(st.get("ready"))],
        ["running", str(st.get("running"))],
        ["decodeReady", str(st.get("decodeReady"))],
        ["mode", str(st.get("mode"))],
        ["task", str(st.get("task"))],
        ["device", str(st.get("device"))],
        ["modelId", str(st.get("modelId"))],
        ["assetDir", str(st.get("assetDir"))],
        ["maxUrl", str(st.get("maxUrl"))],
        ["uptimeSeconds", str(st.get("uptimeSeconds"))],
        ["lastError", str(st.get("lastError"))],
    ]
    return {
        "title": title,
        "action": action,
        "note": note,
        "ready": bool(st.get("ready")),
        "rows": rows,
    }


def _ok(endpoint: str, st: dict[str, Any], *, action: str, message: Any, note: str = "") -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "endpoint": endpoint,
            "visualization": "settings_panel",
            "message": message,
            "source": "matgram",
            "placeholder": False,
            "model_status": st,
            "panel": _panel(
                "MAX / SMI-TED",
                st,
                action=action,
                note=note,
            ),
        }
    )


def _err(endpoint: str, exc: Exception, message: Any) -> JSONResponse:
    return JSONResponse(
        {
            "status": "error",
            "endpoint": endpoint,
            "visualization": "settings_panel",
            "message": message,
            "error": str(exc),
            "hint": "Is `pixi run api` (mat-gram) up on MATGRAM_API_URL?",
        },
        status_code=503,
    )


async def start_max(request: Request) -> JSONResponse:
    """Start MAX with the default pretrained weight if not already ready."""
    body = (
        await request.json()
        if request.headers.get("content-type", "").startswith("application/json")
        else {}
    )
    message = body.get("message") if isinstance(body, dict) else None
    endpoint = "settings_start_max"
    try:
        st = matgram_status()
        if st.get("ready"):
            return _ok(
                endpoint,
                st,
                action="start_max",
                message=message,
                note="MAX already ready — no reload.",
            )
        req = parse_load_request(message)
        if "checkpoint" in req and "weight_path" not in req:
            # start icon defaults to pretrained unless user named a task
            pass
        if "weight_path" not in req and "checkpoint" not in req:
            req["weight_path"] = DEFAULT_WEIGHT_PATH
        st = matgram_load(**req)
        return _ok(
            endpoint,
            st,
            action="start_max",
            message=message,
            note=f"Loaded {req.get('weight_path') or req.get('checkpoint')}",
        )
    except MatgramError as exc:
        return _err(endpoint, exc, message)


async def load_weights(request: Request) -> JSONResponse:
    """Connect a weight_path or finetune checkpoint+task to MAX."""
    body = (
        await request.json()
        if request.headers.get("content-type", "").startswith("application/json")
        else {}
    )
    message = body.get("message") if isinstance(body, dict) else None
    endpoint = "settings_load_weights"
    try:
        req = parse_load_request(message)
        if "weight_path" not in req and "checkpoint" not in req:
            req["weight_path"] = DEFAULT_WEIGHT_PATH
        if "checkpoint" in req and not req.get("task"):
            # infer task from path segment when possible
            ck = str(req["checkpoint"])
            for t in ("esol", "bbbp", "lipo"):
                if f"/{t}/" in ck or ck.endswith(f"/{t}"):
                    req["task"] = t
                    break
            if not req.get("task"):
                raise MatgramError(
                    "checkpoint requires task=esol|bbbp|lipo "
                    "(e.g. 'load esol' or 'checkpoint=... task=esol')"
                )
        st = matgram_load(**{k: v for k, v in req.items() if v is not None})
        return _ok(
            endpoint,
            st,
            action="load_weights",
            message=message,
            note=f"Connected {req.get('weight_path') or req.get('checkpoint')} "
            f"(task={req.get('task')})",
        )
    except MatgramError as exc:
        return _err(endpoint, exc, message)


async def stop_max(request: Request) -> JSONResponse:
    body = (
        await request.json()
        if request.headers.get("content-type", "").startswith("application/json")
        else {}
    )
    message = body.get("message") if isinstance(body, dict) else None
    endpoint = "settings_stop_max"
    try:
        st = matgram_stop()
        return _ok(endpoint, st, action="stop_max", message=message, note="MAX stopped.")
    except MatgramError as exc:
        return _err(endpoint, exc, message)


async def health(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "settings"})


app = make_app(
    [
        Route("/settings/start-max", start_max, methods=["POST"]),
        Route("/settings/load-weights", load_weights, methods=["POST"]),
        Route("/settings/stop-max", stop_max, methods=["POST"]),
        Route("/health", health, methods=["GET"]),
    ]
)


if __name__ == "__main__":
    print(f"Serving settings on http://127.0.0.1:{PORT}/settings/*")
    uvicorn.run(app, host="127.0.0.1", port=PORT)
