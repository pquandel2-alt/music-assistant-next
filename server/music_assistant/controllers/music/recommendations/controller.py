"""Recommendations subcontroller: aggregates library + provider recommendation rows."""

from __future__ import annotations

import asyncio
import logging
import secrets
import time
from collections import OrderedDict
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import zip_longest
from typing import TYPE_CHECKING, TypedDict, cast

from music_assistant_models.auth import Scope
from music_assistant_models.enums import MediaType, ProviderFeature
from music_assistant_models.media_items import (
    Album,
    Artist,
    BrowseFolder,
    ItemMapping,
    Track,
    UniqueList,
)

from music_assistant.constants import MASS_LOGGER_NAME
from music_assistant.controllers.music.constants import (
    RECOMMENDATIONS_ITEMS_TIMEOUT,
    RECOMMENDATIONS_ROWS_TIMEOUT,
)
from music_assistant.controllers.webserver.helpers.auth_middleware import get_current_user
from music_assistant.providers.recommendations import LibraryRecommendationsProvider

if TYPE_CHECKING:
    from music_assistant_models.media_items import (
        MediaItemType,
        RecommendationFolder,
    )

    from music_assistant.mass import MusicAssistant
    from music_assistant.models.media_capabilities import RecommendationsMixin
    from music_assistant.models.music_provider import MusicProvider


DISCOVERY_SESSION_TTL = 10 * 60
DISCOVERY_SESSION_LIMIT = 64
DISCOVERY_CANDIDATE_LIMIT = 200
# Spotify's current Web API caps search results at ten per media type. Other providers may
# allow more, but this common denominator prevents a catalog search from failing as a whole.
DISCOVERY_SEARCH_LIMIT = 10
DISCOVERY_PROVIDER_CONCURRENCY = 4
DISCOVERY_PROVIDER_TIMEOUT = 10


@dataclass(slots=True)
class _ArtistDiscoverySession:
    """Hold one stable, user-scoped artist discovery result set."""

    user_id: str
    created_at: float
    items: list[Artist | ItemMapping]
    source_count: int


class DiscoveryArtistPage(TypedDict):
    """Serialized response for the catalog artist explorer."""

    items: list[Artist | ItemMapping]
    next_cursor: str | None
    source_count: int
    total: int


