<template>
  <section class="artist-discovery">
    <Toolbar
      :icon="Sparkles"
      :title="$t('next.discover_artists')"
      :subtitle="$t('next.catalog_subtitle')"
    >
      <template #append>
        <Button
          variant="ghost"
          size="icon-lg"
          :aria-label="$t('refresh')"
          :disabled="loading"
          @click="reload"
        >
          <RefreshCw class="size-5" :class="{ 'animate-spin': loading }" />
        </Button>
      </template>
    </Toolbar>

    <ArtistHubTabs />

    <div class="artist-discovery__controls">
      <SearchInput
        v-model="query"
        clearable
        :placeholder="$t('next.search_catalog_artists')"
        :aria-label="$t('next.search_catalog_artists')"
      />
      <div class="artist-discovery__providers" :aria-label="$t('next.sources')">
        <Button
          size="sm"
          :variant="selectedProvider ? 'outline' : 'secondary'"
          class="rounded-full"
          @click="selectedProvider = undefined"
        >
          {{ $t("next.all_sources") }}
        </Button>
        <Button
          v-for="source in catalogProviders"
          :key="source.instance_id"
          size="sm"
          :variant="
            selectedProvider === source.instance_id ? 'secondary' : 'outline'
          "
          class="rounded-full"
          @click="selectedProvider = source.instance_id"
        >
          <ProviderIcon :domain="source.domain" :size="16" />
          {{ providerServiceName(source) }}
        </Button>
      </div>
    </div>

    <div
      v-if="loading && !artists.length"
      class="artist-discovery__grid"
      aria-busy="true"
    >
      <div v-for="index in 12" :key="index" class="artist-skeleton">
        <div class="artist-skeleton__art"></div>
        <div class="artist-skeleton__line"></div>
      </div>
    </div>

    <div v-else-if="error" class="artist-discovery__state" role="alert">
      <CircleAlert class="size-8" />
      <h2>{{ $t("next.catalog_error") }}</h2>
      <p>{{ error }}</p>
      <Button variant="outline" @click="reload">{{
        $t("next.try_again")
      }}</Button>
    </div>

    <div v-else-if="!artists.length" class="artist-discovery__state">
      <SearchX class="size-8" />
      <h2>{{ $t("next.no_catalog_artists") }}</h2>
      <p>{{ $t("next.no_catalog_artists_hint") }}</p>
    </div>

    <template v-else>
      <div class="artist-discovery__summary">
        <span>{{ $t("next.catalog_result_count", { count: total }) }}</span>
        <span v-if="sourceCount">
          {{ $t("next.catalog_source_count", { count: sourceCount }) }}
        </span>
      </div>
      <div class="artist-discovery__grid">
        <EditorialMediaCard
          v-for="artist in artists"
          :key="artist.uri"
          :item="artist"
          fluid
          round
          show-provider-on-cover
        />
      </div>
      <div ref="loadSentinel" class="artist-discovery__sentinel">
        <Button
          v-if="nextCursor"
          variant="outline"
          :disabled="loadingMore"
          class="rounded-full"
          @click="loadMore"
        >
          <LoaderCircle v-if="loadingMore" class="size-4 animate-spin" />
          {{ $t("next.load_more") }}
        </Button>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import ArtistHubTabs from "@/components/artist/ArtistHubTabs.vue";
import EditorialMediaCard from "@/components/discover/EditorialMediaCard.vue";
import ProviderIcon from "@/components/ProviderIcon.vue";
import Toolbar from "@/components/Toolbar.vue";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { providerServiceName } from "@/plugins/api/helpers";
import api from "@/plugins/api";
import {
  type Artist,
  type ItemMapping,
  ProviderFeature,
} from "@/plugins/api/interfaces";
import { useDebounceFn } from "@vueuse/core";
import {
  CircleAlert,
  LoaderCircle,
  RefreshCw,
  SearchX,
  Sparkles,
} from "@lucide/vue";
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

const query = ref("");
const selectedProvider = ref<string>();
const artists = ref<Array<Artist | ItemMapping>>([]);
const nextCursor = ref<string | null>(null);
const total = ref(0);
const sourceCount = ref(0);
const loading = ref(false);
const loadingMore = ref(false);
const error = ref("");
const loadSentinel = ref<HTMLElement>();
let requestId = 0;
let observer: IntersectionObserver | undefined;

const catalogProviders = computed(() =>
  Object.values(api.providers)
    .filter(
      (provider) =>
        provider.available &&
        (provider.supported_features.includes(ProviderFeature.SEARCH) ||
          provider.supported_features.includes(ProviderFeature.BROWSE)),
    )
    .sort((a, b) => a.name.localeCompare(b.name)),
);

