# Home Assistant Supervisor installation

The repository is configured for `pquandel2-alt/music-assistant-next` and its GHCR namespace.

## Publisher steps

1. Enable GitHub Actions packages write permission. The workflow needs only `contents: read` and
   `packages: write`; no Spotify or Home Assistant secret belongs in GitHub.
2. Push a `v2.11.0-next.2` tag or run the container workflow manually.
3. Verify that `ghcr.io/pquandel2-alt/music-assistant-next:2.11.0-next.2` has an amd64 and arm64 manifest
   and is public/readable by Home Assistant.
4. Publish this repository. `repository.json` and `music_assistant_next/config.yaml` are already at
   the Supervisor-required root locations, so the repository URL can be added directly.

## User steps

1. Create a full Home Assistant backup including the existing Music Assistant add-on.
2. Stop the official Music Assistant add-on. Disable watchdog/automatic start temporarily.
3. In **Settings → Apps → App store → Repositories**, add the published add-on repository URL.
4. Refresh the store and install **Music Assistant Next** (`music_assistant_next`).
5. Do not start it until the migration decision in `MIGRATION.md` is complete.
6. Start Next, open its ingress UI, and check logs before enabling automatic start.

## Spotify in the community image

The official Music Assistant image contains a private, separately licensed application-variable
bundle that forks may not redistribute. Music Assistant Next therefore requires a user-owned
Spotify Client ID:

1. Create an app in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Set its redirect URI exactly to `https://music-assistant.io/callback`.
3. Copy the public Client ID into the add-on option **Spotify Client ID**. Do not provide a
   Client Secret.
4. Save the options and restart the add-on before adding Spotify as a music source.

Spotify Premium is required for playback. Keep the Client ID in add-on options; OAuth tokens are
stored encrypted by Music Assistant and must not be copied into the repository.

The add-on uses host networking, server port 8095 and ingress port 8094. Running the official and
Next add-ons simultaneously on the same host is unsupported and likely to collide.
