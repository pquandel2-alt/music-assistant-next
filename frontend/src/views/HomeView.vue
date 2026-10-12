<template>
  <div class="ed-discover">
    <Toolbar
      :is-discover-page="true"
      :icon="Compass"
      color="background"
      :title="$t('discover')"
    >
      <template #append>
        <Button
          variant="ghost"
          size="icon"
          :class="editMode ? 'text-primary' : 'opacity-80'"
          :title="
            $t(editMode ? 'homescreen_edit_disable' : 'homescreen_edit_enable')
          "
          :aria-label="
            $t(editMode ? 'homescreen_edit_disable' : 'homescreen_edit_enable')
          "
          @click="handleHomescreenEditToggle"
        >
          <SquarePen class="size-5" />
        </Button>
      </template>
    </Toolbar>

    <!-- Provider error warning banner: message on the left, actions pinned
         right so the bar never reads as empty on wide screens. -->
    <Alert
      v-if="hasProviderErrors && showProviderWarning"
      variant="destructive"
      class="provider-alert mx-7 mb-6 mt-4 flex w-auto items-center gap-3 bg-destructive/8 py-3 pl-4 pr-3 [&>svg]:translate-y-0"
    >
      <CircleAlert class="size-5 shrink-0" />
      <AlertDescription class="min-w-0 flex-1 text-destructive">
        {{ $t("settings.provider_requires_attention_detail") }}
      </AlertDescription>
      <Button
        variant="destructive"
        size="sm"
        class="shrink-0"
        @click="navigateToProviders"
      >
        {{ $t("settings.fix_now") }}
        <ArrowRight class="size-3.5" />
      </Button>
      <Button
        variant="ghost"
        size="icon-sm"
        class="shrink-0 text-destructive hover:bg-destructive/10 hover:text-destructive"
        :aria-label="$t('close')"
        @click="showProviderWarning = false"
      >
        <X class="size-4" />
      </Button>
    </Alert>

    <!-- Newly discovered devices that still need setup; Review opens the
         players list filtered down to them. -->
    <Alert
      v-if="
        canConfigurePlayers && showSetupPrompt && playersNeedingSetup.length > 0
      "
      variant="warning"
      class="mx-7 mb-6 mt-4 flex w-auto items-center gap-3 py-3 pl-4 pr-3 [&>svg]:translate-y-0"
    >
      <TriangleAlert class="size-5 shrink-0" />
      <AlertDescription class="min-w-0 flex-1">
        {{
          $t("players_need_setup", playersNeedingSetup.length, {
            named: { count: playersNeedingSetup.length },
          })
        }}
      </AlertDescription>
      <Button
        variant="secondary"
        size="sm"
        class="shrink-0"
        @click="reviewSetupPlayers"
      >
        {{ $t("review") }}
        <ArrowRight class="size-3.5" />
      </Button>
      <Button
        variant="ghost"
        size="icon-sm"
        class="shrink-0"
        :aria-label="$t('close')"
        @click="showSetupPrompt = false"
      >
        <X class="size-4" />
      </Button>
    </Alert>

    <section class="next-discovery-callout">
      <div class="next-discovery-callout__copy">
        <span class="next-discovery-callout__eyebrow">
          <Sparkles class="size-4" />
          {{ $t("next.discovery_eyebrow") }}
        </span>
        <h1>{{ $t("next.discovery_title") }}</h1>
        <p>{{ $t("next.discovery_description") }}</p>
      </div>
      <Button
        size="lg"
        class="next-discovery-callout__action rounded-full"
        @click="router.push({ name: 'artist-discovery' })"
      >
        {{ $t("next.discover_artists") }}
        <ArrowRight class="size-4" />
      </Button>
    </section>

    <HomeWidgetRows :edit-mode="editMode" />

    <!-- Floating exit button while editing the home screen -->
    <Button
      v-if="editMode"
      class="ed-edit-done"
      @click="handleHomescreenEditToggle"
    >
      <Check class="size-4" />
      {{ $t("homescreen_edit_disable") }}
    </Button>
  </div>
</template>

