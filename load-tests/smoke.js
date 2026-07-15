/**
 * StudyOS — k6 load test suite.
 *
 * Usage:
 *   k6 run load-tests/smoke.js
 *   k6 run load-tests/load.js
 *   k6 run --vus 50 --duration 60s load-tests/stress.js
 *   k6 run --vus 100 --duration 120s load-tests/stress.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  stages: [
    { duration: '10s', target: 10 },
    { duration: '30s', target: 50 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  // Health check
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    'health is 200': (r) => r.status === 200,
    'health returns healthy': (r) => r.json('status') === 'healthy',
  });

  // Root endpoint
  const rootRes = http.get(`${BASE_URL}/`);
  check(rootRes, {
    'root is 200': (r) => r.status === 200,
  });

  sleep(1);
}

export function handleSummary(data) {
  return {
    'load-tests/results/smoke-summary.json': JSON.stringify(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
