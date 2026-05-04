FROM node:24-slim AS base
WORKDIR /app

# Expose globally with VITE_ prefix for React to embed during build/dev
ENV VITE_APP_VERSION="2.0.1"
ARG VITE_APP_RELEASE_DATE="Unreleased"
ENV VITE_APP_RELEASE_DATE=${VITE_APP_RELEASE_DATE}
ARG VITE_APP_TERMS=""
ENV VITE_APP_TERMS=${VITE_APP_TERMS}

COPY apps/openregex-frontend/package*.json ./

# --- DEVELOPMENT STAGE ---
FROM base AS development
RUN npm install
# Code is mounted at runtime
WORKDIR /app/apps/openregex-frontend
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5000"]

# --- BUILDER STAGE (For Production) ---
FROM base AS builder
RUN npm install
COPY apps/openregex-frontend/ ./apps/openregex-frontend/
COPY TERMS.md* ./apps/openregex-frontend/public/TERMS.md
COPY NOTICE* ./apps/openregex-frontend/public/NOTICE
COPY LICENSE* ./apps/openregex-frontend/public/LICENSE
COPY THIRD-PARTY-LICENSES.md* ./apps/openregex-frontend/public/THIRD-PARTY-LICENSES.md

WORKDIR /app/apps/openregex-frontend
RUN npm run build

# --- PRODUCTION STAGE ---
FROM nginx:alpine AS production
COPY apps/openregex-frontend/nginx.conf /etc/nginx/conf.d/default.conf
RUN sed -i 's/listen 80;/listen 5000;/g' /etc/nginx/conf.d/default.conf
COPY --from=builder /app/apps/openregex-frontend/dist /usr/share/nginx/html

EXPOSE 5000
CMD ["nginx", "-g", "daemon off;"]