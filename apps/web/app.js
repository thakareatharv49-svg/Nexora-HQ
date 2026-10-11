(() => {
  "use strict";
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const pages = ["overview", "ventures", "activity", "settings"];
  let apiConnected = false;
  let ventureItems = [];
  let editingVentureId = null;
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

  function makeVentureCard(item, allowEdit = false) {
    const card = document.createElement("article");
    card.className = "venture-card";
    card.dataset.venture = item.id;
    card.dataset.search = [item.name, item.category, item.description].join(" ").toLowerCase();

    const top = document.createElement("div");
    top.className = "venture-card-top";
    const logo = document.createElement("div");
    logo.className = "venture-logo " + (/open source/i.test(item.category) ? "logo-violet" : "logo-blue");
    logo.textContent = String(item.name || "NX").trim().split(/\\s+/).map(part => part[0] || "").join("").slice(0, 2).toUpperCase();
    const state = document.createElement("span");
    state.className = "state-pill";
    const stateDot = document.createElement("i");
    state.append(stateDot, document.createTextNode(
      item.connection_state === "connected" ? "Connected" :
      item.connection_state === "degraded" ? "Degraded" :
      item.connection_state === "unavailable" ? "Unavailable" : "Not connected"
    ));
    top.append(logo, state);

    const category = document.createElement("p");
    category.className = "venture-category";
    category.textContent = item.category;
    const title = document.createElement("h3");
    title.textContent = item.name;
    const description = document.createElement("p");
    description.className = "venture-description";
    description.textContent = item.description;

    const metadata = document.createElement("div");
    metadata.className = "venture-metadata";
    const categoryMeta = document.createElement("span");
    const categoryIcon = document.createElement("i");
    categoryIcon.className = "mini-icon";
    categoryIcon.textContent = "⌘";
    categoryMeta.append(categoryIcon, document.createTextNode(" " + item.category));
    const ownershipMeta = document.createElement("span");
    const ownershipIcon = document.createElement("i");
    ownershipIcon.className = "mini-icon";
    ownershipIcon.textContent = "↗";
    ownershipMeta.append(ownershipIcon, document.createTextNode(" Independent venture"));
    metadata.append(categoryMeta, ownershipMeta);

    const footer = document.createElement("div");
    footer.className = "venture-card-footer";
    const footerState = document.createElement("span");
    footerState.className = "footer-state";
    const footerDot = document.createElement("span");
    footerDot.className = "status-dot";
    const statusText = item.connection_state === "connected" ? "Connected" :
      item.connection_state === "degraded" ? "Needs attention" :
      item.connection_state === "unavailable" ? "Unavailable" : "Awaiting adapter";
    footerState.append(footerDot, document.createTextNode(statusText));
    let repositoryLink = null;
    if (item.repository_url) {
      try {
        const parsed = new URL(item.repository_url);
        if (parsed.protocol === "https:" || parsed.protocol === "http:") {
          repositoryLink = document.createElement("a");
          repositoryLink.href = parsed.href;
          repositoryLink.target = "_blank";
          repositoryLink.rel = "noreferrer";
          repositoryLink.textContent = "View repository ↗";
        }
      } catch {
        repositoryLink = null;
      }
    }
    if (repositoryLink) {
      footer.append(footerState, repositoryLink);
    } else {
      const noRepository = document.createElement("span");
      noRepository.className = "footer-muted";
      noRepository.textContent = "Repository not linked";
      footer.append(footerState, noRepository);
    }
    if (allowEdit) {
      const editButton = document.createElement("button");
      editButton.type = "button";
      editButton.className = "edit-venture-button";
      editButton.dataset.editVenture = item.id;
      editButton.setAttribute("aria-label", "Edit " + item.name);
      editButton.textContent = "Edit";
      footer.append(editButton);
    }
    card.append(top, category, title, description, metadata, footer);
    return card;
  }


  function renderDeveloperIntegration(item) {
    const state = $("#developer-integration-state");
    const message = $("#developer-integration-message");
    const metrics = $("#developer-integration-metrics");
    const freshness = $("#developer-integration-freshness");
    if (!state || !message || !metrics || !freshness || !item) return;

    const stateLabels = {
      not_configured: "Not configured",
      connected: "Connected",
      stale: "Stale data",
      error: "Connection error"
    };
    state.replaceChildren(document.createElement("i"), document.createTextNode(" " + (stateLabels[item.integration_state] || "Unknown")));
    state.classList.toggle("integration-connected", item.integration_state === "connected");
    state.classList.toggle("integration-warning", item.integration_state === "stale" || item.integration_state === "error");
    message.textContent = item.message || "No venture status message is available.";

    const values = [
      ["Active missions", item.active_missions],
      ["Queued", item.queued_missions],
      ["Completed", item.completed_missions],
      ["Blocked", item.blocked_missions]
    ];
    metrics.replaceChildren(...values.map(([label, value]) => {
      const metric = document.createElement("div");
      metric.className = "integration-metric";
      const caption = document.createElement("span");
      caption.textContent = label;
      const count = document.createElement("strong");
      count.textContent = Number.isInteger(value) && value >= 0 ? String(value) : "—";
      metric.append(caption, count);
      return metric;
    }));

    const lastSuccess = item.last_success_at ? new Date(item.last_success_at) : null;
    freshness.textContent = lastSuccess && !Number.isNaN(lastSuccess.getTime())
      ? "Last successful check: " + lastSuccess.toLocaleString()
      : "Last successful check: not yet";

    const noticeTitle = $("#integration-notice-title");
    const noticeDescription = $("#integration-notice-description");
    const noticeTag = $("#integration-notice-tag");
    if (noticeTitle && noticeDescription && noticeTag) {
      if (item.integration_state === "connected") {
        noticeTitle.textContent = "Read-only venture monitoring is connected";
        noticeDescription.textContent = "Status and mission counts come from the venture's dedicated endpoint; HQ cannot start, stop, or change missions.";
        noticeTag.textContent = "READ ONLY";
      } else if (item.integration_state === "stale" || item.integration_state === "error") {
        noticeTitle.textContent = "Venture monitoring needs attention";
        noticeDescription.textContent = item.message || "HQ could not verify the latest venture status.";
        noticeTag.textContent = item.integration_state === "stale" ? "STALE" : "ERROR";
      } else {
        noticeTitle.textContent = "External venture monitoring is not configured";
        noticeDescription.textContent = "HQ shows live status only after a dedicated read-only adapter is configured. It never invents health or mission metrics.";
        noticeTag.textContent = "NOT CONNECTED";
      }
    }
  }

  function renderRegistry(query = "") {
    const grid = $("#registry-grid");
    if (!grid) return;
    const normalized = query.trim().toLowerCase();
    if (apiConnected) {
      const cards = ventureItems.filter(item =>
        [item.name, item.category, item.description].join(" ").toLowerCase().includes(normalized)
      );
      grid.replaceChildren(...cards.map(item => makeVentureCard(item, true)));
      $("#search-count").textContent = "Showing " + cards.length + (cards.length === 1 ? " venture" : " ventures");
      $("#registry-total").textContent = ventureItems.length + " REGISTERED";
      const noResults = cards.length === 0;
      $("#empty-search").classList.toggle("hidden", !noResults);
      grid.classList.toggle("hidden", noResults);
      $("#empty-search-title").textContent = normalized ? "No ventures found" : "No ventures registered yet";
      $("#empty-search-description").textContent = normalized
        ? "Try a different search term."
        : "Add a venture to begin building your HQ registry.";
      return;
    }
    const source = $("#venture-grid");
    const cards = $$(".venture-card", source).filter(card =>
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
    const editButton = event.target.closest("[data-edit-venture]");
    if (editButton) {
      const item = ventureItems.find(venture => venture.id === editButton.dataset.editVenture);
      if (item) openVentureDialog(item);
      return;
    }
    const card = event.target.closest(".venture-card");
    if (card && !event.target.closest("a")) notify("Venture details will be available after the registry API is implemented.");
  });

  function openVentureDialog(item = null) {
    const dialog = $("#venture-dialog");
    if (!apiConnected || !dialog) {
      notify("Venture registry editing requires the HQ API.");
      return;
    }
    editingVentureId = item ? item.id : null;
    $("#venture-dialog-title").textContent = item ? "Edit venture" : "Add a venture";
    $("#save-venture").textContent = item ? "Save changes" : "Add to registry";
    $("#venture-name").value = item ? item.name : "";
    $("#venture-category").value = item ? item.category : "";
    $("#venture-description").value = item ? item.description : "";
    $("#venture-repository").value = item && item.repository_url ? item.repository_url : "";
    $("#venture-form-error").textContent = "";
    dialog.showModal();
    $("#venture-name").focus();
  }

  $("#add-venture")?.addEventListener("click", () => openVentureDialog());

  function closeVentureDialog() {
    const dialog = $("#venture-dialog");
    if (dialog?.open) dialog.close();
    $("#venture-form")?.reset();
    $("#venture-form-error").textContent = "";
    editingVentureId = null;
    $("#venture-dialog-title").textContent = "Add a venture";
    $("#save-venture").textContent = "Add to registry";
  }

  $("#close-venture-dialog")?.addEventListener("click", closeVentureDialog);
  $("#cancel-venture")?.addEventListener("click", closeVentureDialog);
  $("#venture-form")?.addEventListener("submit", async event => {
    event.preventDefault();
    const error = $("#venture-form-error");
    const saveButton = $("#save-venture");
    error.textContent = "";
    const payload = {
      name: $("#venture-name").value.trim(),
      category: $("#venture-category").value.trim(),
      description: $("#venture-description").value.trim(),
      repository_url: $("#venture-repository").value.trim() || null
    };
    saveButton.disabled = true;
    try {
      const isEditing = Boolean(editingVentureId);
      const endpoint = isEditing
        ? "/api/ventures/" + encodeURIComponent(editingVentureId)
        : "/api/ventures";
      const response = await fetch(endpoint, {
        method: isEditing ? "PATCH" : "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (response.status === 401) {
        closeVentureDialog();
        await syncHQApi();
        notify("Your session expired. Sign in before adding a venture.");
        return;
      }
      if (response.status === 409) {
        error.textContent = "A venture with this name is already registered.";
        return;
      }
      if (!response.ok) {
        error.textContent = response.status === 422
          ? "Check the required fields and repository URL."
          : "Could not add the venture. Try again.";
        return;
      }
      await syncHQApi();
      closeVentureDialog();
      showPage("ventures");
      notify(isEditing ? "Venture details updated." : "Venture added to the HQ registry.");
    } catch {
      error.textContent = "Could not reach the HQ server. Try again.";
    } finally {
      saveButton.disabled = false;
    }
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

      const [ventureResponse, activityResponse, integrationResponse] = await Promise.all([
        fetch("/api/ventures", { headers: { Accept: "application/json" }, cache: "no-store" }),
        fetch("/api/activity?limit=50", { headers: { Accept: "application/json" }, cache: "no-store" }),
        fetch("/api/integrations/ai-software-developer", { headers: { Accept: "application/json" }, cache: "no-store" })
      ]);
      if (ventureResponse.status === 401 || activityResponse.status === 401 || integrationResponse.status === 401) {
        await syncHQApi();
        return;
      }
      if (ventureResponse.ok) {
        const registry = await ventureResponse.json();
        const values = $(".stat-card .stat-value");
        if (values[0] && Number.isInteger(registry.count)) values[0].textContent = String(registry.count).padStart(2, "0");
        if (Array.isArray(registry.items)) {
          apiConnected = true;
          ventureItems = registry.items;
          $("#add-venture")?.classList.remove("hidden");
          const connected = ventureItems.filter(item => item.connection_state === "connected").length;
          if (values[1]) values[1].textContent = String(connected).padStart(2, "0");
          $("#venture-grid")?.replaceChildren(...ventureItems.map(item => makeVentureCard(item)));
          renderRegistry($("#venture-search")?.value || "");
        }
      }
      if (integrationResponse.ok) {
        renderDeveloperIntegration(await integrationResponse.json());
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
          $$(".panel-footnote").forEach(note => { note.textContent = "Persisted HQ records; no external venture activity is connected."; });
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

  document.addEventListener("keydown", event => {
    const overlay = $("#auth-overlay");
    if (overlay.classList.contains("hidden")) return;
    if (event.key === "Escape") {
      event.preventDefault();
      return;
    }
    if (event.key !== "Tab") return;
    const focusable = $$("input:not([disabled]), button:not([disabled]), a[href]", overlay);
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  document.documentElement.classList.add("auth-checking");
  const hashPage = location.hash.slice(1);
  if (pages.includes(hashPage)) showPage(hashPage);
  else showPage("overview");
  syncHQApi();
})();