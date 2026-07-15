/**
 * Small runtime guard for values that must exist after optional chaining / parsing.
 * Prefer Zod `.parse` at boundaries; use this only when narrowing is intentionally local.
 */
export function assertDefined<T>(value: T | null | undefined, message = "Expected a defined value"): asserts value is T {
  if (value === null || value === undefined) {
    throw new Error(message);
  }
}
