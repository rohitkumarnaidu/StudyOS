# SKILL_FRONTEND.md
# StudyOS — Frontend Patterns & Conventions
# Read before generating ANY React component, hook, page, or routing code

---

## 1. PROJECT STRUCTURE (canonical — never deviate)

```
apps/web/
├── src/
│   ├── app/                          ← Next.js 16 App Router
│   │   ├── layout.tsx                ← Root layout (SessionProvider, Sentry, PostHog)
│   │   ├── providers.tsx             ← React Query + theme providers
│   │   ├── globals.css               ← Tailwind v4 CSS-first config
│   │   ├── manifest.ts               ← PWA manifest
│   │   ├── sw.ts                     ← Service worker
│   │   ├── error.tsx                 ← Global error boundary
│   │   ├── (app)/                    ← Authenticated route group
│   │   │   ├── layout.tsx            ← App shell (navbar, sidebar)
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── syllabus/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [chapterId]/page.tsx
│   │   │   ├── notes/
│   │   │   │   └── page.tsx
│   │   │   ├── roadmap/
│   │   │   │   └── page.tsx
│   │   │   ├── quiz/
│   │   │   │   └── page.tsx
│   │   │   ├── analytics/
│   │   │   │   └── page.tsx
│   │   │   └── settings/
│   │   │       └── page.tsx
│   │   ├── (auth)/                   ← Auth route group
│   │   │   ├── login/page.tsx
│   │   │   ├── signup/page.tsx
│   │   │   └── forgot-password/page.tsx
│   │   ├── (marketing)/              ← Public route group
│   │   │   └── page.tsx              ← Landing page
│   │   └── api/                      ← BFF API routes
│   │       ├── auth/
│   │       │   ├── login/route.ts
│   │       │   ├── signup/route.ts
│   │       │   ├── logout/route.ts
│   │       │   ├── refresh/route.ts
│   │       │   ├── session/route.ts
│   │       │   └── callback/route.ts  ← Supabase OAuth callback
│   │       └── internal/             ← Internal proxy to FastAPI
│   │
│   ├── features/                     ← Feature modules
│   │   ├── auth/
│   │   │   ├── components/           ← LoginForm, SignupForm
│   │   │   ├── hooks/                ← useLogin, useSignup
│   │   │   └── api.ts                ← Auth API client functions
│   │   ├── progress/
│   │   │   ├── components/           ← ProgressRing, StreakBadge
│   │   │   ├── hooks/                ← useToggleSubtopic
│   │   │   └── api.ts
│   │   ├── notes/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── api.ts
│   │   ├── ai/
│   │   │   ├── components/           ← AIChatPanel
│   │   │   ├── hooks/                ← useAIChat
│   │   │   └── api.ts
│   │   └── syllabus/
│   │       ├── components/
│   │       ├── hooks/
│   │       └── api.ts
│   │
│   ├── shared/                       ← Shared code
│   │   ├── components/
│   │   │   ├── ui/                   ← shadcn/ui primitives (cva variants)
│   │   │   │   ├── button.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   ├── tabs.tsx
│   │   │   │   ├── badge.tsx
│   │   │   │   ├── progress.tsx
│   │   │   │   └── ...
│   │   │   ├── form/                 ← RHF + Zod form components
│   │   │   └── layout/               ← Navbar, Sidebar, AppShell
│   │   ├── config/
│   │   │   ├── routes.ts             ← Centralized route constants
│   │   │   ├── i18n.ts               ← Locale config (en/hi/ta)
│   │   │   └── translations.ts       ← Translation dictionaries
│   │   ├── hooks/                    ← Shared hooks
│   │   │   ├── useTranslation.ts
│   │   │   └── useMediaQuery.ts
│   │   ├── stores/                   ← Zustand stores
│   │   │   └── ui.store.ts
│   │   ├── lib/
│   │   │   ├── supabase/             ← Supabase client (browser + server)
│   │   │   ├── query-client.ts       ← React Query presets
│   │   │   ├── sentry.ts             ← Sentry config
│   │   │   ├── posthog.tsx           ← PostHog provider
│   │   │   ├── analytics.ts          ← Typed event tracking
│   │   │   └── utils.ts              ← cn(), formatDate(), etc
│   │   ├── providers/                ← Context providers
│   │   │   ├── SessionProvider.tsx
│   │   │   └── ThemeProvider.tsx
│   │   └── api/                      ← API client utilities
│   │
│   ├── server/                       ← Server-only code
│   │   ├── actions/                  ← "use server" functions
│   │   └── utils.ts                  ← Server-side helpers
│   │
│   └── test/                         ← Test utilities
│       ├── setup.ts
│       └── utils.tsx
│
├── middleware.ts                     ← Edge middleware (JWT verification)
├── next.config.ts                    ← Next.js config (CSP, Turbopack)
└── package.json
```

