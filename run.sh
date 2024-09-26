#!/bin/bash

echo "Running migrations..."
alembic upgrade head

echo "Starting server..."
uvicorn main:app --reload --host ${HOST:-0.0.0.0} --port ${PORT:-8000}
