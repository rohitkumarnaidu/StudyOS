# StudyOS — DevOps Setup

**Date:** 2026-05-18  
**Version:** 1.0  
**Scope:** CI/CD, monitoring, logging, infrastructure

---

## CI/CD Pipeline

### GitHub Actions Configuration

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '20'
  PYTHON_VERSION: '3.12'

jobs:
  # ─────────────────────────────────────────────
  # LINT & TYPECHECK
  # ─────────────────────────────────────────────
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          
      - name: Install pnpm
        uses: pnpm/action-setup@v3
        with:
          run_install: false
          
      - name: Get pnpm store path
        run: echo "STORE_PATH=$(pnpm store path)" >> $GITHUB_OUTPUT
        id: pnpm-store
        
      - name: Cache pnpm store
        uses: actions/cache@v4
        with:
          path: ${{ steps.pnpm-store.outputs.STORE_PATH }}
          key: ${{ runner.os }}-pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}
          
      - name: Install dependencies
        run: pnpm install --frozen-lockfile
        
      - name: API lint
        run: |
          cd apps/api
          uv run ruff check src
          uv run ruff format --check src
          
      - name: Web lint
        run: |
          cd apps/web
          pnpm lint
          
      - name: Web typecheck
        run: |
          cd apps/web
          pnpm typecheck

  # ─────────────────────────────────────────────
  # TESTS
  # ─────────────────────────────────────────────
  test-api:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          
      - name: Install uv
        run: pip install uv
        
      - name: Install API dependencies
        run: |
          cd apps/api
          uv sync
          
      - name: Run API tests
        run: |
          cd apps/api
          uv run pytest tests/ \
            --cov=studyos_api \
            --cov-report=xml \
            --cov-fail-under=90 \
            --junitxml=junit.xml
            
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: apps/api/coverage.xml
          flags: api
          
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: api-test-results
          path: apps/api/junit.xml

  test-web:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          
      - name: Install pnpm
        uses: pnpm/action-setup@v3
        with:
          run_install: false
          
      - name: Install dependencies
        run: pnpm install --frozen-lockfile
        
      - name: Run web tests
        run: |
          cd apps/web
          pnpm exec vitest run --coverage
          
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: apps/web/coverage/coverage-final.json
          flags: web

  test-e2e:
    runs-on: ubuntu-latest
    needs: [test-api, test-web]
    steps:
      - uses: actions/checkout@v4
      
      - name: Install dependencies
        run: pnpm install --frozen-lockfile
        
      - name: Install Playwright
        run: pnpm exec playwright install --with-deps
        
      - name: Run E2E tests
        run: pnpm exec playwright test
        env:
          BASE_URL: http://localhost:3000
          
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: e2e-results
          path: apps/web/playwright-report/

  # ─────────────────────────────────────────────
  # BUILD
  # ─────────────────────────────────────────────
  build:
    runs-on: ubuntu-latest
    needs: [test-api, test-web]
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Build API Docker image
        run: |
          docker build -t studyos-api:${{ github.sha }} ./apps/api
          
      - name: Build Web Docker image
        run: |
          docker build -t studyos-web:${{ github.sha }} ./apps/web
          
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker tag studyos-api:${{ github.sha }} ${{ secrets.DOCKER_REGISTRY }}/studyos-api:latest
          docker tag studyos-web:${{ github.sha }} ${{ secrets.DOCKER_REGISTRY }}/studyos-web:latest
          docker push ${{ secrets.DOCKER_REGISTRY }}/studyos-api:latest
          docker push ${{ secrets.DOCKER_REGISTRY }}/studyos-web:latest

  # ─────────────────────────────────────────────
  # DEPLOY (Production)
  # ─────────────────────────────────────────────
  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          # Add deployment commands here (e.g., kubectl, terraform, etc.)
```

---

## Monitoring Setup

### Sentry (Error Tracking)
```typescript
// apps/web/src/shared/lib/sentry.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});
```

### PostHog (Product Analytics)
```typescript
// apps/web/src/shared/lib/posthog.tsx
import posthog from "posthog-js";

posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || "https://app.posthog.com",
  person_profiles: "identified_only",
});
```

### Prometheus Metrics (API)
```python
# apps/api/src/studyos_api/core/metrics.py
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration")

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_DURATION.observe(duration)
    return response

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
```

---

## Logging Setup

### Structured Logging (API)
```python
# apps/api/src/studyos_api/core/logging.py
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()
logger.info("api.started", version="1.0.0", environment="production")
```

### Request Logging
```python
# apps/api/src/studyos_api/middleware/request_logging.py
@app.middleware("http")
async def log_requests(request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info("request.started",
        method=request.method,
        path=request.url.path,
        request_id=request_id
    )
    
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info("request.completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2),
        request_id=request_id
    )
    
    return response
```

---

## Infrastructure as Code

### Terraform (AWS Example)
```hcl
# infra/main.tf
provider "aws" {
  region = var.aws_region
}

resource "aws_ecs_cluster" "studyos" {
  name = "studyos-cluster"
}

resource "aws_ecs_task_definition" "api" {
  family                   = "studyos-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  
  container_definitions = jsonencode([{
    name  = "api"
    image = "${var.ecr_repository}/studyos-api:latest"
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    environment = [
      { name = "STUDYOS_APP_ENV", value = "production" },
      { name = "STUDYOS_DATABASE_URL", value = var.database_url },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = "/ecs/studyos-api"
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "api"
      }
    }
  }])
}

resource "aws_ecs_service" "api" {
  name            = "studyos-api-service"
  cluster         = aws_ecs_cluster.studyos.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 2
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [aws_security_group.api.id]
  }
}
```

---

## Alert Configuration

### Critical Alerts (Page immediately)
| Alert | Condition | Channel |
|-------|-----------|---------|
| **API Down** | Health check fails 3x | PagerDuty |
| **DB Down** | Connection refused | PagerDuty |
| **Error Rate > 5%** | 5xx errors > 5% for 5min | PagerDuty |
| **Response Time > 2s** | p95 latency > 2s for 5min | PagerDuty |

### Warning Alerts (Investigate within 1hr)
| Alert | Condition | Channel |
|-------|-----------|---------|
| **Error Rate > 1%** | 5xx errors > 1% for 10min | Slack |
| **CPU > 80%** | Sustained for 10min | Slack |
| **Memory > 85%** | Sustained for 10min | Slack |
| **Disk > 90%** | Any volume | Slack |

### Info Alerts (Review daily)
| Alert | Condition | Channel |
|-------|-----------|---------|
| **Deployment success** | New version deployed | Slack #deployments |
| **Backup completed** | Daily backup success | Slack #backups |
| **Certificate expiry** | < 30 days to expiry | Slack #alerts |

---

## Security Hardening

### Docker Security
```dockerfile
# apps/api/Dockerfile
FROM python:3.12-slim AS runtime

# Non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Read-only filesystem (except temp)
RUN mkdir -p /tmp && chmod 1777 /tmp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Network Security
- **VPC:** Private subnets for API and DB
- **Security Groups:** Restrict to necessary ports only
- **WAF:** Rate limiting, SQL injection protection
- **SSL/TLS:** TLS 1.2+ enforced
- **CORS:** Whitelist only allowed origins

### Secret Management
- **Development:** `.env` files (never committed)
- **CI/CD:** GitHub Secrets
- **Production:** AWS Secrets Manager / HashiCorp Vault
- **Rotation:** Automatic every 90 days
