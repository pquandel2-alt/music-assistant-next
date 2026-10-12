# Rollback

1. Stop Music Assistant Next. Do not let it write further data.
2. Keep its data directory for diagnosis; do not copy a migrated database backward over the
   official installation.
3. Restore the pre-migration Home Assistant backup of the official add-on and its data.
4. Start only the official add-on and verify logs, library, providers, players and playback.
5. Re-enable watchdog/automatic start after verification.

If the Next database was upgraded by a newer upstream schema, only a backup made before that
upgrade is a supported rollback source. Uninstalling an add-on image does not reverse database
migrations. Never run both versions against the same writable database.
