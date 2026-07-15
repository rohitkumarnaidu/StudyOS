# StudyOS — Enterprise Testing Guidelines

**Date:** 2026-05-18  
**Version:** 2.0  
**Scope:** Full-stack testing architecture (API + Web + E2E)

---

## Testing Philosophy

StudyOS follows the **Testing Pyramid** with emphasis on fast, reliable unit tests and strategic integration/E2E coverage.

```
        ┌─────────────┐
        │    E2E      │  ← 5%  (Critical user journeys)
        ├─────────────┤
        │ Integration │  ← 20% (API contracts, DB interactions)
        ├─────────────┤
        │    Unit     │  ← 75% (Pure functions, components, services)
        └─────────────┘
```

### Principles
1. **Tests are documentation** — Name tests after behavior, not implementation
2. **Fast feedback** — Unit tests <1s, integration <5s, E2E <30s
3. **Deterministic** — No flaky tests; mock external dependencies
4. **Maintainable** — Shared fixtures, clear arrange-act-assert structure
5. **Coverage targets** — API: 90%+, Web: 80%+, E2E: Critical paths only

---

## Testing Architecture

### Folder Structure
```
apps/api/tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Pure unit tests
│   ├── test_auth_service.py
│   ├── test_tokens.py
│   ├── test_passwords.py
│   └── test_cache.py
├── integration/             # API + DB integration
│   ├── conftest.py          # DB fixtures
│   └── test_api_real.py
├── api/                     # Route-level tests
│   ├── test_auth_routes.py
│   ├── test_progress_routes.py
│   └── test_privacy_routes.py
├── services/                # Service layer tests
│   ├── test_webhooks.py
│   ├── test_feature_flags.py
│   └── test_refresh_sessions.py
├── ai/                      # AI module tests
│   ├── test_service.py
│   ├── test_usage.py
│   └── test_mcp_registry.py
└── core/                    # Core module tests
    ├── test_config.py
    ├── test_errors.py
    └── test_telemetry.py

apps/web/src/
├── __tests__/               # Colocated tests
│   ├── components/
│   │   ├── button.test.tsx
│   │   └── form-field.test.tsx
│   └── hooks/
│       └── use-translation.test.ts
├── features/
│   ├── auth/
│   │   ├── __tests__/
│   │   │   └── login-form.test.tsx
│   │   └── components/
│   └── progress/
│       ├── __tests__/
│       │   └── progress-ring.test.tsx
│       └── components/
└── e2e/                     # Playwright E2E
    ├── auth-and-syllabus.spec.ts
    └── progress-tracking.spec.ts
```

---

## API Testing (Python/FastAPI)

### Unit Tests
**Purpose:** Test pure functions and isolated services.

```python
# tests/unit/test_auth_service.py
class TestAuthService:
    def test_resolve_user_with_valid_token(self) -> None:
        """Should return User dict for valid JWT."""
        settings = Settings(jwt_secret="test", jwt_issuer="test")
        token = mint_access_token(settings, sub="user-1", roles=["student"])
        
        service = AuthService()
        user = service.resolve_optional_user(token)
        
        assert user is not None
        assert user["sub"] == "user-1"
        assert "student" in user["roles"]

    def test_resolve_user_with_invalid_token(self) -> None:
        """Should return None for malformed JWT."""
        service = AuthService()
        assert service.resolve_optional_user("invalid-token") is None
```

### Integration Tests
**Purpose:** Test API routes with real database interactions.

```python
# tests/integration/test_api_real.py
class TestAuthIntegration:
    @pytest.mark.asyncio
    async def test_login_success(self, api_client: AsyncClient) -> None:
        """Should return access token for valid credentials."""
        resp = await api_client.post("/v1/auth/login", json={
            "email": "test@studyos.app",
            "password": "Test1234!",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
```

### Route Tests (with mocked DB)
**Purpose:** Test route behavior without database dependency.

