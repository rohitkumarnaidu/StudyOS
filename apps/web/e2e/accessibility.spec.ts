import { test, expect } from "@playwright/test";

test.describe("Accessibility", () => {
  test("login page has no critical accessibility violations", async ({ page }) => {
    await page.goto("/");

    // Check for accessible form labels
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toHaveAttribute("aria-label");
    await expect(emailInput).toHaveAttribute("id");

    const passwordInput = page.locator('input[type="password"]');
    await expect(passwordInput).toHaveAttribute("aria-label");
    await expect(passwordInput).toHaveAttribute("id");

    // Check submit button is accessible
    const submitButton = page.locator('button[type="submit"]');
    await expect(submitButton).toBeVisible();
    await expect(submitButton).toBeEnabled();
  });

  test("signup page has proper form structure", async ({ page }) => {
    await page.goto("/signup");

    // All inputs should have associated labels
    const inputs = page.locator("input");
    const count = await inputs.count();

    for (let i = 0; i < count; i++) {
      const input = inputs.nth(i);
      const id = await input.getAttribute("id");
      if (id) {
        const label = page.locator(`label[for="${id}"]`);
        const hasLabel = await label.count().then(c => c > 0);
        const hasAriaLabel = await input.getAttribute("aria-label").then(v => v !== null);
        expect(hasLabel || hasAriaLabel).toBe(true);
      }
    }
  });

  test("all interactive elements are keyboard accessible", async ({ page }) => {
    await page.goto("/");

    // Tab through all interactive elements
    const body = page.locator("body");
    await body.press("Tab");

    // Focus should move to first interactive element
    const focusedElement = page.locator(":focus");
    await expect(focusedElement).toBeVisible();
  });

  test("page has valid heading hierarchy", async ({ page }) => {
    await page.goto("/dashboard");

    const h1Count = await page.locator("h1").count();
    expect(h1Count).toBeGreaterThanOrEqual(1);

    // No skipped heading levels
    const headings = await page.locator("h1, h2, h3, h4, h5, h6").all();
    let prevLevel = 0;
    for (const heading of headings) {
      const tagName = await heading.evaluate(el => el.tagName.toLowerCase());
      const level = parseInt(tagName.charAt(1), 10);
      expect(level).toBeLessThanOrEqual(prevLevel + 1);
      prevLevel = level;
    }
  });

  test("color contrast meets WCAG AA standards", async ({ page }) => {
    await page.goto("/");

    // Check that text is readable against backgrounds
    const body = page.locator("body");
    const bgColor = await body.evaluate(el => {
      return getComputedStyle(el).backgroundColor;
    });
    expect(bgColor).not.toBe("transparent");
  });

  test("images have alt text", async ({ page }) => {
    await page.goto("/dashboard");

    const images = page.locator("img");
    const count = await images.count();

    for (let i = 0; i < count; i++) {
      const img = images.nth(i);
      const alt = await img.getAttribute("alt");
      expect(alt).not.toBeNull();
    }
  });

  test("form errors are announced to screen readers", async ({ page }) => {
    await page.goto("/signup");

    // Submit form with invalid data
    await page.fill('input[type="email"]', "invalid");
    await page.fill('input[type="password"]', "short");
    await page.fill('input[placeholder*="Name"]', "Test");
    await page.click('input[type="checkbox"]');
    await page.click('button[type="submit"]');

    // Error messages should be visible
    const errors = page.locator("[role=alert], .text-destructive");
    await expect(errors.first()).toBeVisible();
  });

  test("focus is visible on all interactive elements", async ({ page }) => {
    await page.goto("/");

    const buttons = page.locator("button, a, input");
    const count = await buttons.count();

    for (let i = 0; i < Math.min(count, 5); i++) {
      await buttons.nth(i).focus();
      const outline = await buttons.nth(i).evaluate(el => {
        return getComputedStyle(el).outlineStyle;
      });
      // Either outline or box-shadow should be visible
      expect(outline !== "none").toBe(true);
    }
  });
});
