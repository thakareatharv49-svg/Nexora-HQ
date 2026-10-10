const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const html = fs.readFileSync("apps/web/index.html", "utf8");
const js = fs.readFileSync("apps/web/app.js", "utf8");
const css = fs.readFileSync("apps/web/styles.css", "utf8");

test("dashboard includes all primary views and navigation targets", () => {
  const views = [...html.matchAll(/data-page="([^"]+)"/g)].map(match => match[1]);
  const nav = [...html.matchAll(/data-view="([^"]+)"/g)].map(match => match[1]);
  assert.deepEqual([...new Set(views)].sort(), ["activity", "overview", "settings", "ventures"]);
  assert.deepEqual([...new Set(nav)].sort(), ["activity", "overview", "settings", "ventures"]);
});

test("venture cards remain explicit about unconnected status", () => {
  assert.match(html, /AI Software Developer/);
  assert.match(html, /AI Open Source Contributor/);
  assert.equal((html.match(/Not connected/g) || []).length >= 2, true);
  assert.match(html, /does not fetch live venture data yet/);
  assert.match(html, /No external event stream is connected/);
});

test("external repository links use safe new-tab attributes", () => {
  for (const match of html.matchAll(/<a\b[^>]*target="_blank"[^>]*>/g)) {
    assert.match(match[0], /rel="[^"]*noreferrer[^"]*"/);
  }
});

test("frontend JavaScript parses without browser-side dependencies at build time", () => {
  assert.doesNotThrow(() => new vm.Script(js, { filename: "apps/web/app.js" }));
});

test("responsive and reduced-motion styles are present", () => {
  assert.match(css, /@media\s*\(max-width:\s*760px\)/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /\.hidden\s*\{/);
});
