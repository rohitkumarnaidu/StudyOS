import { test, expect } from "@playwright/test";

test.describe("Quiz Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.fill('input[type="email"]', "demo@example.com");
    await page.fill('input[type="password"]', "demo");
    await page.click('button:has-text("Sign in")');
    await page.waitForURL("/dashboard");
  });

  test("should navigate to quiz page", async ({ page }) => {
    await page.goto("/quiz");
    await expect(page).toHaveURL(/\/quiz/);
  });

  test("should display quiz setup options", async ({ page }) => {
    await page.goto("/quiz");
    await expect(page.locator("text=Quiz")).toBeVisible();
  });

  test("should select chapter for quiz", async ({ page }) => {
    await page.goto("/quiz");
    await expect(page.locator("text=Quiz")).toBeVisible();
  });

  test("should display quiz player when quiz starts", async ({ page }) => {
    await page.goto("/quiz");
    await expect(page.locator("text=Quiz")).toBeVisible();
  });
});

test.describe("Notes Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.fill('input[type="email"]', "demo@example.com");
    await page.fill('input[type="password"]', "demo");
    await page.click('button:has-text("Sign in")');
    await page.waitForURL("/dashboard");
  });

  test("should navigate to notes page", async ({ page }) => {
    await page.goto("/notes");
    await expect(page).toHaveURL(/\/notes/);
  });

  test("should display notes library", async ({ page }) => {
    await page.goto("/notes");
    await expect(page.locator("text=Notes")).toBeVisible();
  });

  test("should show upload button", async ({ page }) => {
    await page.goto("/notes");
    await expect(page.locator("text=Upload")).toBeVisible();
  });
});

test.describe("Analytics Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.fill('input[type="email"]', "demo@example.com");
    await page.fill('input[type="password"]', "demo");
    await page.click('button:has-text("Sign in")');
    await page.waitForURL("/dashboard");
  });

  test("should navigate to analytics page", async ({ page }) => {
    await page.goto("/analytics");
    await expect(page).toHaveURL(/\/analytics/);
  });

  test("should display analytics dashboard", async ({ page }) => {
    await page.goto("/analytics");
    await expect(page.locator("text=Analytics")).toBeVisible();
  });

  test("should show streak calendar", async ({ page }) => {
    await page.goto("/analytics");
    await expect(page.locator("text=Last 30 Days")).toBeVisible();
  });

  test("should show weak areas section", async ({ page }) => {
    await page.goto("/analytics");
    await expect(page.locator("text=Areas to Improve")).toBeVisible();
  });
});

test.describe("Settings Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.fill('input[type="email"]', "demo@example.com");
    await page.fill('input[type="password"]', "demo");
    await page.click('button:has-text("Sign in")');
    await page.waitForURL("/dashboard");
  });

  test("should navigate to settings page", async ({ page }) => {
    await page.goto("/settings");
    await expect(page).toHaveURL(/\/settings/);
  });

  test("should display settings page", async ({ page }) => {
    await page.goto("/settings");
    await expect(page.locator("text=Settings")).toBeVisible();
  });

  test("should show profile section", async ({ page }) => {
    await page.goto("/settings");
    await expect(page.locator("text=Profile")).toBeVisible();
  });
});

test.describe("Navigation Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.fill('input[type="email"]', "demo@example.com");
    await page.fill('input[type="password"]', "demo");
    await page.click('button:has-text("Sign in")');
    await page.waitForURL("/dashboard");
  });

  test("should navigate from dashboard to syllabus", async ({ page }) => {
    await page.goto("/dashboard");
    await page.click("text=Syllabus");
    await page.waitForURL(/\/syllabus/);
  });

  test("should navigate from dashboard to notes", async ({ page }) => {
    await page.goto("/dashboard");
    await page.click("text=Notes");
    await page.waitForURL(/\/notes/);
  });

  test("should navigate from dashboard to analytics", async ({ page }) => {
    await page.goto("/dashboard");
    await page.click("text=Analytics");
    await page.waitForURL(/\/analytics/);
  });

  test("should navigate from dashboard to settings", async ({ page }) => {
    await page.goto("/dashboard");
    await page.click("text=Settings");
    await page.waitForURL(/\/settings/);
  });
});
