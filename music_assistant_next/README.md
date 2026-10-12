# Music Assistant Next

This Home Assistant add-on runs the Music Assistant Next server and its bundled frontend as one
application. It uses the original Music Assistant playback engine and provider system.

Before publishing a fork, replace `REPLACE_WITH_OWNER` in `config.yaml` and the repository-root
`../repository.json` with the lowercase GitHub Container Registry owner used by the release workflow.

Do not start this add-on while the official Music Assistant add-on is running. Both use host
networking and the same server/ingress ports. Stop the official add-on first, and use a copied
backup for migration; never mount one writable data directory into both containers.

See `docs/ADDON_INSTALLATION.md`, `docs/MIGRATION.md`, and `docs/ROLLBACK.md` in the source
repository before installation.
