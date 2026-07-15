"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef } from "react";
import { FormProvider, useForm } from "react-hook-form";

import { GoogleSignInButton } from "@/features/auth/components/google-sign-in-button";
import { loginFormSchema, type LoginFormValues } from "@/features/auth/schema";
import { useSession } from "@/features/auth/session-provider";
import { FormField } from "@/shared/components/form/form-field";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { notifyError, notifyFromUnknown, notifySuccess } from "@/shared/lib";
import { safeNextPath } from "@/shared/lib/safe-next-path";
import { isSupabaseBrowserConfigured } from "@/shared/lib/supabase/browser-client";

function LoginFormFallback() {
  return (
    <div className="space-y-4" aria-busy="true" aria-label="Loading sign-in form">
      <div className="space-y-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-10 w-full" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-10 w-full" />
      </div>
      <Skeleton className="h-10 w-full" />
    </div>
  );
}

function LoginFormInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refresh } = useSession();
  const nextPath = safeNextPath(searchParams.get("next"));

  const oauthToastShown = useRef(false);

  useEffect(() => {
    if (oauthToastShown.current) return;
    const err = searchParams.get("error");
    if (err !== "oauth") return;
    oauthToastShown.current = true;
    const msg = searchParams.get("message");
    notifyError(msg ? decodeURIComponent(msg) : "Google sign-in failed. Try again.");
  }, [searchParams]);

  const isDev = process.env.NEXT_PUBLIC_APP_ENV === "development";

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: isDev
      ? { email: "demo@studyos.app", password: "demo" }
      : { email: "", password: "" },
  });

  async function onSubmit(values: LoginFormValues) {
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      if (!res.ok) {
        const err = (await res.json().catch(() => null)) as { error?: string } | null;
        notifyError(err?.error ?? "Login failed");
        return;
      }
      notifySuccess("Signed in");
      await refresh();
      router.push(nextPath);
      router.refresh();
    } catch (e) {
      notifyFromUnknown(e, "Network error");
    }
  }

  const showGoogle = isSupabaseBrowserConfigured();

  return (
    <FormProvider {...form}>
      <div className="space-y-4">
        {showGoogle ? (
          <>
            <GoogleSignInButton nextPath={nextPath} />
            <div className="relative">
              <div className="absolute inset-0 flex items-center" aria-hidden>
                <span className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">or email</span>
              </div>
            </div>
          </>
        ) : null}
        <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)} noValidate>
          <FormField<LoginFormValues> name="email" label="Email" hint="Demo: demo@studyos.app">
            <Input id="email" type="email" autoComplete="email" {...form.register("email")} />
          </FormField>
          <FormField<LoginFormValues> name="password" label="Password" hint="Demo password: demo">
            <Input id="password" type="password" autoComplete="current-password" {...form.register("password")} />
          </FormField>
          <Button type="submit" className="w-full" disabled={form.formState.isSubmitting}>
            {form.formState.isSubmitting ? "Signing in…" : "Continue"}
          </Button>
        </form>
      </div>
    </FormProvider>
  );
}

export function LoginForm() {
  return (
    <Suspense fallback={<LoginFormFallback />}>
      <LoginFormInner />
    </Suspense>
  );
}
