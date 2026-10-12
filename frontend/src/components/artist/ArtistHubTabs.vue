<template>
  <nav class="artist-hub-tabs" :aria-label="$t('next.artist_sections')">
    <Button
      v-for="tab in tabs"
      :key="tab.route"
      :variant="activeRoute === tab.route ? 'default' : 'ghost'"
      size="sm"
      class="rounded-full px-5"
      :aria-current="activeRoute === tab.route ? 'page' : undefined"
      @click="router.push({ name: tab.route })"
    >
      <component :is="tab.icon" class="size-4" />
      {{ $t(tab.label) }}
    </Button>
  </nav>
</template>

<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Library, Sparkles } from "@lucide/vue";
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const tabs = [
  { route: "artists", label: "next.my_artists", icon: Library },
  {
    route: "artist-discovery",
    label: "next.discover_artists",
    icon: Sparkles,
  },
];

const activeRoute = computed(() => String(route.name));
</script>

<style scoped>
.artist-hub-tabs {
  display: flex;
  gap: 0.35rem;
  padding: 0 1.75rem 1rem;
  overflow-x: auto;
  scrollbar-width: none;
}

.artist-hub-tabs::-webkit-scrollbar {
  display: none;
}

@media (max-width: 600px) {
  .artist-hub-tabs {
    padding-inline: 1rem;
  }
}
</style>
