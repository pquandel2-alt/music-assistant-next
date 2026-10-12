#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(cd "$(dirname "$0")/.." && pwd)
export NODE_OPTIONS="${NODE_OPTIONS:---max-old-space-size=4096}"

cd "$repo_dir/frontend"
pnpm lint:check
pnpm test:run
pnpm build

cd "$repo_dir/server"
python -m compileall -q music_assistant/controllers/music/recommendations/controller.py
pytest \
  tests/controllers/music/test_recommendations.py \
  tests/controllers/music/test_recommendations_items.py \
  tests/controllers/music/test_recommendations_timeouts.py

cd "$repo_dir"
python - <<'PY'
import json
from pathlib import Path

json.loads(Path("repository.json").read_text())
json.loads(Path("frontend/src/translations/en.json").read_text())
json.loads(Path("frontend/src/translations/de.json").read_text())
print("JSON manifests are valid")
PY
