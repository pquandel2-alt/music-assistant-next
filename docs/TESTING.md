# Testing

## Automated gates

- Frontend workflow: Oxlint, ESLint, Prettier check, Vitest, Vue TypeScript check, Vite production
  build and Python wheel verification.
- Server workflow: Ruff plus targeted discovery/recommendation Pytest files on the Music
  Assistant base image. The complete upstream pre-commit/MyPy/Pytest suite remains a release gate,
  but is not represented as having run merely because the targeted workflow passed.
- Container: Buildx for linux/amd64 and linux/arm64, followed by manifest publication on releases.
- Add-on: manifest parsing plus placeholder-owner rejection before publication.

## Verification record for this source snapshot

Completed locally on 2026-10-12:

- Vue TypeScript check with Node 22 and a 4 GB heap: passed.
- Vite production/PWA build: passed; the `ArtistDiscovery` route is emitted as a lazy chunk.
- Python frontend wheel build and payload inspection: passed.
- Oxlint, ESLint and the upstream Prettier scope: passed.
- Full Vitest run: 434/435 files and 5273/5275 tests passed with the default five-second timeout.
  Two unchanged `AIRadioView` UI tests timed out at the threshold on this four-core host. Repeating
  that file with a 20-second timeout passed all 16/16 tests. This is recorded as a timing flake, not
  silently counted as a clean default run.
- Ruff check/format for the changed server files: passed.
- MyPy for the changed recommendation controller: passed with the server's own configuration.
- Targeted server recommendation/discovery suites under Python 3.14.2 with all provider
  requirements: 51/51 passed.
- JSON, TOML, Supervisor add-on YAML and GitHub workflow YAML parsing: passed.

Browser tests with a real Spotify account, playback device, Home Assistant Supervisor installation,
multi-architecture container build and data migration require external systems; they remain untested
until performed on an isolated host. Docker/Podman was not installed in the local environment, so
the multi-architecture image is implemented in CI but not claimed as locally built.

## Required integration smoke test

Use an isolated Home Assistant test host or stop the production add-on first.

1. Connect a Spotify provider.
2. Open **Interpreten → Interpreten entdecken**.
3. Verify new-release artists appear without being in the library.
4. Search a known non-library artist and filter to Spotify.
5. Open the artist, load albums/top tracks, favorite it, play a track and add another to queue.
6. Scroll/load another page and ensure there are no duplicates.
7. Change the search quickly and confirm stale results do not replace the latest query.
8. Restart the add-on and repeat search/playback.
9. Force a provider error or disconnect Spotify; the page must show an honest empty/error state
   while library/player UI continues to work.
10. Test iPhone-sized Safari/Home Assistant ingress, safe areas, bottom navigation, mini-player,
    fullscreen player and queue.

Real Spotify and Supervisor integration cannot be represented by hidden mock data. Record the
exact image digest, device architecture, Home Assistant version and provider mode for release
evidence.
