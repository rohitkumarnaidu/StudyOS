import base from "@studyos/eslint-config/base";

/** @type {import("eslint").Linter.Config[]} */
export default [{ ignores: ["eslint.config.mjs", "vitest.config.ts"] }, ...base];