```python
# tests/api/test_privacy_routes.py
class TestPrivacyRoutesExport:
    def test_export_requires_auth(self, app) -> None:
        """Should reject unauthenticated export requests."""
        with TestClient(app, base_url="http://testserver") as client:
            resp = client.get("/v1/privacy/export")
            assert resp.status_code in (401, 403)

    def test_export_success_empty_data(self, app, auth_headers) -> None:
        """Should return empty export structure for new user."""
        _mock_pool_for_app(app)
        with TestClient(app, base_url="http://testserver") as client:
            resp = client.get("/v1/privacy/export", headers=auth_headers)
            assert resp.status_code == 200
            assert resp.json()["success"] is True
```

### Test Markers
```python
# pyproject.toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests requiring database",
    "ai: marks tests requiring AI provider mocks",
    "auth: marks authentication-related tests",
]
```

### Running Tests
```bash
# All tests
uv run pytest tests/

# Unit only (fast)
uv run pytest tests/ -m "not integration"

# With coverage
uv run pytest tests/ --cov=studyos_api --cov-report=html

# Specific test file
uv run pytest tests/api/test_auth_routes.py -v
```

---

## Web Testing (TypeScript/Next.js)

### Component Tests (Vitest + Testing Library)
**Purpose:** Test UI components in isolation.

```typescript
// src/shared/components/__tests__/button.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from '../ui/button'

describe('Button', () => {
  it('renders with children', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toHaveTextContent('Click me')
  })

  it('calls onClick when clicked', async () => {
    const onClick = vi.fn()
    const user = userEvent.setup()
    
    render(<Button onClick={onClick}>Click me</Button>)
    await user.click(screen.getByRole('button'))
    
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('shows loading state', () => {
    render(<Button loading>Loading...</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

### Hook Tests
**Purpose:** Test custom hooks with mocked dependencies.

```typescript
// src/shared/hooks/__tests__/use-translation.test.ts
import { renderHook } from '@testing-library/react'
import { useTranslation } from '../use-translation'

describe('useTranslation', () => {
  it('returns translated text for known key', () => {
    const { result } = renderHook(() => useTranslation('en'))
    expect(result.current.t('auth.login')).toBe('Sign in')
  })

  it('returns key for unknown translation', () => {
    const { result } = renderHook(() => useTranslation('en'))
    expect(result.current.t('unknown.key')).toBe('unknown.key')
  })
})
```

### Mock Systems
**Purpose:** Isolate tests from external dependencies.

```typescript
// __mocks__/next/navigation.ts
export const useRouter = vi.fn(() => ({
  push: vi.fn(),
  replace: vi.fn(),
  prefetch: vi.fn(),
}))

export const usePathname = vi.fn(() => '/dashboard')

// __mocks__/@supabase/supabase-js.ts
export const createClient = vi.fn(() => ({
  auth: {
    signInWithOAuth: vi.fn(),
    signOut: vi.fn(),
    getUser: vi.fn(),
  },
  from: vi.fn(() => ({
    select: vi.fn().mockReturnThis(),
    insert: vi.fn().mockReturnThis(),
    update: vi.fn().mockReturnThis(),
    single: vi.fn(),
  })),
}))
```

### Running Tests
```bash
# All tests
pnpm exec vitest run

# Watch mode
pnpm exec vitest

# With coverage
pnpm exec vitest run --coverage

# Specific test
pnpm exec vitest run src/shared/components/__tests__/button.test.tsx
```

---

## E2E Testing (Playwright)

**Purpose:** Test critical user journeys end-to-end.

### Test Structure
```typescript
// e2e/auth-and-syllabus.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test('user can login with demo credentials', async ({ page }) => {
    await page.goto('/login')
    await page.fill('[name="email"]', 'demo@studyos.app')
    await page.fill('[name="password"]', 'demo')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveURL('/dashboard')
    await expect(page.getByText('Welcome back')).toBeVisible()
  })

  test('user can navigate to syllabus', async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.fill('[name="email"]', 'demo@studyos.app')
    await page.fill('[name="password"]', 'demo')
    await page.click('button[type="submit"]')
    
    // Navigate to syllabus
    await page.getByRole('link', { name: 'Syllabus' }).click()
    await expect(page).toHaveURL('/syllabus')
    await expect(page.getByText('Physics')).toBeVisible()
  })
})

