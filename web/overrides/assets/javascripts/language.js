// Keep the reader on the same page when they switch the language.
//
// Both sites use the same page paths; the Swedish site lives under /sv/.
// The theme's own switch cannot see this, because the Swedish root is inside
// the Finnish one, so it always opens the home page of the other language.
// If the page does not exist in the other language, open its home page.
document.addEventListener(
  "click",
  async (event) => {
    const link = event.target.closest(".md-select__link[hreflang]");
    if (!link || event.metaKey || event.ctrlKey || event.shiftKey) {
      return;
    }
    event.preventDefault();
    event.stopImmediatePropagation();

    const roots = {};
    for (const item of document.querySelectorAll(".md-select__link[hreflang]")) {
      roots[item.getAttribute("hreflang")] = new URL(item.href);
    }
    const current = roots[document.documentElement.lang];
    const target = new URL(link.href);
    let destination = target;

    if (current && location.pathname.startsWith(current.pathname)) {
      let page = location.pathname.slice(current.pathname.length);
      // On the Finnish site, /sv/... is the Swedish site, not a Finnish page.
      if (page.startsWith("sv/")) {
        page = "";
      }
      const candidate = new URL(page + location.hash, target);
      try {
        const response = await fetch(candidate, { method: "HEAD" });
        if (response.ok) {
          destination = candidate;
        }
      } catch {
        // Offline or blocked: fall back to the home page of the language.
      }
    }
    location.href = destination.href;
  },
  true,
);