class RecommendationsController:
    """Serves the recommendations API: default library rows plus provider rows."""

    def __init__(self, mass: MusicAssistant) -> None:
        """Initialize the controller and register its api commands."""
        self.mass = mass
        self.logger = logging.getLogger(f"{MASS_LOGGER_NAME}.music.recommendations")
        self.mass.register_api_command(
            "music/recommendations",
            self.get_recommendations,
            required_scope=Scope.LIBRARY_READ,
        )
        self.mass.register_api_command(
            "music/recommendations/items",
            self.get_recommendation_items,
            required_scope=Scope.LIBRARY_READ,
        )
        self.mass.register_api_command(
            "music/discovery/artists",
            self.get_discovery_artists,
            required_scope=Scope.LIBRARY_READ,
        )
        self._artist_discovery_sessions: OrderedDict[str, _ArtistDiscoverySession] = OrderedDict()

    async def get_recommendations(self) -> list[RecommendationFolder]:
        """Get all available recommendation rows (library + providers, interleaved), without items."""
        providers = self.mass.music._apply_user_provider_filter(
            self.mass.get_providers_supporting_feature(ProviderFeature.RECOMMENDATIONS)
        )
        rows_per_source: list[list[RecommendationFolder]] = [
            *await asyncio.gather(
                *[
                    self._provider_rows(cast("RecommendationsMixin", provider))
                    for provider in providers
                ]
            ),
        ]
        # interleave: one folder per source per pass, preserving each source's ordering
        return [item for sublist in zip_longest(*rows_per_source) for item in sublist if item]

    async def get_recommendation_items(
        self, provider: str, item_id: str, providers: list[str] | None = None
    ) -> UniqueList[MediaItemType | ItemMapping | BrowseFolder]:
        """
        Get the items for a single recommendation row.

        :param provider: The provider instance id owning the row.
        :param item_id: The item_id of the row, as returned by the recommendations listing.
        :param providers: Restrict items to those reachable through one of these provider
            instance ids (OR semantics). Only honored on rows that advertise
            `supports_provider_filter`; ignored on other rows for backwards compatibility.
        """
        try:
            prov = self.mass.get_provider(provider)
            # re-apply the user provider filter the rows listing applies, so a user
            # can not fetch items from a music provider an admin has restricted them from
            if prov is None or not self.mass.music._apply_user_provider_filter([prov]):
                return UniqueList()
            if ProviderFeature.RECOMMENDATIONS not in prov.supported_features:
                # keep the base-model guarantee that this method is only called for
                # providers declaring the feature, matching the rows listing
                return UniqueList()
            async with asyncio.timeout(RECOMMENDATIONS_ITEMS_TIMEOUT):
                if isinstance(prov, LibraryRecommendationsProvider):
                    return await prov.get_recommendation_items(item_id, providers=providers)
                # external provider rows don't support provider filtering: their SPI
                # signature is unchanged, so `providers` is silently ignored here
                return await cast("RecommendationsMixin", prov).get_recommendation_items(item_id)
        except TimeoutError:
            self.logger.warning(
                "Timeout while fetching recommendation items for %s/%s; skipping",
                provider,
                item_id,
            )
            return UniqueList()
        except Exception as err:
            self.logger.warning(
                "Error while fetching recommendation items for %s/%s: %s",
                provider,
                item_id,
                str(err),
                exc_info=err if self.logger.isEnabledFor(logging.DEBUG) else None,
            )
            return UniqueList()

    async def get_discovery_artists(
        self,
        query: str | None = None,
        provider: str | None = None,
        cursor: str | None = None,
        limit: int = 24,
    ) -> DiscoveryArtistPage:
        """
        Return a stable page of playable catalog artists outside the library.

        The endpoint does not pretend that a provider exposes a global artist directory.
        It builds candidates from provider search, curated new-release shelves and enabled
        recommendation providers, then filters, de-duplicates and paginates that real catalog
        data. Cursors are short-lived and scoped to the signed-in user.

        :param query: Optional catalog search query.
        :param provider: Optional provider instance id or domain.
        :param cursor: Opaque cursor returned by a previous call.
        :param limit: Page size, clamped to 12-48 items.
        """
        page_size = max(12, min(limit, 48))
        user_id = user.user_id if (user := get_current_user()) else "anonymous"
        self._prune_artist_discovery_sessions()

        session_id, offset = self._parse_discovery_cursor(cursor)
        session = self._artist_discovery_sessions.get(session_id) if session_id else None
        if session is None or session.user_id != user_id:
            items, source_count = await self._build_artist_candidates(query, provider)
            session_id = secrets.token_urlsafe(12)
            session = _ArtistDiscoverySession(user_id, time.monotonic(), items, source_count)
            self._artist_discovery_sessions[session_id] = session
            self._artist_discovery_sessions.move_to_end(session_id)
            offset = 0

        end = min(offset + page_size, len(session.items))
        next_cursor = f"{session_id}:{end}" if end < len(session.items) else None
        return {
            "items": session.items[offset:end],
            "next_cursor": next_cursor,
            "source_count": session.source_count,
            "total": len(session.items),
        }

    async def _provider_rows(self, provider: RecommendationsMixin) -> list[RecommendationFolder]:
        """Return a provider's recommendation rows, or an empty list if it times out or raises."""
        try:
            async with asyncio.timeout(RECOMMENDATIONS_ROWS_TIMEOUT):
                return await provider.get_recommendations()
        except TimeoutError:
            self.logger.warning(
                "Timeout while fetching recommendation rows from %s; skipping for this request",
                provider.name,
            )
            return []
        except Exception as err:
            self.logger.warning(
                "Error while fetching recommendation rows from %s: %s",
                provider.name,
                str(err),
                exc_info=err if self.logger.isEnabledFor(logging.DEBUG) else None,
            )
            return []

    async def _build_artist_candidates(
        self, query: str | None, provider_filter: str | None
    ) -> tuple[list[Artist | ItemMapping], int]:
        """Build a bounded candidate pool from the caller's visible catalog sources."""
        providers = self._discovery_music_providers(provider_filter)
        if query and query.strip():
            result = await self.mass.music.search(
                query.strip(),
                media_types=[MediaType.ARTIST],
                limit=DISCOVERY_SEARCH_LIMIT,
                providers=[provider.instance_id for provider in providers],
            )
            return self._dedupe_external_artists(result.artists), len(providers)

        semaphore = asyncio.Semaphore(DISCOVERY_PROVIDER_CONCURRENCY)

        async def provider_candidates(
            music_provider: MusicProvider,
        ) -> list[Artist | ItemMapping]:
            async with semaphore:
                try:
                    async with asyncio.timeout(DISCOVERY_PROVIDER_TIMEOUT):
                        return await self._artists_from_provider_browse(music_provider)
                except Exception as err:
                    self.logger.debug(
                        "Catalog discovery failed for %s: %s",
                        music_provider.name,
                        str(err),
                    )
                    return []

        per_provider = await asyncio.gather(*(provider_candidates(item) for item in providers))
        recommendation_artists = await self._artists_from_recommendations(provider_filter)
        candidates = [item for group in per_provider for item in group]
        candidates.extend(recommendation_artists)
        return self._dedupe_external_artists(candidates), len(providers)

    def _discovery_music_providers(self, provider_filter: str | None) -> list[MusicProvider]:
        """Return catalog providers visible to the current user and optional source filter."""
        providers = self.mass.music.providers
        if not provider_filter:
            return providers
        return [
            provider
            for provider in providers
            if provider_filter in {provider.instance_id, provider.domain}
        ]

    async def _artists_from_provider_browse(
        self, provider: MusicProvider
    ) -> list[Artist | ItemMapping]:
        """Extract artists from a provider's advertised new-release browse shelf."""
        if ProviderFeature.BROWSE not in provider.supported_features:
            return []
        root = await provider.browse(f"{provider.instance_id}://")
        new_release_folders = [
            item
            for item in root
            if isinstance(item, BrowseFolder)
            and (item.translation_key == "new_releases" or "new-release" in item.item_id.casefold())
        ]
        artists: list[Artist | ItemMapping] = []
        for folder in new_release_folders[:1]:
            for item in await provider.browse(folder.path):
                artists.extend(self._artists_from_media_item(item))
        return artists

    async def _artists_from_recommendations(
        self, provider_filter: str | None
    ) -> list[Artist | ItemMapping]:
        """Extract available artists from a bounded set of external recommendation rows."""
        folders = [
            folder
            for folder in await self.get_recommendations()
            if folder.provider != "recommendations"
        ][:8]
        if not folders:
            return []
        results = await asyncio.gather(
            *(self.get_recommendation_items(folder.provider, folder.item_id) for folder in folders)
        )
        artists = [
            artist
            for items in results
            for item in items
            for artist in self._artists_from_media_item(item)
        ]
        if not provider_filter:
            return artists
        return [
            artist
            for artist in artists
            if artist.provider == provider_filter
            or any(
                provider_filter in {mapping.provider_instance, mapping.provider_domain}
                for mapping in getattr(artist, "provider_mappings", ())
            )
        ]

    @staticmethod
    def _artists_from_media_item(item: object) -> list[Artist | ItemMapping]:
        """Return artists represented by an artist, album or track item."""
        if isinstance(item, Artist):
            return [item]
        if isinstance(item, ItemMapping) and item.media_type == MediaType.ARTIST:
            return [item]
        if isinstance(item, (Album, Track)):
            return list(item.artists)
        return []

    @staticmethod
    def _dedupe_external_artists(
        artists: Sequence[Artist | ItemMapping],
    ) -> list[Artist | ItemMapping]:
        """Keep stable first-seen catalog artists and remove library/URI duplicates."""
        result: list[Artist | ItemMapping] = []
        seen: set[str] = set()
        for artist in artists:
            if artist.provider == "library":
                continue
            keys = {
                f"{mapping.provider_domain or mapping.provider_instance}:{mapping.item_id}"
                for mapping in getattr(artist, "provider_mappings", ())
            } or {artist.uri or f"{artist.provider}:{artist.item_id}"}
            if seen.intersection(keys):
                continue
            seen.update(keys)
            result.append(artist)
            if len(result) >= DISCOVERY_CANDIDATE_LIMIT:
                break
        return result

    def _prune_artist_discovery_sessions(self) -> None:
        """Drop expired sessions and keep the in-memory cache bounded."""
        oldest_allowed = time.monotonic() - DISCOVERY_SESSION_TTL
        for key, session in list(self._artist_discovery_sessions.items()):
            if session.created_at < oldest_allowed:
                self._artist_discovery_sessions.pop(key, None)
        while len(self._artist_discovery_sessions) >= DISCOVERY_SESSION_LIMIT:
            self._artist_discovery_sessions.popitem(last=False)

    @staticmethod
    def _parse_discovery_cursor(cursor: str | None) -> tuple[str | None, int]:
        """Parse an opaque discovery cursor without exposing provider pagination tokens."""
        if not cursor or ":" not in cursor:
            return None, 0
        session_id, raw_offset = cursor.rsplit(":", 1)
        try:
            offset = max(0, int(raw_offset))
        except ValueError:
            return None, 0
        return session_id or None, offset