<script setup lang="ts">
import HomeWidgetRows from "@/components/HomeWidgetRows.vue";
import Toolbar from "@/components/Toolbar.vue";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { api } from "@/plugins/api";
import { Scope } from "@/plugins/api/interfaces";
import { authManager } from "@/plugins/auth";
import {
  ArrowRight,
  Check,
  CircleAlert,
  Compass,
  Sparkles,
  SquarePen,
  TriangleAlert,
  X,
} from "@lucide/vue";
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const editMode = ref(false);
const hasProviderErrors = ref(false);
const showProviderWarning = ref(true);
const erroredProviderType = ref<string | null>(null);
const canConfigurePlayers = computed(() =>
  authManager.hasScope(Scope.CONFIG_PLAYERS_WRITE),
);
const showSetupPrompt = ref(true);

const playersNeedingSetup = computed(() =>
  Object.values(api.players).filter(
    (player) => player.enabled && player.needs_setup,
  ),
);

const reviewSetupPlayers = () => {
  router.push({ name: "playersettings", query: { status: "needs_setup" } });
};

const handleHomescreenEditToggle = () => {
  editMode.value = !editMode.value;
};

const navigateToProviders = () => {
  if (erroredProviderType.value) {
    router.push({
      name: "providersettings",
      query: { types: erroredProviderType.value },
    });
  } else {
    router.push({ name: "settings" });
  }
};

onMounted(async () => {
  // the warning leads on to every provider type, not just a member's own music sources
  if (authManager.hasScope(Scope.CONFIG_PROVIDERS_WRITE)) {
    try {
      const configs = await api.getProviderConfigs();
      const firstError = configs.find(
        (config) => config.enabled && config.last_error,
      );
      hasProviderErrors.value = !!firstError;
      erroredProviderType.value = firstError?.type ?? null;
    } catch {
      // Ignore errors - this is a best-effort feature
    }
  }
});
</script>

<style scoped>
.provider-alert {
  border-color: var(--destructive) !important;
}

.ed-discover {
  background:
    radial-gradient(
      1200px 600px at 20% -10%,
      rgba(var(--v-theme-primary), 0.1),
      transparent 60%
    ),
    rgb(var(--v-theme-background));
  min-height: 100%;
}

.next-discovery-callout {
  display: flex;
  min-height: 190px;
  margin: 0 1.75rem 1.5rem;
  align-items: flex-end;
  justify-content: space-between;
  gap: 2rem;
  overflow: hidden;
  padding: clamp(1.4rem, 4vw, 2.5rem);
  border: 1px solid color-mix(in srgb, var(--primary) 28%, transparent);
  border-radius: 1.5rem;
  background:
    radial-gradient(
      circle at 86% 20%,
      color-mix(in srgb, var(--primary) 32%, transparent),
      transparent 32%
    ),
    linear-gradient(
      125deg,
      color-mix(in srgb, var(--card) 94%, #111325),
      color-mix(in srgb, var(--primary) 12%, var(--card))
    );
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.16);
}

.next-discovery-callout__copy {
  max-width: 690px;
}

.next-discovery-callout__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--primary);
  font-size: 0.76rem;
  font-weight: 750;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.next-discovery-callout h1 {
  margin-top: 0.65rem;
  font-size: clamp(1.75rem, 4vw, 3.25rem);
  font-weight: 780;
  letter-spacing: -0.045em;
  line-height: 1.02;
}

.next-discovery-callout p {
  max-width: 580px;
  margin-top: 0.8rem;
  color: var(--muted-foreground);
  font-size: clamp(0.9rem, 1.4vw, 1.05rem);
}

.next-discovery-callout__action {
  flex: none;
}

@media (max-width: 700px) {
  .next-discovery-callout {
    min-height: 250px;
    margin-inline: 1rem;
    align-items: flex-start;
    flex-direction: column;
  }
}

.ed-edit-done {
  position: fixed;
  right: calc(24px + var(--device-inset-right));
  top: calc(24px + var(--device-inset-top));
  /* Only has to clear the drag ghost in HomeWidgetRows, so it stays out of the
     global stacking scale and below the player bar and its backdrops. */
  z-index: 60;
  /* Outweighs the equally-!important radius the button's own variants carry. */
  border-radius: 999px !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}
</style>
