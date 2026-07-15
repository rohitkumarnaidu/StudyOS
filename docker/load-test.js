// StudyOS — k6 Load Test Script
// Usage: k6 run docker/load-test.js
//        k6 run --vus 50 --duration 60s docker/load-test.js

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate } from "k6/metrics";

// Custom metrics
const errorRate = new Rate("http_errors");

// Test configuration
const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const VUS = parseInt(__ENV.VUS || "10");
const DURATION = __ENV.DURATION || "30s";

export const options = {
  stages: [
    { duration: "10s", target: VUS },      // Ramp up
    { duration: DURATION, target: VUS },   // Stay at load
    { duration: "10s", target: 0 },        // Ramp down
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"],      // 95% of requests should be below 500ms
    http_req_failed: ["rate<0.05"],        // Error rate should be less than 5%
    http_errors: ["rate<0.1"],             // Custom error rate threshold
  },
};

// Test data
const testCredentials = {
  email: "demo@studyos.app",
  password: "demo",
};

export function setup() {
  // Login once to get tokens
  const loginRes = http.post(
    `${BASE_URL}/v1/auth/login`,
    JSON.stringify(testCredentials),
    { headers: { "Content-Type": "application/json" } }
  );

  check(loginRes, {
    "login successful": (r) => r.status === 200,
  });

  const tokens = loginRes.json();
  return {
    accessToken: tokens?.access_token || "",
    refreshToken: tokens?.refresh_token || "",
  };
}

export default function (data) {
  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${data.accessToken}`,
  };

  // Test 1: Health check (light endpoint)
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    "health check returns 200": (r) => r.status === 200,
    "health check response time < 100ms": (r) => r.timings.duration < 100,
  });
  errorRate.add(healthRes.status >= 400);

  // Test 2: Service root
  const rootRes = http.get(`${BASE_URL}/`);
  check(rootRes, {
    "service root returns 200": (r) => r.status === 200,
  });
  errorRate.add(rootRes.status >= 400);

  // Test 3: Syllabus endpoint (read-heavy)
  const syllabusRes = http.get(`${BASE_URL}/v1/syllabus`, { headers });
  check(syllabusRes, {
    "syllabus endpoint returns 200": (r) => r.status === 200,
    "syllabus response time < 1000ms": (r) => r.timings.duration < 1000,
  });
  errorRate.add(syllabusRes.status >= 400);

  sleep(1);
}

export function handleSummary(data) {
  return {
    "stdout": textSummary(data),
    "docker/load-test-results.json": JSON.stringify(data),
  };
}

function textSummary(data) {
  const metrics = data.metrics;
  return `
═══════════════════════════════════════════
  StudyOS Load Test Results
═══════════════════════════════════════════

  Requests:     ${metrics.http_reqs.values.count}
  Failed:       ${metrics.http_req_failed.values.rate * 100}%
  Duration:     ${metrics.http_req_duration.values.med}ms (med)
                ${metrics.http_req_duration.values["p(95)"]}ms (p95)
                ${metrics.http_req_duration.values.max}ms (max)
  Data Sent:    ${(metrics.data_sent.values.count / 1024).toFixed(1)} KB
  Data Received: ${(metrics.data_received.values.count / 1024).toFixed(1)} KB

═══════════════════════════════════════════
`;
}
