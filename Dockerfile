# string_therapy_for_material_science UI + in-process controller (Railway).
# Backends (AGE, matgram, query_agent, analysts) stay on the Hetzner host;
# set ROUTER_DATABASE_URL + seeded router URLs to that public hostname.

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PIXI_HOME=/opt/pixi \
    PATH=/opt/pixi/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
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

EXPOSE 8080

CMD ["pixi", "run", "python", "-m", "string_therapy_for_material_science.main01"]