---

## 2. COMPONENT PATTERNS

### Named exports only (Next.js convention)
```typescript
// ✅ CORRECT — named export
export function ChapterCard({ chapter }: ChapterCardProps) { ... }

// ❌ WRONG — default export
export default function ChapterCard() { ... }
```

### Props interface above component
```typescript
// ✅ CORRECT
interface ChapterCardProps {
  chapter: Chapter;
  onPress?: () => void;
  showProgress?: boolean;
  className?: string;
}

export function ChapterCard({ chapter, onPress, showProgress = true, className }: ChapterCardProps) {
  ...
}

// ❌ WRONG — inline types or any
export function ChapterCard({ chapter, onPress }: any) { ... }
```

### Server vs Client components
```typescript
// ✅ Client component — needs "use client" directive
"use client";

import { useState } from 'react';

export function ChapterCard({ chapter }: ChapterCardProps) {
  const [expanded, setExpanded] = useState(false);
  ...
}

// ✅ Server component — NO directive, can fetch data directly
import { getChapter } from '@/features/syllabus/api';

export async function ChapterDetail({ chapterId }: { chapterId: string }) {
  const chapter = await getChapter(chapterId);
  return <div>{chapter.name}</div>;
}

// ❌ WRONG — using hooks in server component
export async function ChapterDetail() {
  const [data, setData] = useState(null);  // Error!
}
```

### Every async component needs all 3 states
```typescript
// ✅ CORRECT — all 3 states handled (client component with React Query)
"use client";

function ChapterList({ subjectId }: { subjectId: string }) {
  const { data: chapters, isLoading, error } = useChapters(subjectId);

  if (isLoading) return <ChapterListSkeleton />;
  if (error) return <ErrorState message="Couldn't load chapters" onRetry={refetch} />;
  if (!chapters?.length) return <EmptyState title="No chapters found" />;

  return <div>{chapters.map(c => <ChapterCard key={c.id} chapter={c} />)}</div>;
}
```

### Optimistic updates pattern (React Query)
```typescript
// ✅ CORRECT — update UI immediately, sync in background
function useSubtopicCompletion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (subtopicId: string) => markSubtopicComplete(subtopicId),
    onMutate: async (subtopicId) => {
      await queryClient.cancelQueries({ queryKey: ['chapter', chapterId] });
      const previous = queryClient.getQueryData(['chapter', chapterId]);
      queryClient.setQueryData(['chapter', chapterId], (old: Chapter) => ({
        ...old,
        completedSubtopics: [...old.completedSubtopics, subtopicId],
      }));
      return { previous };
    },
    onError: (_err, _vars, context) => {
      queryClient.setQueryData(['chapter', chapterId], context?.previous);
      toast.error('Failed to save');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['chapter', chapterId] });
    },
  });
}
```

---

## 3. STATE MANAGEMENT RULES

### Zustand — global UI state only
```typescript
// ✅ Use Zustand for: UI preferences, active chapter, theme
// ❌ Don't use Zustand for: server data (use React Query), component-local state (useState)

// Store pattern (@/shared/stores/ui.store.ts)
import { create } from 'zustand';

interface UIStore {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  activeChapterId: string | null;
  setActiveChapter: (id: string) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: false,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  activeChapterId: null,
  setActiveChapter: (id) => set({ activeChapterId: id }),
}));
```

