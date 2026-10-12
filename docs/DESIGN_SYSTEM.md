# Design system

Music Assistant Next extends the current shadcn-vue/Tailwind migration instead of introducing a
third UI stack. Vuetify remains where upstream still uses it.

- Primary accent: `#635bff`, used consistently by shadcn and Vuetify tokens.
- Dark-first surfaces: upstream background/card/popover layers are retained.
- Radii: compact controls use existing tokens; feature surfaces use 1.5rem; artist art is round.
- Typography: the upstream Roboto scale remains to avoid an extra font payload. Feature headings
  use responsive `clamp()` sizing and tightened tracking.
- Motion: only opacity/transform/pulse effects; skeleton animation is disabled under
  `prefers-reduced-motion`.
- Touch: horizontal source chips, two-column phone artist grid, 48px search control, native
  long-press context menu, and the existing safe-area-aware mobile player/navigation.
- Loading: content-shaped skeletons preserve layout. Empty and error states explain whether the
  provider returned no data or a request failed.
- Artwork: native image proxy and lazy loading are reused. No browser request is made directly to
  Spotify APIs.

New UI should use `components/ui`, existing media cards, CSS variables, and semantic focus states.
Avoid permanent blur layers or continuous animation on scrolling content.
