# Local UI + in-process controller (stable Docker deploy on this host).
# Use with deploy/ui/docker-compose.yml (network_mode: host so 127.0.0.1
# router URLs reach AGE / matgram / query_agent / analysts on the host).
#
# Railway edge proxy stays at repo-root Dockerfile (Caddy).

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PIXI_HOME=/opt/pixi \
    PATH=/opt/pixi/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=4546 \
    UVICORN_RELOAD=0 \
    JWT_AUTH_DISABLED=true

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://pixi.sh/install.sh | bash

WORKDIR /app

COPY pixi.toml pixi.lock ./
RUN pixi install --locked

COPY pyproject.toml README.md ./
COPY string_therapy_for_material_science ./string_therapy_for_material_science
COPY routes ./routes
COPY ui ./ui

RUN pixi run python -m pip install -e .

EXPOSE 4546

HEALTHCHECK --interval=15s --timeout=5s --start-period=60s --retries=5 \
  CMD curl -fsS http://127.0.0.1:4546/health || exit 1

CMD ["pixi", "run", "python", "-m", "string_therapy_for_material_science.main01"]
