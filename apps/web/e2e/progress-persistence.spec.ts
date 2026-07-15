import { test, expect } from "@playwright/test";

test.describe("Progress Persistence", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
  });

  test("should toggle subtopic and persist after refresh", async ({ page }) => {
    await page.goto("/syllabus");

    const firstChapter = page.locator(".chapter-item").first();
    await firstChapter.click();

    const firstSubtopic = page.locator('[data-testid="subtopic-toggle"]').first();
    const initialChecked = await firstSubtopic.isChecked();

    await firstSubtopic.click();

    const afterClickChecked = await firstSubtopic.isChecked();
    expect(afterClickChecked).toBe(!initialChecked);

    await page.reload();

    const afterRefreshChecked = await firstSubtopic.isChecked();
    expect(afterRefreshChecked).toBe(!initialChecked);
  });

  test("should show progress ring update after toggle", async ({ page }) => {
    await page.goto("/syllabus");

    const firstChapter = page.locator(".chapter-item").first();
    await firstChapter.click();

    const progressText = page.locator('[data-testid="chapter-progress"]');
    const beforeText = await progressText.textContent();

    const firstSubtopic = page.locator('[data-testid="subtopic-toggle"]').first();
    await firstSubtopic.click();

    await page.waitForTimeout(500);

    const afterText = await progressText.textContent();
    expect(afterText).not.toBe(beforeText);
  });

  test("should display streak badge on dashboard", async ({ page }) => {
    await page.goto("/dashboard");

    const streakBadge = page.locator('[data-testid="streak-badge"]');
    await expect(streakBadge).toBeVisible();
  });
});
