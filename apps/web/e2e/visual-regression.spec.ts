import { test, expect } from "@playwright/test";

test.describe("Visual Regression", () => {
  test("login page matches snapshot", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveScreenshot("login-page.png", {
      fullPage: true,
      maxDiffPixels: 100,
    });
  });

  test("signup page matches snapshot", async ({ page }) => {
    await page.goto("/signup");
    await expect(page).toHaveScreenshot("signup-page.png", {
      fullPage: true,
      maxDiffPixels: 100,
    });
  });

  test("dashboard matches snapshot", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveScreenshot("dashboard-page.png", {
      fullPage: true,
      maxDiffPixels: 200,
    });
  });

  test("syllabus chapter list matches snapshot", async ({ page }) => {
    await page.goto("/dashboard");
    const chapterList = page.locator("[data-testid=chapter-list]");
    if (await chapterList.isVisible()) {
      await expect(chapterList).toHaveScreenshot("chapter-list.png", {
        maxDiffPixels: 100,
      });
    }
  });
});
