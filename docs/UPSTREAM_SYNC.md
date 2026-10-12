# Upstream synchronization

The four source roots are pinned in `UPSTREAM.lock`. Server work tracks upstream `dev`; frontend,
models and add-on track `main` at the recorded commits.

1. Fetch the four official repositories and review release notes/security advisories.
2. Update one root at a time. Preserve Music Assistant's usage policy and all provider
   cache/throttle/playback guards.
3. Reapply the small Next delta: distribution rename, discovery controller/API, artist hub,
   branding, Dockerfile and add-on definition.
4. Regenerate/update API interfaces if upstream changes shared models or command schemas.
5. Run frontend lint/tests/build/package verification and targeted server tests, then the full
   upstream suites.
6. Build both architectures and smoke-test an isolated Supervisor instance.
7. Update every SHA/version in `UPSTREAM.lock` in the same reviewed commit.

Never copy a stable server database into a newer development build without a backup and migration
review. Security fixes in upstream take priority over Next styling work.
