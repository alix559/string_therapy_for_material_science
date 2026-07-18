"""Placeholder solubility timeseries visualization endpoint."""

from __future__ import annotations

import uvicorn
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from cors_app import make_app

PORT = 8003
PATH = '/data-visualizations/timeseries'


async def timeseries(request: Request) -> JSONResponse:
    body = await request.json() if request.headers.get('content-type', '').startswith('application/json') else {}
    return JSONResponse(
        {
            'status': 'ok',
            'endpoint': 'solubility_timeseries',
            'visualization': 'timeseries',
            'message': body.get('message'),
            'placeholder': True,
            'plot': {
                'type': 'timeseries',
                'x_label': 'time_min',
                'y_label': 'solubility_g_per_L',
                'series': [
                    {'t': 0, 'y': 10.0},
                    {'t': 15, 'y': 18.2},
                    {'t': 30, 'y': 27.5},
                    {'t': 60, 'y': 41.0},
                ],
            },
        }
    )


async def health(_: Request) -> JSONResponse:
    return JSONResponse({'status': 'ok', 'service': 'solubility_timeseries'})


app = make_app(
    [
        Route(PATH, timeseries, methods=['POST']),
        Route('/health', health, methods=['GET']),
    ]
)


if __name__ == '__main__':
    print(f'Serving placeholder timeseries viz on http://127.0.0.1:{PORT}{PATH}')
    uvicorn.run(app, host='127.0.0.1', port=PORT)
