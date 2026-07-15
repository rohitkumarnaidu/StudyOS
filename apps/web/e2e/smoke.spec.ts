import { expect, test } from "@playwright/test";

test.describe("smoke", () => {
  test("home renders StudyOS", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "StudyOS" })).toBeVisible();
  });
});
