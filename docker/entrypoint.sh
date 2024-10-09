#!/bin/bash

if [[ "${MIGRATION_ENABLED}" == "true" ]]; then
  echo "Running migrations"
  flask db upgrade
fi


echo "Starting server..."
if [[ "${DEBUG}" == "true" ]]; then
    flask run --host=${BIND_ADDRESS:-0.0.0.0} --port=${PORT:-5000} --debug
else
    gunicorn \
        --bind "${BIND_ADDRESS:-0.0.0.0}:${PORT:-5000}" \
        --workers ${SERVER_WORKER_AMOUNT:-10} \
        --worker-class ${SERVER_WORKER_CLASS:-gevent} \
        --timeout ${GUNICORN_TIMEOUT:-200} \
        --preload \
        --log-level debug \
        app:app
fi
