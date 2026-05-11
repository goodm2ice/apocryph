#!/bin/sh
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8080}
uv run uvicorn main:app --host "$HOST" --port "$PORT"
