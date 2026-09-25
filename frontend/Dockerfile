# Build context: repository root (tech.md, 16.5).
FROM node:24-slim AS build
RUN corepack enable
WORKDIR /app
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml frontend/.npmrc ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build

FROM node:24-slim
ENV NODE_ENV=production PORT=3000
WORKDIR /app
# Everything is a devDependency, so the Vite server build is self-contained.
COPY --from=build /app/build ./build
COPY --from=build /app/package.json ./
USER node
EXPOSE 3000
CMD ["node", "build"]
