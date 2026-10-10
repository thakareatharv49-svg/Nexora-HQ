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
