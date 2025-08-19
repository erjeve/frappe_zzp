#!/bin/bash

# Frappe Docker Compose Script
# Usage: ./compose.sh [up|down]

COMPOSE_FILES="-f compose.yaml -f overrides/compose.mariadb.yaml -f overrides/compose.mariadb-secrets.yaml -f overrides/compose.redis.yaml -f overrides/compose.traefik-ssl.yaml -f overrides/compose.ocr.yaml -f overrides/compose.volumes.yaml -f overrides/compose.n8n.yaml -f overrides/compose.ollama.yaml"

case "$1" in
    up)
        echo "Starting Frappe Docker containers..."
        docker compose $COMPOSE_FILES up -d
        ;;
    down)
        echo "Stopping Frappe Docker containers..."
        docker compose $COMPOSE_FILES down
        ;;
    *)
        echo "Usage: $0 {up|down}"
        echo "  up   - Start all containers in detached mode"
        echo "  down - Stop and remove all containers"
        exit 1
        ;;
esac