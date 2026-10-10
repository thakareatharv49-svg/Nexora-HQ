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
  const hashPage = location.hash.slice(1);
  if (pages.includes(hashPage)) showPage(hashPage);
  else showPage("overview");
})();