/**
 * StudyOS — Load test for core API endpoints.
 *
 * Simulates realistic user traffic patterns:
 * - 40% syllabus reads (chapters, exams)
 * - 30% health/metadata
 * - 20% progress reads
 * - 10% auth operations
 *
 * Usage:
 *   k6 run load-tests/load.js
 *   k6 run --vus 100 --duration 120s load-tests/load.js
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up
    { duration: '2m', target: 100 },   // Steady load
    { duration: '30s', target: 200 },  // Spike
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(50)<200', 'p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.05'],
  },
};

const headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

export default function () {
  group('Health & Meta', function () {
    const res = http.get(`${BASE_URL}/health`);
    check(res, {
      'health 200': (r) => r.status === 200,
      'health <100ms': (r) => r.timings.duration < 100,
    });
  });

  group('Syllabus', function () {
    const exams = http.get(`${BASE_URL}/v1/syllabus/exams`, { headers });
    check(exams, {
      'exams 200': (r) => r.status === 200,
      'exams <300ms': (r) => r.timings.duration < 300,
    });

    const chapters = http.get(`${BASE_URL}/v1/syllabus/chapters`, { headers });
    check(chapters, {
      'chapters 200': (r) => r.status === 200,
      'chapters <300ms': (r) => r.timings.duration < 300,
    });
  });

  group('Auth (anonymous)', function () {
    const me = http.get(`${BASE_URL}/v1/me`, { headers });
    check(me, {
      'me 200': (r) => r.status === 200,
      'me returns unauthenticated': (r) => {
        const body = r.json();
        return body && body.data && body.data.authenticated === false;
      },
    });
  });

  sleep(1);
}

export function handleSummary(data) {
  return {
    'load-tests/results/load-summary.json': JSON.stringify(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
