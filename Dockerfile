ARG PYTHON_VERSION="3.12"
ARG UV_VERSION="0.7"


FROM ghcr.io/astral-sh/uv:${UV_VERSION}-python${PYTHON_VERSION}-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
ENV VIRTUAL_ENV=/venv

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --active
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=.,target=. \
    uv sync --frozen --no-editable --no-dev --active


FROM docker.io/python:${PYTHON_VERSION}-slim-bookworm

EXPOSE 8000

RUN groupadd -r app && \
    useradd -r -g app -d /app -s /sbin/nologin app && \
    mkdir -p /app && \
    chown -R app:app /app
USER app

WORKDIR /app

COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

CMD ["app", "run", "-h", "0.0.0.0"]
