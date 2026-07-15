/**
 * StudyOS — Comprehensive k6 stress test suite.
 *
 * Test types:
 * - Ramp-up stress test: 1 -> 500 -> 1000 -> 500 -> 1 VUs over 10 minutes
 * - Spike test: sudden burst from 0 -> 1000 VUs
 * - Soak test: 100 VUs for 30 minutes (memory leak detection)
 * - Breakpoint test: find max VUs before errors
 *
 * Each test targets: auth endpoints, AI chat, quiz creation, notes search, analytics
 *
 * Usage:
 *   k6 run load-tests/stress-comprehensive.js
 *   k6 run --out json=results/stress-rampup.json load-tests/stress-comprehensive.js --scenario rampup
 *   k6 run --out json=results/stress-spike.json load-tests/stress-comprehensive.js --scenario spike
 *   k6 run --out json=results/stress-soak.json load-tests/stress-comprehensive.js --scenario soak
 *   k6 run --out json=results/stress-breakpoint.json load-tests/stress-comprehensive.js --scenario breakpoint
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  scenarios: {
    rampup: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '2m', target: 500 },
        { duration: '2m', target: 1000 },
        { duration: '2m', target: 500 },
        { duration: '2m', target: 100 },
        { duration: '2m', target: 1 },
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'rampup' },
      exec: 'rampupTest',
    },
    spike: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '10s', target: 0 },
        { duration: '30s', target: 1000 },
        { duration: '1m', target: 1000 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'spike' },
      exec: 'spikeTest',
    },
    soak: {
      executor: 'ramping-vus',
      startVUs: 10,
      stages: [
        { duration: '5m', target: 100 },
        { duration: '25m', target: 100 },
        { duration: '5m', target: 0 },
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'soak' },
      exec: 'soakTest',
    },
    breakpoint: {
      executor: 'ramping-vus',
      startVUs: 10,
      stages: [
        { duration: '2m', target: 100 },
        { duration: '2m', target: 200 },
        { duration: '2m', target: 300 },
        { duration: '2m', target: 400 },
        { duration: '2m', target: 500 },
        { duration: '2m', target: 750 },
        { duration: '2m', target: 1000 },
        { duration: '1m', target: 0 },
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'breakpoint' },
      exec: 'breakpointTest',
    },
  },
  thresholds: {
    'http_req_duration{test_type:rampup}': ['p(50)<500', 'p(95)<2000', 'p(99)<5000'],
    'http_req_duration{test_type:spike}': ['p(50)<1000', 'p(95)<3000', 'p(99)<8000'],
    'http_req_duration{test_type:soak}': ['p(50)<300', 'p(95)<1000', 'p(99)<3000'],
    'http_req_duration{test_type:breakpoint}': ['p(50)<1000', 'p(95)<3000'],
    'http_req_failed{test_type:rampup}': ['rate<0.05'],
    'http_req_failed{test_type:spike}': ['rate<0.1'],
    'http_req_failed{test_type:soak}': ['rate<0.02'],
    'http_req_failed{test_type:breakpoint}': ['rate<0.15'],
    'http_reqs{test_type:soak}': ['rate>10'],
  },
};

const headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

function runAuthTests() {
  group('Auth', function () {
    const loginRes = http.post(`${BASE_URL}/v1/auth/login`, JSON.stringify({
      email: 'demo@studyos.app',
      password: 'demo',
    }), { headers });

    check(loginRes, {
      'auth login responds': (r) => r.status === 200 || r.status === 401 || r.status === 429,
      'auth login <500ms': (r) => r.timings.duration < 500,
    });

    const meRes = http.get(`${BASE_URL}/v1/me`, { headers });
    check(meRes, {
      'me endpoint responds': (r) => r.status === 200 || r.status === 401 || r.status === 429,
      'me <300ms': (r) => r.timings.duration < 300,
    });
  });
}

function runSyllabusTests() {
  group('Syllabus', function () {
    const examsRes = http.get(`${BASE_URL}/v1/syllabus/exams`, { headers });
    check(examsRes, {
      'exams responds': (r) => r.status === 200 || r.status === 429,
      'exams <300ms': (r) => r.timings.duration < 300,
      'exams returns data array': (r) => {
        if (r.status === 200) {
          const body = r.json();
          return body && Array.isArray(body.data);
        }
        return true;
      },
    });

    const chaptersRes = http.get(`${BASE_URL}/v1/syllabus/chapters`, { headers });
    check(chaptersRes, {
      'chapters responds': (r) => r.status === 200 || r.status === 429,
      'chapters <300ms': (r) => r.timings.duration < 300,
    });
  });
}

function runQuizTests() {
  group('Quiz', function () {
    const createRes = http.post(`${BASE_URL}/v1/quizzes`, JSON.stringify({
      question_count: 5,
      quiz_type: 'practice',
      difficulty: 'medium',
    }), { headers });

    check(createRes, {
      'quiz create responds': (r) => [200, 401, 403, 429, 500].includes(r.status),
      'quiz create <1000ms': (r) => r.timings.duration < 1000,
    });

    const mistakesRes = http.get(`${BASE_URL}/v1/quizzes/mistakes`, { headers });
    check(mistakesRes, {
      'mistakes list responds': (r) => [200, 401, 403, 429, 500].includes(r.status),
      'mistakes list <500ms': (r) => r.timings.duration < 500,
    });
  });
}

function runNotesTests() {
  group('Notes', function () {
    const listRes = http.get(`${BASE_URL}/v1/notes`, { headers });
    check(listRes, {
      'notes list responds': (r) => [200, 401, 403, 429, 500].includes(r.status),
      'notes list <500ms': (r) => r.timings.duration < 500,
    });

    const searchRes = http.get(`${BASE_URL}/v1/notes/search`, {
      headers,
      params: { q: 'test' },
    });
    check(searchRes, {
      'notes search responds': (r) => [200, 401, 403, 429, 500].includes(r.status),
      'notes search <500ms': (r) => r.timings.duration < 500,
    });
  });
}

function runAnalyticsTests() {
  group('Analytics', function () {
    const overviewRes = http.get(`${BASE_URL}/v1/analytics/overview`, { headers });
    check(overviewRes, {
      'analytics overview responds': (r) => [200, 401, 403, 429, 500].includes(r.status),
      'analytics overview <500ms': (r) => r.timings.duration < 500,
    });

    const dailyRes = http.get(`${BASE_URL}/v1/analytics/daily`, { headers });
    check(dailyRes, {
      'analytics daily responds': (r) => [200, 401, 403, 429, 500].includes(r.status),
      'analytics daily <500ms': (r) => r.timings.duration < 500,
    });

    const subjectsRes = http.get(`${BASE_URL}/v1/analytics/subjects`, { headers });
    check(subjectsRes, {
      'analytics subjects responds': (r) => [200, 401, 403, 429, 500].includes(r.status),
      'analytics subjects <500ms': (r) => r.timings.duration < 500,
    });

    const trendsRes = http.get(`${BASE_URL}/v1/analytics/quiz-trends`, { headers });
    check(trendsRes, {
      'analytics quiz trends responds': (r) => [200, 401, 403, 429, 500].includes(r.status),
      'analytics quiz trends <500ms': (r) => r.timings.duration < 500,
    });

    const weakRes = http.get(`${BASE_URL}/v1/analytics/weak-areas`, { headers });
    check(weakRes, {
      'analytics weak areas responds': (r) => [200, 401, 403, 429, 500].includes(r.status),
      'analytics weak areas <500ms': (r) => r.timings.duration < 500,
    });
  });
}

function runAITests() {
  group('AI', function () {
    const chatRes = http.post(`${BASE_URL}/v1/ai/chat`, JSON.stringify({
      messages: [{ role: 'user', content: 'What is the capital of France?' }],
    }), { headers });

    check(chatRes, {
      'ai chat responds': (r) => [200, 401, 403, 429, 500, 502, 503].includes(r.status),
      'ai chat <5000ms': (r) => r.timings.duration < 5000,
    });
  });
}

function runHealthTests() {
  group('Health & Meta', function () {
    const healthRes = http.get(`${BASE_URL}/health`);
    check(healthRes, {
      'health responds': (r) => r.status === 200,
      'health <100ms': (r) => r.timings.duration < 100,
    });

    const rootRes = http.get(`${BASE_URL}/`);
    check(rootRes, {
      'root responds': (r) => r.status === 200,
      'root <100ms': (r) => r.timings.duration < 100,
    });
  });
}

function runProgressTests() {
  group('Progress', function () {
    const streakRes = http.get(`${BASE_URL}/v1/progress/streak`, { headers });
    check(streakRes, {
      'streak responds': (r) => [200, 401, 403, 429, 500].includes(r.status),
      'streak <500ms': (r) => r.timings.duration < 500,
    });
  });
}

function runRoadmapTests() {
  group('Roadmap', function () {
    const priorityRes = http.get(`${BASE_URL}/v1/roadmap/priority-scores`, { headers });
    check(priorityRes, {
      'priority scores responds': (r) => [200, 401, 403, 429, 500, 503].includes(r.status),
      'priority scores <1000ms': (r) => r.timings.duration < 1000,
    });

    const predictRes = http.get(`${BASE_URL}/v1/roadmap/predict`, { headers });
    check(predictRes, {
      'prediction responds': (r) => [200, 401, 403, 429, 500, 503].includes(r.status),
      'prediction <1000ms': (r) => r.timings.duration < 1000,
    });
  });
}

function runMistakeIntelligenceTests() {
  group('Mistake Intelligence', function () {
    const statsRes = http.get(`${BASE_URL}/v1/mistakes/mistakes/stats`, { headers });
    check(statsRes, {
      'mistake stats responds': (r) => [200, 401, 403, 429, 500].includes(r.status),
      'mistake stats <500ms': (r) => r.timings.duration < 500,
    });

    const reportRes = http.get(`${BASE_URL}/v1/mistakes/mistakes/report`, { headers });
    check(reportRes, {
      'mistake report responds': (r) => [200, 401, 403, 429, 500].includes(r.status),
      'mistake report <1000ms': (r) => r.timings.duration < 1000,
    });
  });
}

export function rampupTest() {
  runHealthTests();
  runAuthTests();
  runSyllabusTests();
  runQuizTests();
  runNotesTests();
  runAnalyticsTests();
  runProgressTests();
  runRoadmapTests();
  runMistakeIntelligenceTests();
  runAITests();
  sleep(1);
}

export function spikeTest() {
  group('Spike - Core Endpoints', function () {
    const healthRes = http.get(`${BASE_URL}/health`);
    check(healthRes, {
      'spike health responds': (r) => r.status === 200 || r.status === 503,
    });

    const examsRes = http.get(`${BASE_URL}/v1/syllabus/exams`, { headers });
    check(examsRes, {
      'spike exams responds': (r) => r.status === 200 || r.status === 429 || r.status === 503,
    });

    const loginRes = http.post(`${BASE_URL}/v1/auth/login`, JSON.stringify({
      email: 'demo@studyos.app',
      password: 'demo',
    }), { headers });
    check(loginRes, {
      'spike login responds': (r) => [200, 401, 429, 503].includes(r.status),
    });
  });
  sleep(0.5);
}

export function soakTest() {
  runHealthTests();
  runAuthTests();
  runSyllabusTests();
  runQuizTests();
  runNotesTests();
  runAnalyticsTests();
  runProgressTests();
  runRoadmapTests();
  runMistakeIntelligenceTests();
  sleep(2);
}

export function breakpointTest() {
  runHealthTests();
  runAuthTests();
  runSyllabusTests();
  runQuizTests();
  runNotesTests();
  runAnalyticsTests();
  runProgressTests();
  runRoadmapTests();
  runMistakeIntelligenceTests();
  runAITests();
  sleep(0.5);
}

export function handleSummary(data) {
  const testType = data.state.testRunDurationMs > 0 ? 'comprehensive' : 'unknown';

  return {
    [`load-tests/results/stress-${testType}-summary.json`]: JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
