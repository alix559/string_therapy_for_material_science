"""Placeholder solubility heatmap visualization endpoint."""

from __future__ import annotations

import uvicorn
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from cors_app import make_app

PORT = 8002
PATH = '/data-visualizations/heatmap'


async def heatmap(request: Request) -> JSONResponse:
    body = await request.json() if request.headers.get('content-type', '').startswith('application/json') else {}
    return JSONResponse(
        {
            'status': 'ok',
            'endpoint': 'solubility_heatmap',
            'visualization': 'heatmap',
            'message': body.get('message'),
            'placeholder': True,
            'plot': {
                'type': 'heatmap',
                'x_label': 'solvent',
                'y_label': 'temperature_C',
                'z_label': 'solubility_g_per_L',
                'x': ['water', 'ethanol', 'acetone'],
                'y': [20, 40, 60],
                'z': [
                    [12.4, 8.1, 5.0],
                    [28.1, 18.4, 11.2],
                    [51.0, 33.7, 19.5],
                ],
            },
        }
    )


async def health(_: Request) -> JSONResponse:
    return JSONResponse({'status': 'ok', 'service': 'solubility_heatmap'})


app = make_app(
    [
        Route(PATH, heatmap, methods=['POST']),
        Route('/health', health, methods=['GET']),
    ]
)


if __name__ == '__main__':
    print(f'Serving placeholder heatmap viz on http://127.0.0.1:{PORT}{PATH}')
    uvicorn.run(app, host='127.0.0.1', port=PORT)
