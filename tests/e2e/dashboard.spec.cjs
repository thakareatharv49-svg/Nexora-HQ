const { test, expect } = require("@playwright/test");

test("administrator can sign in, browse ventures, search, and sign out", async ({ page }) => {
  const pageErrors = [];
  page.on("pageerror", error => pageErrors.push(error.message));

  await page.goto("/");
  const dialog = page.getByRole("dialog", { name: "Sign in to Nexora HQ" });
  await expect(dialog).toBeVisible();

  await page.getByLabel("Administrator password").fill("wrong-password");
  await page.getByRole("button", { name: /Sign in/ }).click();
  await expect(page.getByRole("alert")).toHaveText("Invalid password. Try again.");
  await expect(dialog).toBeVisible();

  await page.getByLabel("Administrator password").fill("e2e-test-password");
  await page.getByRole("button", { name: /Sign in/ }).click();
  await expect(dialog).toBeHidden();
  await expect(page.getByRole("heading", { name: "One view. Every venture." })).toBeVisible();
  await expect(page.getByText("HQ API CONNECTED")).toBeVisible();
  await expect(page.getByRole("button", { name: "Sign out" })).toBeVisible();

  await page.getByRole("link", { name: /Ventures/ }).click();
  await expect(page.getByRole("heading", { name: "Venture registry" })).toBeVisible();
  await page.getByRole("searchbox", { name: "Search ventures" }).fill("Open Source");
  await expect(page.getByRole("heading", { name: "AI Open Source Contributor" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "AI Software Developer" })).toHaveCount(0);

  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(dialog).toBeVisible();
  await expect(page.getByRole("button", { name: "Sign out" })).toBeHidden();
  expect(pageErrors).toEqual([]);
});


test("mobile navigation and keyboard focus remain usable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  const dialog = page.getByRole("dialog", { name: "Sign in to Nexora HQ" });
  const password = page.getByLabel("Administrator password");
  await expect(dialog).toBeVisible();
  await expect(password).toBeFocused();

  await page.keyboard.press("Shift+Tab");
  await expect(page.getByRole("button", { name: /Sign in/ })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(password).toBeFocused();

  await password.fill("e2e-test-password");
  await page.getByRole("button", { name: /Sign in/ }).click();
  await expect(dialog).toBeHidden();

  await expect(page.locator(".main-content")).toHaveCSS("margin-left", "0px");
  const menu = page.getByRole("button", { name: "Toggle navigation" });
  await expect(menu).toBeVisible();
  await menu.click();
  await expect(menu).toHaveAttribute("aria-expanded", "true");
  await page.getByRole("link", { name: /Ventures/ }).click();
  await expect(page.getByRole("heading", { name: "Venture registry" })).toBeVisible();
  await expect(menu).toHaveAttribute("aria-expanded", "false");
});

test("administrator can register a venture without connecting its workload", async ({ page }) => {
  const pageErrors = [];
  page.on("pageerror", error => pageErrors.push(error.message));

  await page.goto("/");
  const signIn = page.getByRole("dialog", { name: "Sign in to Nexora HQ" });
  await page.getByLabel("Administrator password").fill("e2e-test-password");
  await page.getByRole("button", { name: /Sign in/ }).click();
  await expect(signIn).toBeHidden();

  await page.getByRole("link", { name: /Ventures/ }).click();
  await page.getByRole("button", { name: "Add venture" }).click();
  const addDialog = page.getByRole("dialog", { name: "Add a venture" });
  await expect(addDialog).toBeVisible();
  await page.getByLabel("Venture name").fill("QA Observability Venture");
  await page.getByLabel("Category").fill("Infrastructure");
  await page.getByLabel("Description").fill("Tracks internal quality and operational readiness.");
  await page.getByLabel("Repository URL").fill("https://github.com/example/qa-observability");
  await page.getByRole("button", { name: "Add to registry" }).click();

  await expect(addDialog).toBeHidden();
  await expect(page.getByRole("heading", { name: "QA Observability Venture" })).toBeVisible();
  await expect(page.getByText("Not connected").last()).toBeVisible();

  await page.getByRole("button", { name: "Add venture" }).click();
  await page.getByLabel("Venture name").fill("QA Observability Venture");
  await page.getByLabel("Category").fill("Infrastructure");
  await page.getByLabel("Description").fill("Tracks internal quality and operational readiness.");
  await page.getByRole("button", { name: "Add to registry" }).click();
  await expect(page.getByRole("alert")).toHaveText("A venture with this name is already registered.");
  expect(pageErrors).toEqual([]);
});
