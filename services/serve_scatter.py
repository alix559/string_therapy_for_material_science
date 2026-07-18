"""Placeholder solubility scatter visualization endpoint."""

from __future__ import annotations

import uvicorn
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from cors_app import make_app

PORT = 8004
PATH = '/data-visualizations/scatter'


async def scatter(request: Request) -> JSONResponse:
    body = await request.json() if request.headers.get('content-type', '').startswith('application/json') else {}
    return JSONResponse(
        {
            'status': 'ok',
            'endpoint': 'solubility_scatter',
            'visualization': 'scatter',
            'message': body.get('message'),
            'placeholder': True,
            'plot': {
                'type': 'scatter',
                'x_label': 'temperature_C',
                'y_label': 'solubility_g_per_L',
                'points': [
                    {'x': 20, 'y': 12.4},
                    {'x': 40, 'y': 28.1},
                    {'x': 60, 'y': 51.0},
                ],
            },
        }
    )


async def health(_: Request) -> JSONResponse:
    return JSONResponse({'status': 'ok', 'service': 'solubility_scatter'})


app = make_app(
    [
        Route(PATH, scatter, methods=['POST']),
        Route('/health', health, methods=['GET']),
    ]
)


if __name__ == '__main__':
    print(f'Serving placeholder scatter viz on http://127.0.0.1:{PORT}{PATH}')
    uvicorn.run(app, host='127.0.0.1', port=PORT)
