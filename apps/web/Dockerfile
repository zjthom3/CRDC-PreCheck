# syntax=docker/dockerfile:1.4

FROM node:20-alpine AS base

WORKDIR /workspace

COPY pnpm-workspace.yaml ./
COPY apps/web/package.json apps/web/tsconfig.json apps/web/next-env.d.ts ./apps/web/
COPY apps/web/tailwind.config.ts apps/web/postcss.config.js ./apps/web/
COPY apps/web/app ./apps/web/app
COPY apps/web/vitest.config.ts apps/web/vitest.setup.ts ./apps/web/
COPY apps/web/__tests__ ./apps/web/__tests__

RUN corepack enable && pnpm install --dir apps/web --frozen-lockfile=false

CMD ["pnpm", "--dir", "apps/web", "dev"]
