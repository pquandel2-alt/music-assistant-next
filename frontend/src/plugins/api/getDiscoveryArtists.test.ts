import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "./index";

describe("getDiscoveryArtists", () => {
  afterEach(() => vi.restoreAllMocks());

  it("forwards catalog filters and the opaque cursor", async () => {
    const page = {
      items: [],
      next_cursor: null,
      source_count: 1,
      total: 0,
    };
    const spy = vi.spyOn(api, "sendCommand").mockResolvedValue(page);

    await api.getDiscoveryArtists("ambient", "spotify--user", "session:24", 36);

    expect(spy).toHaveBeenCalledWith("music/discovery/artists", {
      query: "ambient",
      provider: "spotify--user",
      cursor: "session:24",
      limit: 36,
    });
  });
});
