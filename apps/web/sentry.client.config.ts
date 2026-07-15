import { withSentryConfig } from "@sentry/nextjs";

const sentryConfig = {
  org: process.env.SENTRY_ORG ?? "studyos",
  project: process.env.SENTRY_PROJECT ?? "studyos-web",
  silent: true,
  widenClientFileUpload: true,
  hideSourceMaps: true,
  disableLogger: true,
  tunnelRoute: "/monitoring-tunnel",
};

export default withSentryConfig(
  {},
  sentryConfig,
);
