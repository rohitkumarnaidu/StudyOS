import { validateServerEnv, getPublicEnv } from "@studyos/config";

let _validated = false;

/**
 * Validate all environment variables at startup.
 * Call this once during app initialization.
 */
export function validateEnv() {
  if (_validated) return;

  try {
    validateServerEnv();
    getPublicEnv();
    _validated = true;
  } catch (error) {
    console.error("Environment validation failed:", error);
    throw error;
  }
}
