FROM python:3.13-slim-bookworm AS base
COPY --from=ghcr.io/astral-sh/uv:0.6.2 /uv /uvx /bin/

LABEL maintainer="ERCS Dev"
LABEL org.opencontainers.image.source="https://github.com/your-org/ercs-backend/"

ENV PYTHONUNBUFFERED=1

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

WORKDIR /code

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    apt-get update -y \
    && apt-get install -y --no-install-recommends \
        procps \
        # Required by uv to fetch the banjo-utils git dependency
        git \
    && uv lock --locked --offline \
        && uv sync --frozen --no-install-project --all-groups \
    # git is only needed for the uv git-dependency fetch above; drop it.
    && apt-get remove -y git \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY . /code/
