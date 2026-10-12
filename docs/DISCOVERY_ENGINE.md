# Discovery engine

## Existing recommendation pipeline

The pinned server already aggregates Music Assistant library rows and any provider implementing
`ProviderFeature.RECOMMENDATIONS`. Rows and row items are fetched separately, time-bounded, and
filtered through the current user's provider visibility. The frontend lets each user hide,
reorder, refresh, and provider-filter shelves.

Library signals already include recent plays, most-played, favorites, recently added, forgotten,
rarely played, and in-progress content. Optional Last.fm and MusicBrainz providers add external
similarity, genre, release, and chart candidates. Items are resolved back to playable connected
providers before presentation.

## Next artist candidate generator

`music/discovery/artists` adds an explicit catalog surface:

1. Resolve only music sources visible to the current authenticated user.
2. With a query, call the existing cached multi-provider search for artists, explicitly excluding
   the library target.
3. Without a query, inspect provider browse roots and follow only folders advertised as new
   releases; extract their album artists.
4. Add artists present in a bounded set of enabled external recommendation rows.
5. Apply an optional provider filter.
6. Remove library items and deduplicate by `(provider_domain, provider_item_id)`.
7. Cap the pool, store it in a user-scoped short-lived session, and return cursor pages.

There are no invented popularity scores and no example-artist fallback. Empty sources produce an
honest empty state. Provider search/browse caching and throttling remain inside the provider.

## Privacy and failure isolation

The endpoint requires `LIBRARY_READ`. Provider selection already honors per-user sharing rules.
Cursor sessions store the user ID and cannot be continued by another user. One slow or failing
browse provider is isolated by a timeout; external recommendation rows use the upstream per-row
error boundary. Stale frontend responses are discarded by a monotonically increasing request ID.

## Future ranking work

The endpoint currently preserves source relevance/order and prioritizes real new-release and
recommendation data. A later version may add an explicit weighted diversity ranker and persisted
negative-feedback controls. That work must use user-scoped play/favorite records, document each
weight, and never synthesize popularity.
