import eslint from "@eslint/js";
import tseslint from "typescript-eslint";

/** @type {import("eslint").Linter.Config[]} */
export default tseslint.config(eslint.configs.recommended, ...tseslint.configs.strict, {
  languageOptions: {
    parserOptions: { projectService: true },
  },
  rules: {
    "@typescript-eslint/consistent-type-imports": [
      "error",
      { prefer: "type-imports", fixStyle: "inline-type-imports" },
    ],
  },
});
