#!/bin/sh
set -eu

: "${VITE_API_URL?VITE_API_URL is required}"
: "${VITE_WS_URL?VITE_WS_URL is required}"
: "${VITE_GRAFANA_URL:=}"
: "${VITE_QDRANT_URL:=}"
: "${VITE_PROMETHEUS_URL:=}"

mkdir -p /tmp/nginx/client_temp /tmp/nginx/proxy_temp /tmp/nginx/fastcgi_temp /tmp/nginx/uwsgi_temp /tmp/nginx/scgi_temp
envsubst < /usr/share/nginx/html/config.template.js > /usr/share/nginx/html/config.js
