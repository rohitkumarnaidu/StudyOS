import Link from "next/link";
import { APP_NAME, healthPayload } from "@studyos/shared";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";

export default function MarketingHomePage() {
  const api = healthPayload("web");
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-6 py-16">
      <header className="space-y-2" id="content">
        <p className="text-sm font-medium text-primary">Foundation</p>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">{APP_NAME}</h1>
        <p className="text-base leading-relaxed text-muted-foreground">
          Enterprise monorepo scaffold: feature-based Next.js app, shared packages, and versioned
          FastAPI service. See{" "}
          <code className="rounded-md bg-muted px-1.5 py-0.5 text-sm text-foreground">
            ARCHITECTURE.md
          </code>{" "}
          for layout.
        </p>
        <div className="flex flex-wrap gap-3 pt-2">
          <Link
            href="/login"
            className="inline-flex rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow-sm transition-opacity hover:opacity-90"
          >
            Sign in
          </Link>
          <Link
            href="/signup"
            className="inline-flex rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium text-card-foreground shadow-sm transition-colors hover:bg-muted"
          >
            Sign up
          </Link>
          <Link
            href="/dashboard"
            className="inline-flex rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium text-card-foreground shadow-sm transition-colors hover:bg-muted"
          >
            Dashboard
          </Link>
        </div>
      </header>
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Shared package</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="overflow-x-auto rounded-lg bg-muted p-3 text-xs text-foreground">
            {JSON.stringify(api, null, 2)}
          </pre>
        </CardContent>
      </Card>
    </main>
  );
}
