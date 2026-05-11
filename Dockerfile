FROM node:24-slim AS front_build
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
WORKDIR /app
COPY frontend/package.json frontend/pnpm-lock.yaml .
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile
COPY frontend/* .
RUN pnpm run build

FROM python:3.12-slim
# Установка uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
# Установка зависимостей
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project
COPY backend/* .
# Синхронизация проекта
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked
# Переносим билд фронта
COPY --from=front_build /app/dist ./frontend
ENTRYPOINT ["/bin/sh"]
CMD ["entrypoint.sh"]