### React Query — all server state
```typescript
// ✅ Use TanStack Query for: all API data, all server state
// Query key convention: [entity, ...identifiers]
const { data: chapter } = useQuery({
  queryKey: ['chapter', chapterId],
  queryFn: () => fetchChapter(chapterId),
  staleTime: 1000 * 60 * 5, // 5 min
  gcTime: 1000 * 60 * 30,   // 30 min
});

// Prefetch on hover pattern
const queryClient = useQueryClient();
<ChapterCard
  onMouseEnter={() => queryClient.prefetchQuery({
    queryKey: ['chapter', chapter.id],
    queryFn: () => fetchChapter(chapter.id),
  })}
/>
```

### Server Actions — mutations from server components
```typescript
// ✅ Server action for form submissions
"use server";

import { revalidatePath } from 'next/cache';

export async function updateProfile(data: ProfileFormData) {
  const validated = profileSchema.parse(data);
  await api.put('/v1/profile', validated);
  revalidatePath('/settings');
  return { success: true };
}

// Usage in client component
"use client";

import { updateProfile } from '@/server/actions/profile';

export function ProfileForm() {
  const handleSubmit = async (data: ProfileFormData) => {
    const result = await updateProfile(data);
    if (result.success) toast.success('Profile updated');
  };
  ...
}
```

---

## 4. PERFORMANCE RULES

### Dynamic imports for heavy pages
```typescript
// ✅ Dynamic import for quiz page (heavy)
import dynamic from 'next/dynamic';

const QuizPage = dynamic(() => import('@/features/quiz/components/QuizPage'), {
  loading: () => <PageSkeleton />,
  ssr: false,
});

// ✅ Dynamic import for AI chat panel
const AIChatPanel = dynamic(() => import('@/features/ai/components/AIChatPanel'), {
  loading: () => <ChatSkeleton />,
});
```

### Memoization rules
```typescript
// ✅ useMemo: expensive computations (chapter completion %)
const completionPct = useMemo(() =>
  calcCompletionPct(subtopics, completedIds),
  [subtopics, completedIds]
);

// ✅ useCallback: stable callbacks passed to child components
const handleComplete = useCallback((subtopicId: string) => {
  markComplete(subtopicId);
}, [markComplete]);

// ✅ React.memo: components that re-render often with same props
export const SubtopicItem = React.memo(function SubtopicItem({ subtopic, isCompleted, onToggle }) {
  ...
});
```

---

## 5. MOBILE-FIRST RULES (MANDATORY)

```typescript
// ✅ ALL CSS written mobile-first
// Default = 375px phone, override upward

// Layout
<div className="
  px-4 py-6          // mobile padding
  sm:px-6            // tablet
  lg:px-8            // desktop
  flex flex-col      // mobile: stack vertically
  lg:flex-row        // desktop: horizontal
  gap-4 lg:gap-8
">

// Typography
<h1 className="text-2xl font-bold md:text-3xl lg:text-4xl">

// Grid
<div className="
  grid grid-cols-1   // mobile: 1 column
  sm:grid-cols-2     // tablet: 2 columns
  lg:grid-cols-3     // desktop: 3 columns
  gap-4
">

// ❌ NEVER desktop-first
<div className="flex-row lg:flex-col">  // WRONG — starts desktop, overrides mobile
```

### Touch targets (non-negotiable)
```typescript
// ✅ Every interactive element: minimum 44×44px tap target
// Even if visual is smaller, pad the wrapper

// Checkbox example — visual 18px, tap area 44px
<label className="flex items-center cursor-pointer min-h-[44px] gap-3 py-2">
  <div className="relative h-[18px] w-[18px] shrink-0">
    <input type="checkbox" className="sr-only" />
    <div className="h-full w-full rounded border-2 ...">
      {checked && <Check className="h-3 w-3" />}
    </div>
  </div>
  <span className="text-sm">{label}</span>
</label>
```