test.describe('Progress Tracking', () => {
  test('user can toggle subtopic completion', async ({ page }) => {
    // ... test implementation
  })
})
```

### Running E2E Tests
```bash
# Run all E2E tests
pnpm exec playwright test

# Run with UI
pnpm exec playwright test --ui

# Run specific test
pnpm exec playwright test e2e/auth-and-syllabus.spec.ts

# Generate trace for debugging
pnpm exec playwright test --trace on
```

---

## CI Test Integration

### GitHub Actions Pipeline
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          
      - name: Install pnpm
        uses: pnpm/action-setup@v3
        
      - name: Install deps
        run: pnpm install
        
      - name: API tests
        run: |
          cd apps/api
          uv run pytest tests/ --cov=studyos_api --cov-fail-under=90
          
      - name: Web tests
        run: |
          cd apps/web
          pnpm exec vitest run --coverage
          
      - name: E2E tests
        run: pnpm exec playwright test
```

### Test Quality Gates
| Gate | Threshold | Action |
|------|-----------|--------|
| API Coverage | 90%+ | Fail CI if below |
| Web Coverage | 80%+ | Fail CI if below |
| Test Duration | <5min total | Alert if exceeded |
| Flaky Tests | 0 | Quarantine flaky tests |
| E2E Pass Rate | 100% | Block merge if failed |

---

## Test Utilities

### API Test Fixtures
```python
# tests/conftest.py
@pytest.fixture
def auth_headers():
    """Generate valid auth headers for testing."""
    settings = get_settings()
    token = mint_access_token(settings, sub=str(uuid.uuid4()), roles=["student"])
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_db_pool():
    """Create a mock asyncpg pool."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow = AsyncMock(return_value=None)
    mock_conn.fetch = AsyncMock(return_value=[])
    mock_conn.execute = AsyncMock(return_value="")
    
    mock_pool = AsyncMock()
    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    return mock_pool
```

### Web Test Utilities
```typescript
// test-utils.tsx
import { render } from '@testing-library/react'
import type { RenderOptions } from '@testing-library/react'

const AllProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <QueryClientProvider client={new QueryClient()}>
      <ThemeProvider>{children}</ThemeProvider>
    </QueryClientProvider>
  )
}

const customRender = (ui: React.ReactElement, options?: RenderOptions) =>
  render(ui, { wrapper: AllProviders, ...options })

export * from '@testing-library/react'
export { customRender as render }
```

---

## Coverage Targets by Module

| Module | Target | Current | Status |
|--------|--------|---------|--------|
| **API Core** | 95% | 88% | ⚠️ |
| **API Services** | 90% | 85% | ⚠️ |
| **API Routes** | 95% | 92% | ✅ |
| **AI Module** | 85% | 75% | ⚠️ |
| **Web Components** | 85% | 70% | ⚠️ |
| **Web Hooks** | 80% | 60% | ⚠️ |
| **E2E Critical Paths** | 100% | 60% | ⚠️ |

---

## Testing Anti-Patterns to Avoid

1. **Testing implementation details** — Test behavior, not internals
2. **Over-mocking** — Mock only external dependencies, not your own code
3. **Brittle selectors** — Use `getByRole` over CSS selectors
4. **Shared state between tests** — Each test should be independent
5. **Sleep-based waits** — Use proper async/await or waitFor
6. **Testing third-party libraries** — Trust tested libraries
7. **100% coverage obsession** — Focus on critical paths, not vanity metrics
