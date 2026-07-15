import { test, expect } from "@playwright/test";

test.describe("Authentication Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("should navigate to signup page", async ({ page }) => {
    await page.click("text=Sign up");
    await expect(page).toHaveURL(/\/signup/);
    await expect(page.locator("h1")).toContainText("Create account");
  });

  test("should display signup form", async ({ page }) => {
    await page.goto("/signup");
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('input[placeholder*="Name"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test("should validate email format", async ({ page }) => {
    await page.goto("/signup");
    await page.fill('input[type="email"]', "invalid-email");
    await page.fill('input[type="password"]', "ValidPassword123");
    await page.fill('input[placeholder*="Name"]', "Test User");
    await page.click('input[type="checkbox"]'); // Accept terms
    await page.click('button[type="submit"]');

    // Should show validation error
    await expect(page.locator("text=Invalid email")).toBeVisible();
  });

  test("should validate password length", async ({ page }) => {
    await page.goto("/signup");
    await page.fill('input[type="email"]', "test@example.com");
    await page.fill('input[type="password"]', "short");
    await page.fill('input[placeholder*="Name"]', "Test User");
    await page.click('input[type="checkbox"]');
    await page.click('button[type="submit"]');

    // Should show password validation error
    await expect(page.locator("text=Min 8 characters")).toBeVisible();
  });

  test("should require terms acceptance", async ({ page }) => {
    await page.goto("/signup");
    await page.fill('input[type="email"]', "test@example.com");
    await page.fill('input[type="password"]', "ValidPassword123");
    await page.fill('input[placeholder*="Name"]', "Test User");
    // Don't click checkbox
    await page.click('button[type="submit"]');

    // Should show terms error
    await expect(page.locator("text=Accept terms")).toBeVisible();
  });
});

test.describe("Dashboard and Syllabus", () => {
  test("should display dashboard after login", async ({ page }) => {
    // Assuming demo login works
    await page.goto("/");
    await page.fill('input[type="email"]', "demo@example.com");
    await page.fill('input[type="password"]', "demo");
    await page.click('button:has-text("Sign in")');

    // Should redirect to dashboard
    await page.waitForURL("/dashboard");
    await expect(page.locator("text=Dashboard")).toBeVisible();
  });

  test("should display NEET 2026 exam on dashboard", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.locator("text=NEET 2026")).toBeVisible();
  });

  test("should display chapters list", async ({ page }) => {
    await page.goto("/dashboard");
    // Wait for chapters to load
    await page.waitForSelector("text=Physics");
    await expect(page.locator("text=Physics")).toBeVisible();
    await expect(page.locator("text=Chemistry")).toBeVisible();
    await expect(page.locator("text=Biology")).toBeVisible();
  });

  test("should expand/collapse chapters", async ({ page }) => {
    await page.goto("/dashboard");
    const firstChapter = page.locator("[role=button]").first();

    // Click to expand
    await firstChapter.click();
    await expect(page.locator("text=topic")).toBeVisible();

    // Click to collapse
    await firstChapter.click();
    await expect(page.locator("text=topic")).not.toBeVisible();
  });

  test("should show topics when chapter expanded", async ({ page }) => {
    await page.goto("/dashboard");
    const chapter = page.locator("[role=button]").first();
    await chapter.click();

    // Should show topics inside
    await expect(page.locator("text=items")).toBeVisible();
  });

  test("should logout from dashboard", async ({ page }) => {
    await page.goto("/dashboard");
    await page.click('button:has-text("Sign out")');
    await page.waitForURL("/");
    await expect(page.locator("text=Dashboard")).not.toBeVisible();
  });
});

test.describe("Full Signup to Dashboard Flow", () => {
  test("should complete full signup and view syllabus", async ({ page }) => {
    // Navigate to signup
    await page.goto("/");
    await page.click("text=Sign up");
    await expect(page).toHaveURL(/\/signup/);

    // Fill form
    const timestamp = Date.now();
    await page.fill('input[type="email"]', `user-${timestamp}@test.com`);
    await page.fill('input[type="password"]', "TestPassword123");
    await page.fill('input[placeholder*="Name"]', "Test User");
    await page.click('input[type="checkbox"]');

    // Submit
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await page.waitForURL("/dashboard");
    await expect(page.locator("text=Dashboard")).toBeVisible();

    // Should see NEET 2026
    await expect(page.locator("text=NEET 2026")).toBeVisible();

    // Should see chapters
    await expect(page.locator("text=Physics")).toBeVisible();

    // Should be able to expand a chapter
    const firstChapter = page.locator("[role=button]").first();
    await firstChapter.click();
    await expect(page.locator("text=items")).toBeVisible();
  });
});
