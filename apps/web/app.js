(() => {
  "use strict";
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const pages = ["overview", "ventures", "activity", "settings"];
  const activityItems = [
    { symbol: "✦", tone: "violet", title: "HQ foundation created", detail: "Dashboard shell and venture boundaries established.", meta: "Foundation record · illustrative", kind: "SYSTEM" },
    { symbol: "◇", tone: "blue", title: "Venture registry initialized", detail: "Two independent ventures listed for future monitoring.", meta: "Foundation record · illustrative", kind: "REGISTRY" },
    { symbol: "⌁", tone: "teal", title: "Integration boundary documented", detail: "Future adapters are restricted to venture-level read-only status.", meta: "Foundation record · illustrative", kind: "ARCHITECTURE" }
  ];
  document.documentElement.dataset.hqMode = "foundation";

  function showPage(name) {
    if (!pages.includes(name)) name = "overview";
    $$("[data-page]").forEach(section => section.classList.toggle("hidden", section.dataset.page !== name));
    $$(".nav-link").forEach(link => {
      const active = link.dataset.view === name;
      link.classList.toggle("active", active);
      if (active) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    const crumb = $("#current-crumb");
    if (crumb) crumb.textContent = name === "ventures" ? "Venture registry" : name[0].toUpperCase() + name.slice(1);
    document.title = "Nexora HQ · " + (name === "ventures" ? "Venture registry" : name[0].toUpperCase() + name.slice(1));
    $(".sidebar")?.classList.remove("sidebar-open");
    $("#mobile-menu")?.setAttribute("aria-expanded", "false");
    if (location.hash !== "#" + name) history.replaceState(null, "", "#" + name);
    if (name === "ventures") renderRegistry($("#venture-search")?.value || "");
  }

  function makeActivity(item) {
    const row = document.createElement("article");
    row.className = "activity-row";
    const symbol = document.createElement("span");
    symbol.className = "activity-symbol symbol-" + item.tone;
    symbol.textContent = item.symbol;
    const copy = document.createElement("div");
    copy.className = "activity-copy";
    const title = document.createElement("strong");
    title.textContent = item.title;
    const detail = document.createElement("p");
    detail.textContent = item.detail;
    const meta = document.createElement("small");
    meta.textContent = item.meta;
    copy.append(title, detail, meta);
    const kind = document.createElement("span");
    kind.className = "activity-kind";
    kind.textContent = item.kind;
    row.append(symbol, copy, kind);
    return row;
  }

  function renderRegistry(query = "") {
    const grid = $("#registry-grid");
    if (!grid) return;
    const normalized = query.trim().toLowerCase();
    const cards = $$(".venture-card", $("#venture-grid")).filter(card =>
      (card.dataset.search || "").toLowerCase().includes(normalized) ||
      $("h3", card).textContent.toLowerCase().includes(normalized)
    );
    grid.replaceChildren(...cards.map(card => card.cloneNode(true)));
    $("#search-count").textContent = "Showing " + cards.length + (cards.length === 1 ? " venture" : " ventures");
    $("#empty-search").classList.toggle("hidden", cards.length !== 0);
    grid.classList.toggle("hidden", cards.length === 0);
  }

  function notify(message) {
    const toast = $("#toast");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("toast-visible");
    clearTimeout(notify.timer);
    notify.timer = setTimeout(() => toast.classList.remove("toast-visible"), 2600);
  }

  $$(".nav-link").forEach(link => link.addEventListener("click", event => {
    event.preventDefault();
    showPage(link.dataset.view);
  }));
  $$("[data-go]").forEach(button => button.addEventListener("click", () => showPage(button.dataset.go)));
  $("#venture-search")?.addEventListener("input", event => renderRegistry(event.target.value));
  $("#mobile-menu")?.addEventListener("click", () => {
    const sidebar = $(".sidebar");
    const open = sidebar.classList.toggle("sidebar-open");
    $("#mobile-menu").setAttribute("aria-expanded", String(open));
  });
  $("#venture-grid")?.addEventListener("click", event => {
    const card = event.target.closest(".venture-card");
    if (card && !event.target.closest("a")) notify("Venture details will be available after the registry API is implemented.");
  });
  $("#registry-grid")?.addEventListener("click", event => {
    const card = event.target.closest(".venture-card");
    if (card && !event.target.closest("a")) notify("Venture details will be available after the registry API is implemented.");
  });

  const allActivity = $("#all-activity-list");
  if (allActivity) allActivity.replaceChildren(...activityItems.map(makeActivity));

  async function syncHQApi() {
    try {
      const authResponse = await fetch("/api/auth/status", { headers: { Accept: "application/json" }, cache: "no-store" });
      if (!authResponse.ok) {
        document.documentElement.classList.remove("auth-checking");
        return;
      }
      const auth = await authResponse.json();
      const overlay = $("#auth-overlay");
      const signOut = $("#sign-out");
      if (auth.auth_required && !auth.authenticated) {
        overlay.classList.remove("hidden");
        signOut.classList.add("hidden");
        document.documentElement.classList.remove("auth-checking");
        $("#login-password").focus();
        return;
      }
      overlay.classList.add("hidden");
      signOut.classList.toggle("hidden", !auth.auth_required);
      document.documentElement.classList.remove("auth-checking");

      const healthResponse = await fetch("/api/health", { headers: { Accept: "application/json" }, cache: "no-store" });
      if (!healthResponse.ok) return;
      const health = await healthResponse.json();
      if (health.status !== "ok" || health.service !== "nexora-hq") return;

      $("#api-status-text").textContent = "HQ API CONNECTED";
      document.documentElement.dataset.hqApi = "connected";
      document.documentElement.classList.add("api-connected");

      const [ventureResponse, activityResponse] = await Promise.all([
        fetch("/api/ventures", { headers: { Accept: "application/json" }, cache: "no-store" }),
        fetch("/api/activity?limit=50", { headers: { Accept: "application/json" }, cache: "no-store" })
      ]);
      if (ventureResponse.ok) {
        const registry = await ventureResponse.json();
        const values = $(".stat-card .stat-value");
        if (values[0] && Number.isInteger(registry.count)) values[0].textContent = String(registry.count).padStart(2, "0");
        if (values[1] && Array.isArray(registry.items)) {
          const connected = registry.items.filter(item => item.connection_state === "connected").length;
          values[1].textContent = String(connected).padStart(2, "0");
        }
      }
      if (activityResponse.ok) {
        const payload = await activityResponse.json();
        if (Array.isArray(payload.items)) {
          const records = payload.items.map(item => ({
            symbol: item.kind === "REGISTRY" ? "◇" : item.kind === "ARCHITECTURE" ? "⌁" : "✦",
            tone: item.kind === "REGISTRY" ? "blue" : item.kind === "ARCHITECTURE" ? "teal" : "violet",
            title: item.title,
            detail: item.detail,
            meta: item.source === "hq" ? "HQ record · persisted" : "External record · read-only",
            kind: item.kind
          }));
          $("#activity-list")?.replaceChildren(...records.slice(0, 3).map(makeActivity));
          $("#all-activity-list")?.replaceChildren(...records.map(makeActivity));
          $(".panel-footnote").forEach(note => { note.textContent = "Persisted HQ records; no external venture activity is connected."; });
        }
      }
    } catch {
      // Static hosting has no HQ API; keep the explicit static-foundation state.
    } finally {
      document.documentElement.classList.remove("auth-checking");
    }
  }

  $("#login-form")?.addEventListener("submit", async event => {
    event.preventDefault();
    const error = $("#login-error");
    const password = $("#login-password").value;
    error.textContent = "";
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        body: JSON.stringify({ password })
      });
      if (!response.ok) {
        error.textContent = response.status === 401 ? "Invalid password. Try again." : "Sign-in is unavailable. Check the server configuration.";
        return;
      }
      $("#login-password").value = "";
      await syncHQApi();
    } catch {
      error.textContent = "Could not reach the HQ server. Try again.";
    }
  });

  $("#sign-out")?.addEventListener("click", async () => {
    try {
      await fetch("/api/auth/logout", { method: "POST", headers: { Accept: "application/json" } });
      await syncHQApi();
    } catch {
      notify("Could not sign out. Check the HQ server connection.");
    }
  });

  document.documentElement.classList.add("auth-checking");
  const hashPage = location.hash.slice(1);
  if (pages.includes(hashPage)) showPage(hashPage);
  else showPage("overview");
  syncHQApi();
})();