# Spotify capabilities and limitations

Verified against the pinned provider and Spotify's public developer documentation on
2026-10-11.

## Directly supported through Music Assistant

- Keyword catalog search for artists, albums, tracks, playlists, podcasts, and audiobooks where
  Spotify returns those types.
- Artist, album, top-track, release, library and playlist operations exposed by the provider.
- Playback through Music Assistant's Spotify backend; no audio URL is exposed to the browser.
- Curated new-release metadata and category browsing while Spotify continues to serve those
  endpoints to the session used by the upstream provider.
- Provider caching, retry/backoff, market availability and account authorization in the server.

## Important current constraints

- Spotify has no API that enumerates every artist alphabetically. Next therefore offers search,
  genres/categories, new-release artists and recommendation-driven discovery, not a fictitious
  complete catalog listing.
- The current public Search reference caps results at 10 per requested media type. Search is a
  relevance result, not a browse-all cursor.
- Spotify currently marks `GET /browse/new-releases` as deprecated. The pinned provider caches it
  for 24 hours and treats a missing endpoint as an empty list. The explorer therefore degrades to
  search and enabled recommendation providers.
- Spotify's Web API rate limit uses a rolling 30-second window and returns HTTP 429. Development
  mode also has a separate quota; from July 2026 that quota is shared per developer account and
  exposes `reason: QUOTA_EXCEEDED`.
- Development-mode access requires Premium and a small allowlist. Extended quota access is not a
  realistic assumption for a personal fork and is not required by Next.
- Spotify does not guarantee the official app's personal home feed, charts, proprietary ranking,
  or complete related-artist graph through public APIs.

Official references:

- https://developer.spotify.com/documentation/web-api/reference/search
- https://developer.spotify.com/documentation/web-api/reference/get-new-releases
- https://developer.spotify.com/documentation/web-api/concepts/rate-limits
- https://developer.spotify.com/documentation/web-api/concepts/quota-modes
- https://developer.spotify.com/blog/2026-07-23-web-api-quota-updates

No scraping, private endpoint, DRM bypass, subscription bypass, audio export, or client-side token
use is included.
