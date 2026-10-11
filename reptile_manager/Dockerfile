# ── Stage 1: Build Vue frontend ───────────────────────────────────────────────
FROM node:20-alpine AS frontend-build

WORKDIR /build
COPY frontend/package*.json ./
RUN npm install --prefer-offline

COPY frontend/ .
# Vite reads the app version from ../config.yaml (same layout as the repo)
COPY config.yaml ../config.yaml

# Relative API URL — nginx proxies /api/ internally
ENV VITE_API_URL=""
RUN npm run build


# ── Stage 2: Runtime (Python + nginx + supervisord) ───────────────────────────
FROM python:3.12-slim

# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    jq \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python backend dependencies (SQLite — no psycopg2 needed)
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Backend source
COPY backend/app ./app
# Backend reads the app version from /app/config.yaml
COPY config.yaml ./config.yaml

# Frontend build output → nginx webroot
COPY --from=frontend-build /build/dist /var/www/html

# Add-on config files
COPY nginx.conf        /etc/nginx/conf.d/default.conf
COPY supervisord.conf  /etc/supervisor/conf.d/supervisord.conf
COPY run.sh            /run.sh
RUN chmod +x /run.sh

# Remove default nginx site
RUN rm -f /etc/nginx/sites-enabled/default

EXPOSE 8099

CMD ["/run.sh"]
