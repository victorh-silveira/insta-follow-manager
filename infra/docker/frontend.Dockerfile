# syntax=docker/dockerfile:1.7

# --- Stage 1: Install Dependencies ---
FROM node:22.14-alpine AS deps

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# --- Stage 2: Build Standalone Bundle ---
FROM node:22.14-alpine AS builder

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ .

ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL} \
    NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# --- Stage 3: Minimal Non-Root Runtime ---
FROM node:22.14-alpine AS runner

ARG APP_UID=10001
ARG APP_GID=10001
ARG IMAGE_VERSION=dev
ARG BUILD_DATE=unknown
ARG VCS_REF=unknown

LABEL org.opencontainers.image.title="insta-follow-manager-frontend" \
      org.opencontainers.image.description="Interface Next.js para triagem de seguidores" \
      org.opencontainers.image.version="${IMAGE_VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}"

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

# hadolint ignore=DL3018
RUN apk add --no-cache tini

RUN addgroup --system --gid "${APP_GID}" nodejs \
    && adduser --system --uid "${APP_UID}" --ingroup nodejs --shell /sbin/nologin nextjs

COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD ["node", "-e", "fetch('http://127.0.0.1:3000').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"]

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "server.js"]
