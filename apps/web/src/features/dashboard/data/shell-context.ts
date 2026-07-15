import "server-only";

import { APP_NAME } from "@studyos/shared";

export type DashboardShellContext = {
  appName: string;
  serverRenderedAt: string;
};

/**
 * Server-only data for the dashboard shell. Swap for DB/API reads (syllabus, tenant, etc.)
 * without shipping that logic to the client bundle.
 */
export async function getDashboardShellContext(): Promise<DashboardShellContext> {
  await Promise.resolve();
  return {
    appName: APP_NAME,
    serverRenderedAt: new Date().toISOString(),
  };
}
