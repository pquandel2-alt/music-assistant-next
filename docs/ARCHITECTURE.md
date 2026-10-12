# Architecture

## Runtime

```text
Home Assistant Supervisor / Ingress
  -> Music Assistant Next image
     -> Music Assistant server (authentication, library, providers, players, queues)
        -> connected music providers (Spotify included)
        -> recommendation plugins (library, Last.fm, MusicBrainz, provider-native)
     -> music_assistant_frontend.where()
        -> bundled Music Assistant Next Vue application
```

There is no iframe, second dashboard, browser-side Spotify client, or parallel audio engine.
`server/music_assistant/controllers/webserver/controller.py` imports
`music_assistant_frontend.where`; the Next wheel deliberately retains that Python module name.
Its distribution name is `music-assistant-next-frontend`, and the server depends on that exact
package, preventing PyPI's upstream frontend from replacing the forked assets.

## Artist discovery request

```text
ArtistDiscovery.vue
  -> music/discovery/artists (LIBRARY_READ)
     -> current user's visible music-provider set
     -> query? provider catalog search
        : advertised new-release browse folders + external recommendation rows
     -> availability/source filter
     -> provider-mapping deduplication
     -> bounded candidate pool
     -> user-scoped cursor session
  -> native media cards
  -> existing artist detail / favorite / playback / queue commands
```

The cursor contains only a random session key and offset. Provider cursors/tokens never reach the
browser. Sessions expire after ten minutes, are capped at 64, and are bound to the API user.

## Upstream ownership

Playback, streaming, DRM boundaries, queues, grouping, audio processing, authentication,
provider configuration, database schema, and migrations remain upstream-owned. Next changes are
kept in a narrow API/controller extension and frontend views so future upstream synchronization
does not fork business-critical audio code.

## Ports and storage

- Server: `8095` on host networking.
- Supervisor ingress bridge: `8094`.
- Persistent add-on data: Supervisor-managed `/data` for the `music_assistant_next` slug.

The official and Next add-ons cannot safely run together on one host with their default network
configuration. Their writable databases must never be shared concurrently.
