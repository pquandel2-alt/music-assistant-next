# Migration

No automated production migration is executed by this repository.

## Safe procedure

1. Update the official add-on to a schema-compatible version if the release notes require it.
2. Stop playback and wait for library/provider background tasks to finish.
3. Create and download a full Home Assistant backup containing the official add-on data.
4. Stop the official add-on and disable watchdog/automatic start.
5. Install Next but keep it stopped.
6. Restore a **copy** of the official add-on data into the Next add-on's Supervisor-managed data
   location using a documented Supervisor backup/restore path. Never bind both slugs to one live
   `/data` directory.
7. Start Next alone. Inspect the startup log, schema migrations, provider status, player list,
   playlists and library counts.
8. Spotify refresh tokens are encrypted/configuration-bound. If the copied configuration cannot
   be decrypted or the provider requests reauthentication, perform a new OAuth login; never copy
   tokens through logs or source files.
9. Test search, a non-library artist, one album, queue insertion and actual playback on a
   non-critical player before accepting the migration.

## Preserved when the complete data directory is compatible

Library database, playlists, play history, provider/player configuration, user preferences and
audio settings live under add-on data and should be retained by a compatible full-directory copy.
The exact outcome depends on the upstream server schema at the source version.

Do not migrate forward if the Next server would apply an irreversible schema change and you have
not verified rollback against a restored copy.
