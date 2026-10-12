# Development

## Prerequisites

- Node 22+ and pnpm 11.8.0.
- Python 3.14 and `uv` for the current server branch.
- ffmpeg 7+ for a local server.
- Docker Buildx for release images.

## Frontend

```bash
cd frontend
export NODE_OPTIONS=--max-old-space-size=4096
pnpm install --frozen-lockfile
pnpm lint:check
pnpm test:run
pnpm build
python -m build --wheel
```

The complete Vue typecheck and Vite bundle exceed Node's default 2 GB heap on the pinned
frontend; the 4 GB limit above is also set in Docker and CI.

For live UI development run `pnpm dev` and connect it to an isolated server. Do not point
development code at a production database.

## Server

```bash
cd server
scripts/setup.sh
source .venv/bin/activate
pytest tests/controllers/music/test_recommendations.py
pre-commit run --all-files
```

The server currently requires Python 3.14. Do not relax that pin locally. The discovery endpoint
must continue to use provider APIs, their cache/throttler, current-user filtering, and existing
media objects. It must never return streaming audio URLs.

## Integrated image

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --build-arg MASS_VERSION=2.11.0-next.2 \
  -f Dockerfile.next .
```

The Dockerfile builds frontend assets, packages them as
`music-assistant-next-frontend`, builds the server wheel, installs both, downloads/verifies the
same AirPlay CLI artifact as upstream, and uses the upstream runtime base image.

Never place Spotify tokens, Supervisor tokens, registry credentials, databases, backups, or
`.env` files in the repository.
