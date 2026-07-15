import { test, expect } from "@playwright/test";

test.describe("Mobile Responsive", () => {
  test("should render login form on mobile viewport", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText(/sign in|studyos/i);
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test("should render signup form on mobile viewport", async ({ page }) => {
    await page.goto("/signup");
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test("should have touch-friendly button sizes", async ({ page }) => {
    await page.goto("/");
    const buttons = page.locator("button");
    const count = await buttons.count();
    expect(count).toBeGreaterThan(0);

    for (let i = 0; i < Math.min(count, 3); i++) {
      const box = await buttons.nth(i).boundingBox();
      expect(box).not.toBeNull();
      expect(box!.height).toBeGreaterThanOrEqual(32);
    }
  });

  test("should not have horizontal overflow", async ({ page }) => {
    await page.goto("/");
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = page.viewportSize()?.width ?? 0;
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 2);
  });

  test("should render dashboard shell on mobile", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.locator("text=NEET 2026")).toBeVisible();
  });

  test("should have readable text on mobile", async ({ page }) => {
    await page.goto("/dashboard");
    const fontSize = await page.evaluate(() => {
      const el = document.body;
      return parseFloat(getComputedStyle(el).fontSize);
    });
    expect(fontSize).toBeGreaterThanOrEqual(14);
  });

  test("should have accessible tap targets", async ({ page }) => {
    await page.goto("/");
    const links = page.locator("a, button");
    const count = await links.count();

    for (let i = 0; i < Math.min(count, 5); i++) {
      const box = await links.nth(i).boundingBox();
      if (box) {
        expect(box.width).toBeGreaterThanOrEqual(24);
        expect(box.height).toBeGreaterThanOrEqual(24);
      }
    }
  });
});

test.describe("Mobile Navigation", () => {
  test("should have working navigation on mobile", async ({ page }) => {
    await page.goto("/");
    await page.click("text=Sign up");
    await expect(page).toHaveURL(/\/signup/);
  });

  test("should handle form submission on mobile", async ({ page }) => {
    await page.goto("/signup");
    await page.fill('input[type="email"]', "mobile@test.com");
    await page.fill('input[type="password"]', "short");
    await page.fill('input[placeholder*="Name"]', "Mobile User");
    await page.click('input[type="checkbox"]');
    await page.click('button[type="submit"]');

    await expect(page.locator("text=Min 8 characters")).toBeVisible();
  });

  test("should render footer on mobile", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("footer, [role=contentinfo]")).toBeVisible();
  });
});
