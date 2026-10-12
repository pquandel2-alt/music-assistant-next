# Music Assistant Next

Music Assistant Next is a discovery-first fork of Music Assistant delivered as one server,
one bundled Vue frontend, and one Home Assistant Supervisor add-on. It keeps the upstream
playback, queue, player, provider, authentication, and library implementations.

This repository is an integrated source snapshot pinned in [`UPSTREAM.lock`](UPSTREAM.lock).
The untouched clones used for verification are intentionally ignored by Git.

## Implemented in this revision

- Responsive Music Assistant Next identity layered onto the upstream dark-first UI.
- A real Discover hero linked to catalog discovery and the existing configurable,
  provider-backed recommendation shelves.
- An integrated artist hub that separates **My artists** from **Discover artists**.
- Server-side `music/discovery/artists` API using connected-provider search, advertised
  new-release browse shelves, and enabled external recommendation providers.
- User-scoped, ten-minute cursor sessions; stable pagination; bounded memory, concurrency,
  and request duration; provider-identity deduplication; no hard-coded artists.
- Direct reuse of Music Assistant artist detail, favorite, context-menu, queue, and playback
  flows for discovered catalog items.
- A renamed Python frontend distribution so the upstream frontend dependency cannot overwrite
  the customized bundle during image creation.
- amd64/arm64 image workflow and a distinct `music_assistant_next` Supervisor add-on definition.
- Migration, rollback, architecture, Spotify-limit, development, test, and release guidance.

## Honest scope

This revision is a production-oriented vertical slice, not a claim that every item in the
master specification is newly reimplemented. A large part of that specification is already
present in the pinned upstream: responsive sidebar/bottom navigation, mini/fullscreen player,
queue, global progressive search, album/track/artist details, user-scoped favorites and play
history, configurable Discover rows, Last.fm/MusicBrainz recommendations, provider caching,
and player management. Those capabilities are preserved and documented rather than duplicated.

No production Home Assistant installation has been modified. No image has been published from
this environment. Replace `REPLACE_WITH_OWNER`, publish the image, and perform the documented
backup-first migration before installing.

## Layout

- `frontend/` – Vue 3, TypeScript, Vite, Tailwind and shadcn-vue frontend.
- `server/` – asynchronous Python server and catalog discovery endpoint.
- `models/` – pinned shared model source for compatibility/reference.
- `repository.json` and `music_assistant_next/` – directly installable Supervisor repository.
- `Dockerfile.next` – integrated frontend-wheel + server-wheel multi-arch image.
- `docs/` – operational and technical documentation.

Start with [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) and
[`docs/ADDON_INSTALLATION.md`](docs/ADDON_INSTALLATION.md).
