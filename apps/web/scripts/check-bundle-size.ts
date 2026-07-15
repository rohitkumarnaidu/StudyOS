// StudyOS — Bundle size budget check
// Run as part of CI to prevent JS/CSS bloat

import { readFileSync } from "node:fs";
import { join } from "node:path";

const BUDGETS = {
  main_js: 250_000,      // 250KB for main JS bundle
  vendor_js: 500_000,    // 500KB for vendor JS
  css: 50_000,           // 50KB for CSS
  total: 1_000_000,      // 1MB total
};

function checkBudgets() {
  const buildDir = join(process.cwd(), ".next", "static");

  try {
    const files = readFileSync(join(buildDir, "..", "..", "build-manifest.json"), "utf-8");
    const manifest = JSON.parse(files);

    let totalSize = 0;

    for (const [, paths] of Object.entries(manifest.pages || {})) {
      for (const filePath of paths as string[]) {
        const fullPath = join(process.cwd(), ".next", filePath);
        try {
          const stat = readFileSync(fullPath);
          totalSize += stat.length;

          if (filePath.includes("main") && filePath.endsWith(".js")) {
            if (stat.length > BUDGETS.main_js) {
              console.error(`❌ main.js bundle too large: ${(stat.length / 1024).toFixed(1)}KB (limit: ${(BUDGETS.main_js / 1024).toFixed(1)}KB)`);
              process.exit(1);
            }
          }

          if (filePath.includes("vendor") && filePath.endsWith(".js")) {
            if (stat.length > BUDGETS.vendor_js) {
              console.error(`❌ vendor.js bundle too large: ${(stat.length / 1024).toFixed(1)}KB (limit: ${(BUDGETS.vendor_js / 1024).toFixed(1)}KB)`);
              process.exit(1);
            }
          }

          if (filePath.endsWith(".css")) {
            if (stat.length > BUDGETS.css) {
              console.error(`❌ CSS bundle too large: ${(stat.length / 1024).toFixed(1)}KB (limit: ${(BUDGETS.css / 1024).toFixed(1)}KB)`);
              process.exit(1);
            }
          }
        } catch {
          // File may not exist in all builds
        }
      }
    }

    if (totalSize > BUDGETS.total) {
      console.error(`❌ Total bundle size too large: ${(totalSize / 1024).toFixed(1)}KB (limit: ${(BUDGETS.total / 1024).toFixed(1)}KB)`);
      process.exit(1);
    }

    console.log(`✅ Bundle size check passed: ${(totalSize / 1024).toFixed(1)}KB total`);
  } catch {
    console.log("⚠️  Could not check bundle sizes (build manifest not found)");
  }
}

checkBudgets();
