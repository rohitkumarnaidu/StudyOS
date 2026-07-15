/**
 * StudyOS — Stress test for breaking point discovery.
 *
 * Gradually increases load until the service degrades.
 * Use to find maximum concurrent users and failure modes.
 *
 * Usage:
 *   k6 run load-tests/stress.js
 *   k6 run --vus 500 --duration 300s load-tests/stress.js
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  stages: [
    { duration: '1m', target: 50 },
    { duration: '2m', target: 200 },
    { duration: '2m', target: 500 },
    { duration: '2m', target: 1000 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.1'],
  },
};

export default function () {
  group('Concurrent syllabus reads', function () {
    const res = http.get(`${BASE_URL}/v1/syllabus/chapters`);
    check(res, {
      'syllabus responds': (r) => r.status === 200 || r.status === 429,
    });
  });

  group('Concurrent health checks', function () {
    const res = http.get(`${BASE_URL}/health`);
    check(res, {
      'health responds': (r) => r.status === 200 || r.status === 503,
    });
  });

  sleep(0.5);
}

export function handleSummary(data) {
  return {
    'load-tests/results/stress-summary.json': JSON.stringify(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