---

## 6. ROUTING PATTERNS (Next.js App Router)

```typescript
// Route groups for layout isolation
// (app)/ — authenticated pages, shares layout
// (auth)/ — login/signup, no sidebar
// (marketing)/ — landing page, public

// Protected route pattern (middleware.ts — Edge runtime)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('studyos_access');
  const isAuthRoute = request.nextUrl.pathname.startsWith('/login') ||
                      request.nextUrl.pathname.startsWith('/signup');

  if (!token && !isAuthRoute) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (token && isAuthRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next|static|favicon.ico).*)'],
};

// Navigation
import Link from 'next/link';

// ✅ Correct — Next.js Link
<Link href="/dashboard">Dashboard</Link>
<Link href={`/syllabus/${chapter.id}`}>{chapter.name}</Link>

// ❌ WRONG — React Router patterns
import { Link } from 'react-router-dom';  // Not used!
```

---

## 7. FORMS (RHF + Zod)

```typescript
// ✅ Use React Hook Form + Zod validation
"use client";

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema } from '@/shared/config/schemas';

export function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      toast.error('Invalid credentials');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Input label="Email" {...register('email')} error={errors.email?.message} />
      <Input label="Password" type="password" {...register('password')} error={errors.password?.message} />
      <Button type="submit" className="w-full">Sign In</Button>
    </form>
  );
}
```

---

## 8. ERROR BOUNDARIES

```typescript
// ✅ Global error boundary (app/error.tsx)
"use client";

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Send to Sentry
    Sentry.captureException(error);
  }, [error]);

  return (
    <div className="p-4 rounded-lg bg-danger/10 border border-danger/20">
      <p className="text-sm text-danger">Something went wrong.</p>
      <button onClick={reset} className="text-sm underline mt-2">
        Try again
      </button>
    </div>
  );
}
```

---

## 9. UTILITY FUNCTIONS (lib/utils.ts)

```typescript
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Merge Tailwind classes (always use this)
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Days until exam
export function daysUntilExam(examDate: string): number {
  const exam = new Date(examDate);
  const now = new Date();
  const diff = exam.getTime() - now.getTime();
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
}

// Completion percentage
export function calcCompletionPct(total: number, completed: number): number {
  if (total === 0) return 0;
  return Math.round((completed / total) * 100);
}

// Urgency level
export function getUrgencyLevel(daysRemaining: number): 'comfortable' | 'moderate' | 'urgent' | 'critical' {
  if (daysRemaining > 140) return 'comfortable';
  if (daysRemaining > 84) return 'moderate';
  if (daysRemaining > 42) return 'urgent';
  return 'critical';
}
```

---

## 10. DO / DON'T QUICK REFERENCE

```
✅ DO:
  Use named exports (not default)
  Add "use client" directive when using hooks/state
  Use server components by default (no directive)
  Handle loading + error + empty in every async component
  Lazy-load heavy components with next/dynamic
  Mobile-first Tailwind (default = mobile)
  44px minimum tap targets
  Optimistic UI updates with React Query
  Error boundaries on every major section
  useMemo for expensive calculations
  RHF + Zod for forms
  Route groups: (app), (auth), (marketing)
  BFF pattern: Next.js → FastAPI internal proxy

❌ DON'T:
  Use React Router (use Next.js App Router)
  Use default exports
  Use any type
  Fetch in useEffect without React Query
  Mutate Zustand state directly
  Put server state in Zustand (use React Query)
  Use desktop-first CSS
  Skip error boundaries
  Use inline styles (use Tailwind)
  Access localStorage directly
  Import from shadcn/ui internals
  Use dangerouslySetInnerHTML without DOMPurify
  Reference Vite, Dexie.js, or PWA patterns
```

---

*SKILL_FRONTEND.md — StudyOS | Next.js 16 App Router | May 2026*