const load = async (append = false) => {
  const ownRequestId = ++requestId;
  if (append) loadingMore.value = true;
  else {
    loading.value = true;
    error.value = "";
    nextCursor.value = null;
  }
  try {
    const page = await api.getDiscoveryArtists(
      query.value.trim() || undefined,
      selectedProvider.value,
      append ? nextCursor.value || undefined : undefined,
    );
    if (ownRequestId !== requestId) return;
    const combined = append ? [...artists.value, ...page.items] : page.items;
    artists.value = [
      ...new Map(combined.map((item) => [item.uri, item])).values(),
    ];
    nextCursor.value = page.next_cursor;
    total.value = page.total;
    sourceCount.value = page.source_count;
  } catch (err) {
    if (ownRequestId !== requestId) return;
    error.value = err instanceof Error ? err.message : String(err);
  } finally {
    if (ownRequestId === requestId) {
      loading.value = false;
      loadingMore.value = false;
    }
  }
};

const reload = () => load(false);
const loadMore = () => {
  if (!nextCursor.value || loadingMore.value) return;
  void load(true);
};
const debouncedReload = useDebounceFn(reload, 350);

watch(query, () => debouncedReload());
watch(selectedProvider, reload);

onMounted(() => {
  void reload();
  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry?.isIntersecting) loadMore();
    },
    { rootMargin: "320px" },
  );
  if (loadSentinel.value) observer.observe(loadSentinel.value);
});

watch(loadSentinel, (element, previous) => {
  if (!observer) return;
  if (previous) observer.unobserve(previous);
  if (element) observer.observe(element);
});

onBeforeUnmount(() => {
  requestId += 1;
  observer?.disconnect();
});
</script>

<style scoped>
.artist-discovery {
  min-height: 100%;
  padding-bottom: 4rem;
  background:
    radial-gradient(
      900px 460px at 85% -10%,
      rgba(var(--v-theme-primary), 0.16),
      transparent 65%
    ),
    rgb(var(--v-theme-background));
}

.artist-discovery__controls {
  display: grid;
  gap: 0.9rem;
  padding: 0 1.75rem 1.5rem;
}

.artist-discovery__controls :deep(.search-field) {
  width: min(680px, 100%);
  min-height: 48px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--card) 84%, transparent);
}

.artist-discovery__providers {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding-bottom: 0.25rem;
  scrollbar-width: none;
}

.artist-discovery__providers::-webkit-scrollbar {
  display: none;
}

.artist-discovery__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(154px, 1fr));
  gap: clamp(0.6rem, 1.5vw, 1.25rem);
  padding: 0 1.75rem;
}

.artist-discovery__summary {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0 2.25rem 0.75rem;
  color: rgb(var(--v-theme-on-surface-variant));
  font-size: 0.85rem;
}

.artist-discovery__state {
  display: grid;
  max-width: 560px;
  min-height: 320px;
  margin: 1rem auto;
  place-items: center;
  align-content: center;
  gap: 0.75rem;
  padding: 2rem;
  text-align: center;
  color: rgb(var(--v-theme-on-surface-variant));
}

.artist-discovery__state h2 {
  color: rgb(var(--v-theme-on-background));
  font-size: 1.2rem;
  font-weight: 650;
}

.artist-discovery__sentinel {
  display: flex;
  min-height: 96px;
  align-items: center;
  justify-content: center;
}

.artist-skeleton {
  padding: 0.5rem;
}

.artist-skeleton__art,
.artist-skeleton__line {
  background: rgba(var(--v-theme-on-surface), 0.09);
  animation: artist-pulse 1.6s ease-in-out infinite;
}

.artist-skeleton__art {
  aspect-ratio: 1;
  border-radius: 999px;
}

.artist-skeleton__line {
  width: 72%;
  height: 0.8rem;
  margin: 0.8rem auto 0;
  border-radius: 999px;
}

@keyframes artist-pulse {
  50% {
    opacity: 0.45;
  }
}

@media (prefers-reduced-motion: reduce) {
  .artist-skeleton__art,
  .artist-skeleton__line {
    animation: none;
  }
}

@media (max-width: 600px) {
  .artist-discovery__controls,
  .artist-discovery__grid {
    padding-inline: 1rem;
  }

  .artist-discovery__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.35rem;
  }

  .artist-discovery__summary {
    padding-inline: 1.5rem;
  }
}
</style>
